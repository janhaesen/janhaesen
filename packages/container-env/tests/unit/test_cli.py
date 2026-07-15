from __future__ import annotations

from io import StringIO
import unittest

from container_env.build import BuildResult
from container_env.capabilities import EnvironmentCheck, EnvironmentReport, RegistryAccess, RuntimeCapabilities
from container_env.cli import main
from container_env.deploy import DeploymentReference


class StubEnvironment:
  def __init__(self) -> None:
    self.last_request = None

  def doctor(self) -> EnvironmentReport:
    return EnvironmentReport(
      selected_runtime="docker",
      capabilities=RuntimeCapabilities(
        name="docker",
        available=True,
        active=True,
        supports_multi_platform=True,
        supports_buildx=True,
        supports_local_registry=True,
        supports_kubernetes=False,
      ),
      checks=(
        EnvironmentCheck(name="docker-installed", ok=True, detail="docker is available on PATH."),
        EnvironmentCheck(name="docker-active", ok=True, detail="docker is running."),
        EnvironmentCheck(name="colima-installed", ok=False, detail="colima is missing on PATH.", remediation="Install colima if you need it."),
      ),
      registry_access=RegistryAccess(
        mode="insecure",
        push_endpoint="127.0.0.1:5000",
        pull_endpoint="127.0.0.1:5000",
        kubernetes_endpoint="127.0.0.1:5000",
        requires_runtime_configuration=False,
      ),
    )

  def build(self, request) -> BuildResult:
    self.last_request = request
    return BuildResult(
      source_reference="127.0.0.1:5000/demo-app:latest",
      published_reference="127.0.0.1:5000/demo-app:latest",
      platforms=request.platforms,
      used_buildx=bool(request.platforms),
      pushed=request.push,
    )

  def deployment_references(self, build_result: BuildResult) -> tuple[DeploymentReference, ...]:
    return (
      DeploymentReference(target="compose", image=build_result.published_reference or build_result.source_reference),
      DeploymentReference(target="kubernetes", image=build_result.published_reference or build_result.source_reference),
    )


class CliTests(unittest.TestCase):
  def test_doctor_json_succeeds_when_one_runtime_is_usable(self) -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
      ["--json", "doctor"],
      environment_factory=lambda config: StubEnvironment(),
      stdout=stdout,
      stderr=stderr,
    )

    self.assertEqual(exit_code, 0)
    self.assertIn('"selected_runtime": "docker"', stdout.getvalue())
    self.assertEqual(stderr.getvalue(), "")

  def test_build_command_parses_platforms_and_build_args(self) -> None:
    stdout = StringIO()
    stderr = StringIO()
    environment = StubEnvironment()

    exit_code = main(
      [
        "build",
        "--image",
        "demo-app",
        "--platform",
        "linux/amd64",
        "--platform",
        "linux/arm64",
        "--build-arg",
        "FOO=bar",
      ],
      environment_factory=lambda config: environment,
      stdout=stdout,
      stderr=stderr,
    )

    self.assertEqual(exit_code, 0)
    self.assertEqual(environment.last_request.platforms, ("linux/amd64", "linux/arm64"))
    self.assertEqual(dict(environment.last_request.build_args), {"FOO": "bar"})
    self.assertIn("published image: 127.0.0.1:5000/demo-app:latest", stdout.getvalue())
    self.assertEqual(stderr.getvalue(), "")

  def test_build_command_rejects_invalid_build_args(self) -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
      ["build", "--image", "demo-app", "--build-arg", "BROKEN"],
      environment_factory=lambda config: StubEnvironment(),
      stdout=stdout,
      stderr=stderr,
    )

    self.assertEqual(exit_code, 1)
    self.assertIn("Invalid build argument 'BROKEN'", stderr.getvalue())
    self.assertEqual(stdout.getvalue(), "")


if __name__ == "__main__":
  unittest.main()
