from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from container_env.config import BuildRequest
from container_env.runtimes.docker import DockerRuntime

from tests.unit.support import FakeRunner, ok


class DockerRuntimeTests(unittest.TestCase):
  @patch("container_env.runtimes.docker.command_exists", return_value=True)
  def test_single_platform_build_pushes_to_destination(self, _command_exists) -> None:
    responses = dict(
      [
        ok("docker", "info", "--format", "{{.ServerVersion}}", stdout="27.0.0"),
        ok("docker", "build", "--tag", "127.0.0.1:5000/app:latest", ".", stdout="built"),
        ok("docker", "push", "127.0.0.1:5000/app:latest", stdout="pushed"),
      ]
    )
    runtime = DockerRuntime(FakeRunner(responses))

    result = runtime.build(
      BuildRequest(context=Path("."), image="app"),
      destination="127.0.0.1:5000/app:latest",
    )

    self.assertTrue(result.pushed)
    self.assertEqual(result.published_reference, "127.0.0.1:5000/app:latest")

  @patch("container_env.runtimes.docker.command_exists", return_value=True)
  def test_multi_platform_build_uses_buildx_push(self, _command_exists) -> None:
    responses = dict(
      [
        ok("docker", "info", "--format", "{{.ServerVersion}}", stdout="27.0.0"),
        ok("docker", "buildx", "version", stdout="buildx v0.12.0"),
        ok(
          "docker",
          "buildx",
          "build",
          "--platform",
          "linux/amd64,linux/arm64",
          "--tag",
          "127.0.0.1:5000/app:latest",
          "--push",
          ".",
          stdout="built",
        ),
      ]
    )
    runtime = DockerRuntime(FakeRunner(responses))

    result = runtime.build(
      BuildRequest(context=Path("."), image="app", platforms=("linux/amd64", "linux/arm64")),
      destination="127.0.0.1:5000/app:latest",
    )

    self.assertTrue(result.used_buildx)
    self.assertTrue(result.pushed)


if __name__ == "__main__":
  unittest.main()

