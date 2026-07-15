# `container-env`

Python-first runtime abstraction for local Docker and Colima workflows.

## Layout

- `src/container_env/` — library source
- `tests/` — standard-library test suite
- `examples/` — Compose and Kubernetes usage examples
- `docs/` — package-specific template, architecture, and usage notes

## Run locally

```bash
./bin/container-env doctor
./bin/container-env build --image demo-app --context .
PYTHONPATH=src python3 -m unittest discover -s tests -t .
PYTHONPATH=src python3 -m container_env doctor
PYTHONPATH=src python3 -m container_env build --image demo-app --context .
```

## Scope

The first slice provides:

- a programmatic Python facade
- a thin CLI wrapper via `./bin/container-env`, `python3 -m container_env`, or the installed `container-env` script
- Docker and Colima adapters
- local registry automation for insecure local development
- Compose/Kubernetes-oriented deployment references
