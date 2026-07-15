from __future__ import annotations


class ContainerEnvError(RuntimeError):
  """Base class for container environment failures."""


class RuntimeNotFoundError(ContainerEnvError):
  def __init__(self, runtime: str) -> None:
    super().__init__(f"Runtime '{runtime}' is not installed or not available on PATH.")
    self.runtime = runtime


class RuntimeNotStartedError(ContainerEnvError):
  def __init__(self, runtime: str, remediation: str | None = None) -> None:
    detail = f"Runtime '{runtime}' is not running."
    if remediation:
      detail = f"{detail} {remediation}"
    super().__init__(detail)
    self.runtime = runtime
    self.remediation = remediation


class BuildError(ContainerEnvError):
  def __init__(self, image: str, exit_code: int, stderr: str) -> None:
    super().__init__(f"Build failed for '{image}' with exit code {exit_code}: {stderr.strip()}")
    self.image = image
    self.exit_code = exit_code
    self.stderr = stderr


class RegistryError(ContainerEnvError):
  pass


class RegistryConfigError(RegistryError):
  pass


class DeploymentError(ContainerEnvError):
  pass

