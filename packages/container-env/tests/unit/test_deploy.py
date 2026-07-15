from __future__ import annotations

import unittest

from container_env.build import BuildResult
from container_env.capabilities import RegistryAccess
from container_env.deploy import deployment_references, render_k3s_registries_yaml


class DeployTests(unittest.TestCase):
  def test_deployment_references_rewrite_pull_prefixes(self) -> None:
    references = deployment_references(
      BuildResult(
        source_reference="127.0.0.1:5000/app:latest",
        published_reference="127.0.0.1:5000/app:latest",
        platforms=(),
        used_buildx=False,
        pushed=True,
      ),
      RegistryAccess(
        mode="insecure",
        push_endpoint="127.0.0.1:5000",
        pull_endpoint="host.lima.internal:5000",
        kubernetes_endpoint="host.lima.internal:5000",
        requires_runtime_configuration=True,
      ),
    )

    self.assertEqual(references[0].image, "host.lima.internal:5000/app:latest")
    self.assertEqual(references[1].image, "host.lima.internal:5000/app:latest")

  def test_render_k3s_registries_yaml_uses_http_endpoint(self) -> None:
    yaml_text = render_k3s_registries_yaml(
      RegistryAccess(
        mode="insecure",
        push_endpoint="127.0.0.1:5000",
        pull_endpoint="host.lima.internal:5000",
        kubernetes_endpoint="host.lima.internal:5000",
        requires_runtime_configuration=True,
      )
    )

    self.assertIn('"host.lima.internal:5000"', yaml_text)
    self.assertIn('"http://host.lima.internal:5000"', yaml_text)


if __name__ == "__main__":
  unittest.main()

