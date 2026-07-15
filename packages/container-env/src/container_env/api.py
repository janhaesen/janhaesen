from __future__ import annotations

from dataclasses import replace

from .build import BuildResult
from .capabilities import EnvironmentCheck, EnvironmentReport, RegistryAccess
from .commands import CommandRunner, SubprocessRunner
from .config import BuildRequest, EnvironmentConfig
from .deploy import DeploymentReference, deployment_references
from .detection import RuntimeDetector
from .errors import RuntimeNotFoundError
from .registry import RegistryService, RegistryStatus
from .runtimes.base import RuntimeAdapter
from .runtimes.colima import ColimaRuntime
from .runtimes.docker import DockerRuntime


class ContainerEnvironment:
  def __init__(
    self,
    config: EnvironmentConfig | None = None,
    *,
    runner: CommandRunner | None = None,
  ) -> None:
    self.config = config or EnvironmentConfig()
    self.runner = runner or SubprocessRunner()
    self.detector = RuntimeDetector(self.runner)
    self.registry_service = RegistryService(self.runner)

  def check_environment(self) -> EnvironmentReport:
    adapters = self._adapters()
    checks: list[EnvironmentCheck] = []
    for runtime_name in self.config.preferred_runtimes:
      adapter = adapters[runtime_name]
      available = adapter.is_available()
      active = adapter.is_active()
      checks.append(
        EnvironmentCheck(
          name=f"{runtime_name}-installed",
          ok=available,
          detail=f"{runtime_name} is {'available' if available else 'missing'} on PATH.",
          remediation=None if available else f"Install {runtime_name} before using this template.",
        )
      )
      checks.append(
        EnvironmentCheck(
          name=f"{runtime_name}-active",
          ok=active,
          detail=f"{runtime_name} is {'running' if active else 'not running'}.",
          remediation=None if active else f"Start {runtime_name} or let the facade choose another runtime.",
        )
      )

    selected_runtime: str | None = None
    capabilities = None
    registry_access: RegistryAccess | None = None
    try:
      adapter = self._select_runtime()
      selected_runtime = adapter.name
      capabilities = adapter.detect_capabilities()
      registry_access = adapter.resolve_registry_access(self.config.registry)
    except RuntimeNotFoundError:
      selected_runtime = None

    return EnvironmentReport(
      selected_runtime=selected_runtime,
      capabilities=capabilities,
      checks=tuple(checks),
      registry_access=registry_access,
    )

  def doctor(self) -> EnvironmentReport:
    return self.check_environment()

  def ensure_environment(self) -> RuntimeAdapter:
    adapter = self._select_runtime()
    adapter.ensure_started(auto_start=self._should_auto_start(adapter))
    return adapter

  def ensure_registry_running(self) -> RegistryStatus:
    self.ensure_environment()
    return self.registry_service.ensure_running(self.config.registry)

  def ensure_registry_access(self) -> RegistryAccess:
    adapter = self.ensure_environment()
    self.ensure_registry_running()
    access = adapter.resolve_registry_access(self.config.registry)
    adapter.configure_registry_access(
      self.config.registry,
      access,
      auto_restart=self.config.auto_restart_colima,
    )
    return access

  def build(self, request: BuildRequest) -> BuildResult:
    adapter = self.ensure_environment()
    destination: str | None = None
    if request.push:
      access = self.ensure_registry_access()
      destination = f"{access.push_endpoint}/{request.local_reference}"

    result = adapter.build(request, destination=destination)
    if destination and request.push and not result.pushed:
      adapter.push(destination)
      result = replace(result, published_reference=destination, pushed=True)
    return result

  def deployment_references(self, build_result: BuildResult) -> tuple[DeploymentReference, ...]:
    adapter = self._select_runtime()
    access = adapter.resolve_registry_access(self.config.registry)
    return deployment_references(build_result, access)

  def _select_runtime(self) -> RuntimeAdapter:
    adapters = self._adapters()
    selection = self.detector.select_runtime(adapters, self.config.preferred_runtimes)
    return adapters[selection.runtime_name]

  def _adapters(self) -> dict[str, RuntimeAdapter]:
    return {
      "docker": DockerRuntime(self.runner),
      "colima": ColimaRuntime(self.runner),
    }

  def _should_auto_start(self, adapter: RuntimeAdapter) -> bool:
    return adapter.name == "colima" and self.config.auto_start_colima
