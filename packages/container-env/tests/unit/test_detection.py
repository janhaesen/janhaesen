from __future__ import annotations

import unittest
from unittest.mock import patch

from container_env.api import ContainerEnvironment
from container_env.commands import CommandResult
from container_env.config import EnvironmentConfig

from tests.unit.support import FakeRunner


class DetectionTests(unittest.TestCase):
  @patch("container_env.runtimes.colima.command_exists", return_value=True)
  @patch("container_env.runtimes.docker.command_exists", return_value=True)
  def test_colima_context_is_preferred_when_active(self, _docker_exists, _colima_exists) -> None:
    responses = {
      ("docker", "context", "show"): CommandResult(
        args=("docker", "context", "show"),
        returncode=0,
        stdout="colima\n",
        stderr="",
      ),
      ("colima", "status", "--json"): CommandResult(
        args=("colima", "status", "--json"),
        returncode=0,
        stdout='{"runtime":"docker","kubernetes":true,"ip_address":"192.168.5.2"}',
        stderr="",
      ),
      ("docker", "buildx", "version"): CommandResult(
        args=("docker", "buildx", "version"),
        returncode=0,
        stdout="buildx v0.12.0",
        stderr="",
      ),
      ("docker", "info", "--format", "{{.ServerVersion}}"): CommandResult(
        args=("docker", "info", "--format", "{{.ServerVersion}}"),
        returncode=0,
        stdout="27.0.0",
        stderr="",
      ),
    }
    environment = ContainerEnvironment(
      EnvironmentConfig(preferred_runtimes=("docker", "colima")),
      runner=FakeRunner(responses),
    )

    report = environment.check_environment()

    self.assertEqual(report.selected_runtime, "colima")
    self.assertIsNotNone(report.registry_access)
    self.assertEqual(report.registry_access.pull_endpoint, "host.lima.internal:5000")


if __name__ == "__main__":
  unittest.main()

