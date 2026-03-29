# Contributing

This repository is primarily a personal engineering standards repo, but contributions and improvements are welcome.

## Workflow

1. Create a branch from `main`.
2. Make focused changes with a small blast radius.
3. Follow Conventional Commits for every commit.
4. Run local checks before opening a PR.
5. Open a PR using the provided template.

## Commit convention

This repository enforces Conventional Commits via the `commit-msg` hook.

Example:

```text
feat(checklist): add rollout guardrails section
```

## Local checks

Run:

```bash
./scripts/bootstrap.sh
./scripts/check.sh
```

Use `./scripts/bootstrap.sh` once per clone to install hooks and validate setup.

## Repository docs

Operational repository documentation lives in `docs/REPOSITORY.md`.

## Pull requests

- Keep PRs small and easy to review.
- Include context, risks, and validation notes.
- Link any related issue.
- Update `docs/REPOSITORY.md` when adding new repo assets.

## Code style

- Follow `.editorconfig` settings.
- Keep shell scripts POSIX/Bash compatible and readable.
- Prefer portable tooling over ecosystem-specific dependencies.
