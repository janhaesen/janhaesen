# Container Environment Architecture

The `container_env` package is a Python-first abstraction over local container runtimes.

## Core layers

1. `api.py` exposes the high-level facade.
2. `runtimes/` contains runtime adapters for Docker and Colima.
3. `registry.py` owns local registry lifecycle.
4. `deploy.py` turns build outputs into Compose/Kubernetes-friendly image references.

## Registry model

The default strategy is **insecure local development mode**:

- host pushes use `127.0.0.1:<port>`
- Colima guest pulls use `host.lima.internal:<port>`
- Colima Kubernetes uses a generated `registries.yaml` for k3s when Kubernetes is enabled

TLS fields already exist in the config model so a stricter registry mode can be added without reshaping the public API.

