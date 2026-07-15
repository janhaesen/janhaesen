# Using `container_env`

## CLI examples

```bash
./bin/container-env doctor
./bin/container-env build --image demo-app --context .
./bin/container-env build --image demo-app --platform linux/amd64 --platform linux/arm64

# direct module invocation also works
PYTHONPATH=packages/container-env/src python3 -m container_env doctor
PYTHONPATH=packages/container-env/src python3 -m container_env build --image demo-app --context .
PYTHONPATH=packages/container-env/src python3 -m container_env build --image demo-app --platform linux/amd64 --platform linux/arm64
```

Installed package usage:

```bash
container-env doctor
container-env build --image demo-app --context .
```

## Python example

```python
from pathlib import Path

from container_env import BuildRequest, ContainerEnvironment

environment = ContainerEnvironment()

result = environment.build(
    BuildRequest(
        context=Path("."),
        image="demo-app",
        platforms=("linux/amd64",),
    )
)

for reference in environment.deployment_references(result):
    print(reference.target, reference.image)
```

## First-slice scope

- programmatic Python facade plus a thin CLI wrapper
- Docker and Colima adapters
- local registry automation for insecure local development
- Kubernetes handoff support aimed at Colima-managed k3s
