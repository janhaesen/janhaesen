from __future__ import annotations

from dataclasses import dataclass, field

from .config import RegistryMode


@dataclass(frozen=True)
class RuntimeCapabilities:
  name: str
  available: bool
  active: bool
  supports_multi_platform: bool
  supports_buildx: bool
  supports_local_registry: bool
  supports_kubernetes: bool
  guest_pull_host: str | None = None
  notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RegistryAccess:
  mode: RegistryMode
  push_endpoint: str
  pull_endpoint: str
  kubernetes_endpoint: str
  requires_runtime_configuration: bool
  notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class EnvironmentCheck:
  name: str
  ok: bool
  detail: str
  remediation: str | None = None


@dataclass(frozen=True)
class EnvironmentReport:
  selected_runtime: str | None
  capabilities: RuntimeCapabilities | None
  checks: tuple[EnvironmentCheck, ...] = field(default_factory=tuple)
  registry_access: RegistryAccess | None = None

  @property
  def ok(self) -> bool:
    return all(check.ok for check in self.checks)

