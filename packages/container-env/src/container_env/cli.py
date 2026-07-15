from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Any, Callable, Sequence

from .api import ContainerEnvironment
from .config import BuildRequest, EnvironmentConfig, RegistryConfig
from .errors import ContainerEnvError


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(prog="container-env", description="Container runtime abstraction for Docker and Colima.")
  parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")

  subparsers = parser.add_subparsers(dest="command", required=True)

  doctor = subparsers.add_parser("doctor", help="Inspect the local runtime environment.")
  _add_environment_options(doctor)

  build = subparsers.add_parser("build", help="Build an image and optionally push it to the local registry.")
  _add_environment_options(build)
  build.add_argument("--context", default=".", help="Build context directory.")
  build.add_argument("--image", required=True, help="Image name without registry prefix.")
  build.add_argument("--tag", default="latest", help="Image tag.")
  build.add_argument("--platform", action="append", default=[], help="Target platform; repeat for multiple values.")
  build.add_argument("--dockerfile", help="Optional Dockerfile path.")
  build.add_argument("--build-arg", action="append", default=[], help="Build argument in KEY=VALUE form.")
  build.add_argument("--no-push", action="store_true", help="Build locally without pushing to the managed registry.")

  return parser


def main(
  argv: Sequence[str] | None = None,
  *,
  environment_factory: Callable[[EnvironmentConfig], ContainerEnvironment] | None = None,
  stdout: Any = None,
  stderr: Any = None,
) -> int:
  stdout = stdout or sys.stdout
  stderr = stderr or sys.stderr
  parser = build_parser()
  args = parser.parse_args(list(argv) if argv is not None else None)

  try:
    config = _environment_config_from_args(args)
    factory = environment_factory or (lambda env_config: ContainerEnvironment(env_config))
    environment = factory(config)

    if args.command == "doctor":
      report = environment.doctor()
      payload = _serialize_report(report)
      if args.json:
        json.dump(payload, stdout, indent=2)
        stdout.write("\n")
      else:
        _print_doctor(payload, stdout)
      return _doctor_exit_code(payload)

    if args.command == "build":
      request = BuildRequest(
        context=Path(args.context),
        image=args.image,
        tag=args.tag,
        platforms=tuple(args.platform),
        dockerfile=Path(args.dockerfile) if args.dockerfile else None,
        build_args=_parse_build_args(args.build_arg),
        push=not args.no_push,
      )
      result = environment.build(request)
      references = environment.deployment_references(result)
      payload = {
        "build_result": _normalize(asdict(result)),
        "deployment_references": [_normalize(asdict(reference)) for reference in references],
      }
      if args.json:
        json.dump(payload, stdout, indent=2)
        stdout.write("\n")
      else:
        _print_build(payload, stdout)
      return 0
  except (ContainerEnvError, ValueError) as error:
    if args.json:
      json.dump({"error": str(error)}, stderr, indent=2)
      stderr.write("\n")
    else:
      stderr.write(f"error: {error}\n")
    return 1

  parser.error(f"Unknown command: {args.command}")
  return 2


def _add_environment_options(parser: argparse.ArgumentParser) -> None:
  parser.add_argument(
    "--runtime",
    action="append",
    choices=("docker", "colima"),
    dest="runtimes",
    help="Preferred runtime order; repeat to set precedence.",
  )
  parser.add_argument("--registry-host", default="127.0.0.1", help="Host-side registry bind address.")
  parser.add_argument("--registry-port", type=int, default=5000, help="Host-side registry port.")
  parser.add_argument("--registry-guest-host", help="Optional guest-visible registry hostname override.")
  parser.add_argument("--registry-name", default="container-env-registry", help="Registry container name.")
  parser.add_argument("--no-auto-start-colima", action="store_true", help="Do not auto-start Colima when selected.")
  parser.add_argument("--no-auto-restart-colima", action="store_true", help="Do not auto-restart Colima after registry config changes.")


def _environment_config_from_args(args: argparse.Namespace) -> EnvironmentConfig:
  preferred_runtimes = tuple(args.runtimes) if args.runtimes else ("docker", "colima")
  registry = RegistryConfig(
    name=args.registry_name,
    host=args.registry_host,
    port=args.registry_port,
    guest_host=args.registry_guest_host,
  )
  return EnvironmentConfig(
    preferred_runtimes=preferred_runtimes,
    auto_start_colima=not args.no_auto_start_colima,
    auto_restart_colima=not args.no_auto_restart_colima,
    registry=registry,
  )


def _parse_build_args(values: Sequence[str]) -> dict[str, str]:
  parsed: dict[str, str] = {}
  for value in values:
    key, separator, remainder = value.partition("=")
    if not separator or not key:
      raise ValueError(f"Invalid build argument '{value}'. Expected KEY=VALUE.")
    parsed[key] = remainder
  return parsed


def _serialize_report(report: Any) -> dict[str, Any]:
  payload = _normalize(asdict(report))
  payload["ok"] = bool(report.selected_runtime and report.capabilities and report.capabilities.active)
  return payload


def _normalize(value: Any) -> Any:
  if isinstance(value, Path):
    return str(value)
  if isinstance(value, tuple):
    return [_normalize(item) for item in value]
  if isinstance(value, list):
    return [_normalize(item) for item in value]
  if isinstance(value, dict):
    return {key: _normalize(item) for key, item in value.items()}
  return value


def _doctor_exit_code(payload: dict[str, Any]) -> int:
  return 0 if payload.get("ok") else 1


def _print_doctor(payload: dict[str, Any], stdout: Any) -> None:
  selected_runtime = payload.get("selected_runtime") or "none"
  stdout.write(f"selected runtime: {selected_runtime}\n")
  capabilities = payload.get("capabilities")
  if capabilities:
    stdout.write(
      "capabilities: "
      f"buildx={capabilities['supports_buildx']} "
      f"multi_platform={capabilities['supports_multi_platform']} "
      f"kubernetes={capabilities['supports_kubernetes']}\n"
    )
  registry_access = payload.get("registry_access")
  if registry_access:
    stdout.write(
      "registry access: "
      f"push={registry_access['push_endpoint']} "
      f"pull={registry_access['pull_endpoint']} "
      f"kubernetes={registry_access['kubernetes_endpoint']}\n"
    )
  stdout.write("checks:\n")
  for check in payload["checks"]:
    marker = "OK" if check["ok"] else "FAIL"
    stdout.write(f"- [{marker}] {check['name']}: {check['detail']}\n")
    if check.get("remediation"):
      stdout.write(f"  remediation: {check['remediation']}\n")


def _print_build(payload: dict[str, Any], stdout: Any) -> None:
  result = payload["build_result"]
  stdout.write(f"source image: {result['source_reference']}\n")
  if result["published_reference"]:
    stdout.write(f"published image: {result['published_reference']}\n")
  stdout.write(
    "build details: "
    f"platforms={','.join(result['platforms']) if result['platforms'] else 'default'} "
    f"buildx={result['used_buildx']} pushed={result['pushed']}\n"
  )
  stdout.write("deployment references:\n")
  for reference in payload["deployment_references"]:
    stdout.write(f"- {reference['target']}: {reference['image']}\n")
    for note in reference["notes"]:
      stdout.write(f"  note: {note}\n")

