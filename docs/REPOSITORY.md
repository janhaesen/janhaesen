# Repository Guide

This document is the repository-focused companion to the profile-oriented `README.md`.

## Purpose

This repository is a personal engineering toolkit with reusable standards, templates, and lightweight automation for day-to-day development work.

## Structure

- Root-level files and scripts are for **shared repository governance**.
- Reusable implementations should live under **`packages/`** as self-contained units with their own source, tests, examples, docs, and packaging metadata.
- Not every package is expected to be used at the same time; isolation is preferred over flattening everything into the repository root.

## Repository Assets

| File | Description |
|------|-------------|
| [`ENGINEERING_CHANGE_CHECKLIST.md`](../ENGINEERING_CHANGE_CHECKLIST.md) | Checklist for planning, implementing, validating, and rolling out changes safely. |
| [`.gitignore`](../.gitignore) | Ignore rules for macOS, editors, temporary files, and local secrets. |
| [`.editorconfig`](../.editorconfig) | Shared formatting defaults across editors. |
| [`CONTRIBUTING.md`](../CONTRIBUTING.md) | Contribution workflow, quality expectations, and local validation guidance. |
| [`.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md) | PR structure for context, validation, and risk communication. |
| [`.github/ISSUE_TEMPLATE/bug_report.md`](../.github/ISSUE_TEMPLATE/bug_report.md) | Structured bug report template. |
| [`.github/ISSUE_TEMPLATE/feature_request.md`](../.github/ISSUE_TEMPLATE/feature_request.md) | Structured feature request template. |
| [`.github/CODEOWNERS`](../.github/CODEOWNERS) | Default code ownership and review routing. |
| [`scripts/hooks/commit-msg`](../scripts/hooks/commit-msg) | Enforces Conventional Commits on commit message subjects. |
| [`scripts/hooks/pre-commit`](../scripts/hooks/pre-commit) | Fast local guardrails for staged markdown and shell files before commit. |
| [`scripts/install-hooks.sh`](../scripts/install-hooks.sh) | Installs all versioned hooks from `scripts/hooks/`. |
| [`scripts/uninstall-hooks.sh`](../scripts/uninstall-hooks.sh) | Removes installed hook symlinks and restores backups. |
| [`scripts/check.sh`](../scripts/check.sh) | Full local repository hygiene checks. |
| [`scripts/bootstrap.sh`](../scripts/bootstrap.sh) | One-step setup: installs hooks and runs local checks. |
| [`terminal/`](../terminal/) | Portable zsh, Starship and terminal tools configuration, backup-aware installer, doctor and isolated installation tests. |
| [`bin/container-env`](../bin/container-env) | Repo-local launcher for the `container-env` CLI without installing the package. |
| [`.github/workflows/repo-hygiene.yml`](../.github/workflows/repo-hygiene.yml) | CI safety net that executes `scripts/check.sh` on PRs and pushes to `main`. |

## Packages

| Package | Description |
|---------|-------------|
| [`packages/container-env/`](../packages/container-env/) | Self-contained Python package that abstracts Docker and Colima environment setup, local registry management, and deployment handoff. |
| [`packages/container-env/docs/`](../packages/container-env/docs/) | Package-local template, architecture, and usage documentation. |
| [`packages/container-env/tests/`](../packages/container-env/tests/) | Standard-library unit tests for runtime selection, build orchestration, and registry endpoint behavior. |
| [`packages/container-env/examples/`](../packages/container-env/examples/) | Compose and Kubernetes examples that use package-generated image references. |
| [`packages/container-env/src/container_env/cli.py`](../packages/container-env/src/container_env/cli.py) | Thin CLI wrapper that exposes doctor and build commands on top of the package facade. |

## Quick Start

```bash
./scripts/bootstrap.sh
```

This command:

1. Installs all hooks from `scripts/hooks/`.
2. Runs `scripts/check.sh` to validate shell hygiene plus any package-local Python syntax and tests under `packages/`.

## Daily Workflow

```bash
# optional after first clone
./scripts/install-hooks.sh

# run the repo-local container-env CLI without installation
./bin/container-env doctor

# before opening a PR
./scripts/check.sh

# run the container-env package tests directly
PYTHONPATH=packages/container-env/src python3 -m unittest discover -s packages/container-env/tests -t packages/container-env
```

## Commit Policy

Conventional Commit format:

```text
<type>[(<scope>)][!]: <description>
```

Allowed types:

- `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `build`, `ci`, `revert`

Examples:

```text
feat(auth): add OAuth2 login
fix(parser): handle empty input
chore(repo): add bootstrap script
feat!: redesign public API
```

## Hook Overview

- `commit-msg`: validates commit message format.
- `pre-commit`: runs fast checks on staged files:
  - markdown trailing whitespace check
  - `bash -n` syntax checks for staged `.sh` files

## Uninstall Hooks

```bash
./scripts/uninstall-hooks.sh
```

## Related Docs

- Profile README: [`README.md`](../README.md)
- Contribution guide: [`CONTRIBUTING.md`](../CONTRIBUTING.md)
- Engineering checklist: [`ENGINEERING_CHANGE_CHECKLIST.md`](../ENGINEERING_CHANGE_CHECKLIST.md)
- Container environment template notes: [`packages/container-env/docs/TEMPLATE.md`](../packages/container-env/docs/TEMPLATE.md)
- Container environment architecture: [`packages/container-env/docs/architecture/container-env.md`](../packages/container-env/docs/architecture/container-env.md)
- Container environment usage: [`packages/container-env/docs/usage/container-env.md`](../packages/container-env/docs/usage/container-env.md)
