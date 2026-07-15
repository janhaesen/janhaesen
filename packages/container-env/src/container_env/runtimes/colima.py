from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os

from ..capabilities import RegistryAccess, RuntimeCapabilities
from ..commands import CommandRunner, command_exists
from ..config import RegistryConfig
from ..deploy import render_k3s_registries_yaml
from ..errors import RegistryConfigError, RegistryError, RuntimeNotFoundError, RuntimeNotStartedError
from .docker import DockerRuntime


@dataclass(frozen=True)
class ColimaStatus:
  runtime: str
  kubernetes: bool
  ip_address: str | None


class ColimaRuntime(DockerRuntime):
  name = "colima"

  def is_available(self) -> bool:
    return command_exists("docker") and command_exists("colima")

  def is_active(self) -> bool:
    if not self.is_available():
      return False
    result = self.runner.run(["colima", "status", "--json"])
    return result.returncode == 0

  def ensure_started(self, *, auto_start: bool = False) -> None:
    if not self.is_available():
      raise RuntimeNotFoundError(self.name)
    if self.is_active():
      return
    if not auto_start:
      raise RuntimeNotStartedError(self.name, remediation="Run 'colima start' or enable auto_start_colima.")

    result = self.runner.run(["colima", "start"])
    if result.returncode != 0:
      raise RuntimeNotStartedError(self.name, remediation=result.stderr.strip() or "Failed to start Colima.")

  def detect_capabilities(self) -> RuntimeCapabilities:
    status = self.status()
    buildx_result = self.runner.run(["docker", "buildx", "version"])
    supports_buildx = buildx_result.returncode == 0
    notes = ()
    if status is not None:
      notes = ("Use host.lima.internal for in-VM registry pulls when the host publishes localhost ports.",)
    return RuntimeCapabilities(
      name=self.name,
      available=self.is_available(),
      active=self.is_active(),
      supports_multi_platform=supports_buildx,
      supports_buildx=supports_buildx,
      supports_local_registry=True,
      supports_kubernetes=bool(status and status.kubernetes),
      guest_pull_host="host.lima.internal",
      notes=notes,
    )

  def resolve_registry_access(self, registry: RegistryConfig) -> RegistryAccess:
    host_endpoint = registry.host_endpoint
    guest_endpoint = registry.guest_endpoint("host.lima.internal")
    notes = (
      "Host pushes use the published localhost endpoint; guest-side pulls should use host.lima.internal.",
    )
    return RegistryAccess(
      mode=registry.mode,
      push_endpoint=host_endpoint,
      pull_endpoint=guest_endpoint,
      kubernetes_endpoint=guest_endpoint,
      requires_runtime_configuration=registry.mode == "insecure",
      notes=notes,
    )

  def configure_registry_access(
    self,
    registry: RegistryConfig,
    access: RegistryAccess,
    *,
    auto_restart: bool = False,
  ) -> None:
    if registry.mode == "tls":
      raise RegistryConfigError("TLS registry mode is not automated for Colima yet.")

    changed = self._ensure_insecure_registry(access.pull_endpoint)
    if changed and self.is_active():
      if not auto_restart:
        raise RegistryConfigError(
          "Colima registry configuration changed and requires a restart. Enable auto_restart_colima or restart Colima manually."
        )
      self._restart_colima()

    status = self.status()
    if status and status.kubernetes:
      self._configure_k3s_registry(access)

  def status(self) -> ColimaStatus | None:
    result = self.runner.run(["colima", "status", "--json"])
    if result.returncode != 0:
      return None

    payload = json.loads(result.stdout)
    return ColimaStatus(
      runtime=payload.get("runtime", "docker"),
      kubernetes=bool(payload.get("kubernetes", False)),
      ip_address=payload.get("ip_address"),
    )

  def _restart_colima(self) -> None:
    stop_result = self.runner.run(["colima", "stop"])
    if stop_result.returncode != 0:
      raise RegistryConfigError(f"Failed to stop Colima for registry reconfiguration: {stop_result.stderr.strip()}")
    start_result = self.runner.run(["colima", "start"])
    if start_result.returncode != 0:
      raise RegistryConfigError(f"Failed to start Colima after registry reconfiguration: {start_result.stderr.strip()}")

  def _ensure_insecure_registry(self, endpoint: str) -> bool:
    config_path = self._config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    original = config_path.read_text() if config_path.exists() else "docker: {}\n"
    updated = self._upsert_insecure_registry(original, endpoint)
    if updated == original:
      return False
    config_path.write_text(updated)
    return True

  def _config_path(self) -> Path:
    colima_home = os.environ.get("COLIMA_HOME")
    if colima_home:
      base = Path(colima_home)
    else:
      base = Path.home() / ".colima"
    profile = os.environ.get("COLIMA_PROFILE", "default")
    return base / profile / "colima.yaml"

  def _upsert_insecure_registry(self, contents: str, endpoint: str) -> str:
    if endpoint in contents:
      return contents
    if "docker: {}" in contents:
      return contents.replace("docker: {}", f"docker:\n  insecure-registries:\n    - {endpoint}")

    lines = contents.splitlines()
    docker_index = next((index for index, line in enumerate(lines) if line.strip() == "docker:"), None)
    if docker_index is None:
      lines.extend(["docker:", "  insecure-registries:", f"    - {endpoint}"])
      return "\n".join(lines) + "\n"

    section_end = len(lines)
    for index in range(docker_index + 1, len(lines)):
      line = lines[index]
      if line and not line.startswith(" "):
        section_end = index
        break

    insecure_index = next(
      (index for index in range(docker_index + 1, section_end) if lines[index].strip() == "insecure-registries:"),
      None,
    )
    if insecure_index is None:
      lines[docker_index + 1:docker_index + 1] = ["  insecure-registries:", f"    - {endpoint}"]
      return "\n".join(lines) + "\n"

    insert_at = insecure_index + 1
    while insert_at < section_end and lines[insert_at].startswith("    - "):
      insert_at += 1
    lines.insert(insert_at, f"    - {endpoint}")
    return "\n".join(lines) + "\n"

  def _configure_k3s_registry(self, access: RegistryAccess) -> None:
    mkdir_result = self.runner.run(["colima", "ssh", "--", "sudo", "mkdir", "-p", "/etc/rancher/k3s"])
    if mkdir_result.returncode != 0:
      raise RegistryError(f"Failed to create k3s registry directory in Colima: {mkdir_result.stderr.strip()}")

    tee_result = self.runner.run(
      ["colima", "ssh", "--", "sudo", "tee", "/etc/rancher/k3s/registries.yaml"],
      input_text=render_k3s_registries_yaml(access),
    )
    if tee_result.returncode != 0:
      raise RegistryError(f"Failed to write k3s registries.yaml in Colima: {tee_result.stderr.strip()}")

    restart_result = self.runner.run(["colima", "ssh", "--", "sudo", "systemctl", "restart", "k3s"])
    if restart_result.returncode != 0:
      service_result = self.runner.run(["colima", "ssh", "--", "sudo", "service", "k3s", "restart"])
      if service_result.returncode != 0:
        raise RegistryError(
          "Failed to restart k3s after updating registries.yaml: "
          f"{restart_result.stderr.strip() or service_result.stderr.strip()}"
        )

