# janhaesen

Personal repository by **Jan Haesen** — a collection of engineering templates, checklists, and resources I use across projects.

---

## 📋 Contents

| File | Description |
|------|-------------|
| [`ENGINEERING_CHANGE_CHECKLIST.md`](./ENGINEERING_CHANGE_CHECKLIST.md) | A comprehensive checklist to use for every engineering change (feature, bugfix, refactor, infra, docs, security, etc.) |
| [`.gitignore`](./.gitignore) | Ignores OS artefacts, IDE files, logs, temp files, and secrets across macOS, JetBrains, VS Code, and Vim environments. |
| [`scripts/hooks/commit-msg`](./scripts/hooks/commit-msg) | Git `commit-msg` hook that enforces the [Conventional Commits](https://www.conventionalcommits.org) specification. |
| [`scripts/install-hooks.sh`](./scripts/install-hooks.sh) | Symlinks all hooks from `scripts/hooks/` into `.git/hooks/` and backs up any pre-existing hooks. |
| [`scripts/uninstall-hooks.sh`](./scripts/uninstall-hooks.sh) | Removes installed hook symlinks and restores any backups. |

---

## 🚀 About

This repository serves as a personal knowledge base and toolkit. It holds reusable artifacts that help me maintain consistency and quality across different projects and teams.

---

## 🛠️ Usage

### Engineering Change Checklist

Use the checklist whenever you are about to make a change to a codebase:

1. Copy [`ENGINEERING_CHANGE_CHECKLIST.md`](./ENGINEERING_CHANGE_CHECKLIST.md) into your project or PR description.
2. Fill in the **Change Summary** section at the top.
3. Work through each section, marking items as:
   - `[x]` — done
   - `[ ]` — not done
   - `[N/A]` — not applicable
4. Use it as a self-review gate before requesting code review.

---

### Conventional Commits Hook

The `commit-msg` hook rejects any commit whose message does not follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.

#### Install

```bash
./scripts/install-hooks.sh
```

This symlinks `scripts/hooks/commit-msg` into `.git/hooks/`. Any pre-existing hook is automatically backed up as `<hook>.bak`.

#### Uninstall

```bash
./scripts/uninstall-hooks.sh
```

Removes the symlinks and restores any backups.

#### Commit message format

```
<type>[(<scope>)][!]: <description>

[optional body]

[optional footer(s)]
```

| Type | When to use |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code restructuring, no feature/fix |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `chore` | Tooling, deps, config |
| `build` | Build system changes |
| `ci` | CI/CD pipeline changes |
| `revert` | Revert a previous commit |

**Examples:**

```
feat(auth): add OAuth2 login
fix: handle nil pointer in parser
chore(deps): bump lodash to 4.17.21
feat!: redesign public API (breaking change)
```

> Append `!` after the type/scope to signal a **breaking change**.

---

## 📐 Principles

- **Minimal blast radius** — scope changes tightly and roll out carefully.
- **Observability first** — if you can't measure it, you can't trust it.
- **Backward compatibility by default** — break things intentionally, never accidentally.
- **Security is not optional** — every change goes through a threat model.

---

## 📬 Contact

- **GitHub**: [@janhaesen](https://github.com/janhaesen)

---

## 📄 License

This repository is personal and does not carry an open-source license. Feel free to use the templates as inspiration for your own workflows.

