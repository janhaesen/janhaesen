from __future__ import annotations

from typing import Protocol

from ..build import BuildResult
from ..capabilities import RegistryAccess, RuntimeCapabilities
from ..config import BuildRequest, RegistryConfig


class RuntimeAdapter(Protocol):
  name: str

  def is_available(self) -> bool:
    ...

  def is_active(self) -> bool:
    ...

  def ensure_started(self, *, auto_start: bool = False) -> None:
    ...

  def detect_capabilities(self) -> RuntimeCapabilities:
    ...

  def resolve_registry_access(self, registry: RegistryConfig) -> RegistryAccess:
    ...

  def configure_registry_access(
    self,
    registry: RegistryConfig,
    access: RegistryAccess,
    *,
    auto_restart: bool = False,
  ) -> None:
    ...

  def build(self, request: BuildRequest, *, destination: str | None = None) -> BuildResult:
    ...

  def push(self, image_reference: str) -> None:
    ...

