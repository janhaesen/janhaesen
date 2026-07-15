from __future__ import annotations

from pathlib import Path

from ..build import BuildResult
from ..capabilities import RegistryAccess, RuntimeCapabilities
from ..commands import CommandRunner, command_exists
from ..config import BuildRequest, RegistryConfig
from ..errors import BuildError, RegistryConfigError, RegistryError, RuntimeNotFoundError, RuntimeNotStartedError


class DockerRuntime:
  name = "docker"

  def __init__(self, runner: CommandRunner) -> None:
    self.runner = runner

  def is_available(self) -> bool:
    return command_exists("docker")

  def is_active(self) -> bool:
    if not self.is_available():
      return False
    result = self.runner.run(["docker", "info", "--format", "{{.ServerVersion}}"])
    return result.returncode == 0

  def ensure_started(self, *, auto_start: bool = False) -> None:
    if not self.is_available():
      raise RuntimeNotFoundError(self.name)
    if not self.is_active():
      raise RuntimeNotStartedError(
        self.name,
        remediation="Start Docker Desktop or another Docker daemon before building images.",
      )

  def detect_capabilities(self) -> RuntimeCapabilities:
    buildx_result = self.runner.run(["docker", "buildx", "version"])
    supports_buildx = buildx_result.returncode == 0
    return RuntimeCapabilities(
      name=self.name,
      available=self.is_available(),
      active=self.is_active(),
      supports_multi_platform=supports_buildx,
      supports_buildx=supports_buildx,
      supports_local_registry=True,
      supports_kubernetes=False,
      guest_pull_host="127.0.0.1",
      notes=(),
    )

  def resolve_registry_access(self, registry: RegistryConfig) -> RegistryAccess:
    if registry.mode == "tls" and registry.tls is None:
      raise RegistryConfigError("TLS registry mode requires TLS material in RegistryConfig.tls.")

    endpoint = registry.host_endpoint
    return RegistryAccess(
      mode=registry.mode,
      push_endpoint=endpoint,
      pull_endpoint=endpoint,
      kubernetes_endpoint=endpoint,
      requires_runtime_configuration=False,
      notes=(),
    )

  def configure_registry_access(
    self,
    registry: RegistryConfig,
    access: RegistryAccess,
    *,
    auto_restart: bool = False,
  ) -> None:
    if registry.mode == "tls":
      raise RegistryConfigError("TLS registry mode is not automated for the Docker adapter yet.")

  def build(self, request: BuildRequest, *, destination: str | None = None) -> BuildResult:
    self.ensure_started()
    image_reference = destination or request.local_reference
    platforms = tuple(request.platforms)
    used_buildx = len(platforms) > 1

    if used_buildx:
      buildx_check = self.runner.run(["docker", "buildx", "version"])
      if buildx_check.returncode != 0:
        raise BuildError(request.local_reference, buildx_check.returncode, buildx_check.stderr or "docker buildx is unavailable")

      command = ["docker", "buildx", "build", "--platform", ",".join(platforms), "--tag", image_reference]
      if destination and request.push:
        command.append("--push")
      else:
        command.append("--load")
      command.extend(self._build_arguments(request))
      command.append(str(request.context))

      result = self.runner.run(command)
      if result.returncode != 0:
        raise BuildError(image_reference, result.returncode, result.stderr)

      return BuildResult(
        source_reference=image_reference,
        published_reference=image_reference if destination and request.push else None,
        platforms=platforms,
        used_buildx=True,
        pushed=bool(destination and request.push),
      )

    command = ["docker", "build", "--tag", image_reference]
    command.extend(self._build_arguments(request))
    command.append(str(request.context))
    result = self.runner.run(command)
    if result.returncode != 0:
      raise BuildError(image_reference, result.returncode, result.stderr)

    pushed = False
    if destination and request.push:
      self.push(image_reference)
      pushed = True

    return BuildResult(
      source_reference=image_reference,
      published_reference=image_reference if pushed else None,
      platforms=platforms,
      used_buildx=False,
      pushed=pushed,
    )

  def push(self, image_reference: str) -> None:
    result = self.runner.run(["docker", "push", image_reference])
    if result.returncode != 0:
      raise RegistryError(f"Failed to push image '{image_reference}': {result.stderr.strip()}")

  def _build_arguments(self, request: BuildRequest) -> list[str]:
    arguments: list[str] = []
    if request.dockerfile:
      arguments.extend(["--file", str(request.dockerfile)])
    for key, value in sorted(request.build_args.items()):
      arguments.extend(["--build-arg", f"{key}={value}"])
    return arguments

