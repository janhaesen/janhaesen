from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Mapping

RegistryMode = Literal["insecure", "tls"]
DeployTarget = Literal["compose", "kubernetes"]


@dataclass(frozen=True)
class RegistryTLSConfig:
  ca_file: Path | None = None
  cert_file: Path | None = None
  key_file: Path | None = None


@dataclass(frozen=True)
class RegistryConfig:
  name: str = "container-env-registry"
  host: str = "127.0.0.1"
  port: int = 5000
  mode: RegistryMode = "insecure"
  guest_host: str | None = None
  tls: RegistryTLSConfig | None = None

  @property
  def host_endpoint(self) -> str:
    return f"{self.host}:{self.port}"

  def guest_endpoint(self, fallback_host: str | None = None) -> str:
    guest_host = self.guest_host or fallback_host or self.host
    return f"{guest_host}:{self.port}"


@dataclass(frozen=True)
class BuildRequest:
  context: Path
  image: str
  tag: str = "latest"
  platforms: tuple[str, ...] = ()
  dockerfile: Path | None = None
  build_args: Mapping[str, str] = field(default_factory=dict)
  push: bool = True

  def __post_init__(self) -> None:
    object.__setattr__(self, "context", Path(self.context))
    if self.dockerfile is not None:
      object.__setattr__(self, "dockerfile", Path(self.dockerfile))

  @property
  def local_reference(self) -> str:
    return f"{self.image}:{self.tag}"


@dataclass(frozen=True)
class EnvironmentConfig:
  preferred_runtimes: tuple[str, ...] = ("docker", "colima")
  auto_start_colima: bool = True
  auto_restart_colima: bool = True
  registry: RegistryConfig = field(default_factory=RegistryConfig)

