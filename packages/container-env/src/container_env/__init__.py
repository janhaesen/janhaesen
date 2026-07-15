from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .api import ContainerEnvironment
from .build import BuildResult
from .capabilities import EnvironmentReport, RegistryAccess, RuntimeCapabilities
from .cli import main
from .config import BuildRequest, EnvironmentConfig, RegistryConfig
from .deploy import DeploymentReference

try:
  __version__ = version("container-env")
except PackageNotFoundError:
  __version__ = "0.0.0"

__all__ = [
  "BuildRequest",
  "BuildResult",
  "ContainerEnvironment",
  "DeploymentReference",
  "EnvironmentConfig",
  "EnvironmentReport",
  "RegistryAccess",
  "RegistryConfig",
  "RuntimeCapabilities",
  "main",
]
