from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BuildResult:
  source_reference: str
  published_reference: str | None
  platforms: tuple[str, ...]
  used_buildx: bool
  pushed: bool

