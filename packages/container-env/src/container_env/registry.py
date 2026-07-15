from __future__ import annotations

from dataclasses import dataclass

from .commands import CommandRunner
from .config import RegistryConfig
from .errors import RegistryConfigError, RegistryError


@dataclass(frozen=True)
class RegistryStatus:
  name: str
  endpoint: str
  running: bool


class RegistryService:
  def __init__(self, runner: CommandRunner) -> None:
    self.runner = runner

  def ensure_running(self, config: RegistryConfig) -> RegistryStatus:
    if config.mode == "tls":
      raise RegistryConfigError(
        "TLS registry mode is reserved in the API but the first implementation only automates insecure local development registries."
      )

    inspect_result = self.runner.run(
      ["docker", "inspect", "--format", "{{.State.Running}}", config.name]
    )
    if inspect_result.returncode == 0:
      is_running = inspect_result.stdout.strip() == "true"
      if not is_running:
        start_result = self.runner.run(["docker", "start", config.name])
        if start_result.returncode != 0:
          raise RegistryError(f"Failed to start registry container '{config.name}': {start_result.stderr.strip()}")
      return RegistryStatus(name=config.name, endpoint=config.host_endpoint, running=True)

    run_result = self.runner.run(
      [
        "docker",
        "run",
        "--detach",
        "--restart",
        "always",
        "--publish",
        f"{config.host}:{config.port}:5000",
        "--name",
        config.name,
        "registry:2",
      ]
    )
    if run_result.returncode != 0:
      raise RegistryError(f"Failed to create registry container '{config.name}': {run_result.stderr.strip()}")

    return RegistryStatus(name=config.name, endpoint=config.host_endpoint, running=True)

