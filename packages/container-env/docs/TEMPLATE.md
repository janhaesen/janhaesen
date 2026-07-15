# Python Template Notes

This repository now includes a Python package starter for local container-runtime orchestration.

## Rename points when copying

Update these values together when promoting the template into a project-specific repository:

1. `packages/container-env/pyproject.toml` project name
2. `packages/container-env/src/container_env/` package directory
3. `import container_env` references in tests and consumer code
4. Example image names and registry container names

## Why this matters

The package intentionally keeps the first implementation small and copyable. Explicit rename points make the template usable without requiring a separate templating engine.
