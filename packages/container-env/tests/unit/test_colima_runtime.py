from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from container_env.capabilities import RegistryAccess
from container_env.config import RegistryConfig
from container_env.runtimes.colima import ColimaRuntime

from tests.unit.support import FakeRunner, fail


class ColimaRuntimeTests(unittest.TestCase):
  @patch("container_env.runtimes.colima.command_exists", return_value=True)
  def test_insecure_registry_is_written_to_colima_yaml(self, _command_exists) -> None:
    responses = dict(
      [
        fail("colima", "status", "--json", stderr="not running"),
      ]
    )
    runtime = ColimaRuntime(FakeRunner(responses))

    with TemporaryDirectory() as tempdir:
      profile_dir = Path(tempdir) / "default"
      profile_dir.mkdir(parents=True)
      config_path = profile_dir / "colima.yaml"
      config_path.write_text("docker: {}\n")

      previous_home = os.environ.get("COLIMA_HOME")
      previous_profile = os.environ.get("COLIMA_PROFILE")
      os.environ["COLIMA_HOME"] = tempdir
      os.environ["COLIMA_PROFILE"] = "default"
      try:
        runtime.configure_registry_access(
          RegistryConfig(),
          RegistryAccess(
            mode="insecure",
            push_endpoint="127.0.0.1:5000",
            pull_endpoint="host.lima.internal:5000",
            kubernetes_endpoint="host.lima.internal:5000",
            requires_runtime_configuration=True,
          ),
        )
      finally:
        if previous_home is None:
          os.environ.pop("COLIMA_HOME", None)
        else:
          os.environ["COLIMA_HOME"] = previous_home
        if previous_profile is None:
          os.environ.pop("COLIMA_PROFILE", None)
        else:
          os.environ["COLIMA_PROFILE"] = previous_profile

      updated = config_path.read_text()
      self.assertIn("insecure-registries:", updated)
      self.assertIn("host.lima.internal:5000", updated)


if __name__ == "__main__":
  unittest.main()

