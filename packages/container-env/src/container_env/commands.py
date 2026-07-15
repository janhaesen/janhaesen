from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import subprocess
from typing import Mapping, Protocol, Sequence


@dataclass(frozen=True)
class CommandResult:
  args: tuple[str, ...]
  returncode: int
  stdout: str
  stderr: str


class CommandRunner(Protocol):
  def run(
    self,
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    input_text: str | None = None,
  ) -> CommandResult:
    ...


class SubprocessRunner:
  def __init__(self, *, timeout_seconds: int = 120) -> None:
    self.timeout_seconds = timeout_seconds

  def run(
    self,
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    input_text: str | None = None,
  ) -> CommandResult:
    merged_env = os.environ.copy()
    if env:
      merged_env.update(env)

    completed = subprocess.run(
      list(args),
      cwd=str(cwd) if cwd else None,
      env=merged_env,
      input=input_text,
      text=True,
      capture_output=True,
      timeout=self.timeout_seconds,
      check=False,
    )
    return CommandResult(
      args=tuple(str(part) for part in args),
      returncode=completed.returncode,
      stdout=completed.stdout,
      stderr=completed.stderr,
    )


def command_exists(command: str) -> bool:
  return shutil.which(command) is not None

