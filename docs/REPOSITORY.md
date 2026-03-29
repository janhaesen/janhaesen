# Repository Guide

This document is the repository-focused companion to the profile-oriented `README.md`.

## Purpose

This repository is a personal engineering toolkit with reusable standards, templates, and lightweight automation for day-to-day development work.

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
| [`.github/workflows/repo-hygiene.yml`](../.github/workflows/repo-hygiene.yml) | CI safety net that executes `scripts/check.sh` on PRs and pushes to `main`. |

## Quick Start

```bash
./scripts/bootstrap.sh
```

This command:

1. Installs all hooks from `scripts/hooks/`.
2. Runs `scripts/check.sh` to validate repository health.

## Daily Workflow

```bash
# optional after first clone
./scripts/install-hooks.sh

# before opening a PR
./scripts/check.sh
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

