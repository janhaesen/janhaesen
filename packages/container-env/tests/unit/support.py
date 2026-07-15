from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Mapping

from container_env.commands import CommandResult


class FakeRunner:
  def __init__(self, responses: dict[tuple[str, ...], CommandResult]) -> None:
    self.responses = responses
    self.calls: list[tuple[tuple[str, ...], str | None]] = []

  def run(
    self,
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    input_text: str | None = None,
  ) -> CommandResult:
    key = tuple(args)
    self.calls.append((key, input_text))
    if key not in self.responses:
      raise AssertionError(f"Unexpected command: {key}")
    return self.responses[key]


def ok(*args: str, stdout: str = "") -> tuple[tuple[str, ...], CommandResult]:
  key = tuple(args)
  return key, CommandResult(args=key, returncode=0, stdout=stdout, stderr="")


def fail(*args: str, stderr: str) -> tuple[tuple[str, ...], CommandResult]:
  key = tuple(args)
  return key, CommandResult(args=key, returncode=1, stdout="", stderr=stderr)

