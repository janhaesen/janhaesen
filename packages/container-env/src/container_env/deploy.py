from __future__ import annotations

from dataclasses import dataclass

from .build import BuildResult
from .capabilities import RegistryAccess
from .errors import DeploymentError


@dataclass(frozen=True)
class DeploymentReference:
  target: str
  image: str
  notes: tuple[str, ...] = ()


def deployment_references(
  build_result: BuildResult,
  registry_access: RegistryAccess | None,
) -> tuple[DeploymentReference, ...]:
  image = build_result.published_reference or build_result.source_reference
  compose_image = image
  kubernetes_image = image
  compose_notes: list[str] = []
  kubernetes_notes: list[str] = []

  if registry_access is not None and registry_access.pull_endpoint != registry_access.push_endpoint:
    compose_image = _rewrite_registry_prefix(image, registry_access.push_endpoint, registry_access.pull_endpoint)
    kubernetes_image = _rewrite_registry_prefix(image, registry_access.push_endpoint, registry_access.kubernetes_endpoint)
    compose_notes.append(
      f"Containers should pull from {registry_access.pull_endpoint} even though the host pushes to {registry_access.push_endpoint}."
    )
    kubernetes_notes.append(
      f"Cluster nodes should pull from {registry_access.kubernetes_endpoint}; host-side references differ."
    )

  if registry_access is not None and registry_access.requires_runtime_configuration:
    kubernetes_notes.append("Ensure the runtime or cluster accepts the registry endpoint before pulling.")

  return (
    DeploymentReference(target="compose", image=compose_image, notes=tuple(compose_notes)),
    DeploymentReference(target="kubernetes", image=kubernetes_image, notes=tuple(kubernetes_notes)),
  )


def render_k3s_registries_yaml(registry_access: RegistryAccess) -> str:
  if not registry_access.kubernetes_endpoint:
    raise DeploymentError("Kubernetes registry configuration requires a pull endpoint.")

  return "\n".join(
    [
      "mirrors:",
      f'  "{registry_access.kubernetes_endpoint}":',
      "    endpoint:",
      f'      - "http://{registry_access.kubernetes_endpoint}"',
      "",
    ]
  )


def _rewrite_registry_prefix(image: str, source_prefix: str, target_prefix: str) -> str:
  prefix = f"{source_prefix}/"
  if image.startswith(prefix):
    return image.replace(prefix, f"{target_prefix}/", 1)
  return image
