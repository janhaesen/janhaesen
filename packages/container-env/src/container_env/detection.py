from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .commands import CommandRunner
from .errors import RuntimeNotFoundError
from .runtimes.base import RuntimeAdapter


@dataclass(frozen=True)
class RuntimeSelection:
  runtime_name: str
  reason: str


class RuntimeDetector:
  def __init__(self, runner: CommandRunner) -> None:
    self.runner = runner

  def active_docker_context(self) -> str | None:
    result = self.runner.run(["docker", "context", "show"])
    if result.returncode != 0:
      return None
    context_name = result.stdout.strip()
    return context_name or None

  def select_runtime(
    self,
    adapters: Mapping[str, RuntimeAdapter],
    preferred_runtimes: Iterable[str],
  ) -> RuntimeSelection:
    active_context = self.active_docker_context()
    if active_context == "colima" and "colima" in adapters and adapters["colima"].is_available():
      return RuntimeSelection(runtime_name="colima", reason="Detected active Docker context 'colima'.")

    for runtime_name in preferred_runtimes:
      adapter = adapters.get(runtime_name)
      if adapter and adapter.is_available() and adapter.is_active():
        return RuntimeSelection(runtime_name=runtime_name, reason=f"Selected active runtime '{runtime_name}'.")

    for runtime_name in preferred_runtimes:
      adapter = adapters.get(runtime_name)
      if adapter and adapter.is_available():
        return RuntimeSelection(runtime_name=runtime_name, reason=f"Selected available runtime '{runtime_name}'.")

    preferred = next(iter(preferred_runtimes), "docker")
    raise RuntimeNotFoundError(preferred)

