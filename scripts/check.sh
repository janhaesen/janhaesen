#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() {
  echo "[FAIL] $1"
  exit 1
}

pass() {
  echo "[PASS] $1"
}

echo "Running repository checks from: $ROOT_DIR"

# 1) Ensure required files exist
required_files=(
  "$ROOT_DIR/README.md"
  "$ROOT_DIR/docs/REPOSITORY.md"
  "$ROOT_DIR/ENGINEERING_CHANGE_CHECKLIST.md"
  "$ROOT_DIR/.github/CODEOWNERS"
  "$ROOT_DIR/scripts/hooks/commit-msg"
  "$ROOT_DIR/scripts/hooks/pre-commit"
  "$ROOT_DIR/scripts/install-hooks.sh"
  "$ROOT_DIR/scripts/uninstall-hooks.sh"
  "$ROOT_DIR/scripts/bootstrap.sh"
)

for f in "${required_files[@]}"; do
  [[ -f "$f" ]] || fail "Missing required file: $f"
done
pass "Required files present"

# 2) Check shell scripts have valid syntax
shell_files=(
  "$ROOT_DIR/scripts/check.sh"
  "$ROOT_DIR/scripts/bootstrap.sh"
  "$ROOT_DIR/scripts/install-hooks.sh"
  "$ROOT_DIR/scripts/uninstall-hooks.sh"
  "$ROOT_DIR/scripts/hooks/commit-msg"
  "$ROOT_DIR/scripts/hooks/pre-commit"
)

for s in "${shell_files[@]}"; do
  bash -n "$s" || fail "Shell syntax error in: $s"
done
pass "Shell script syntax"

# 3) Ensure key scripts are executable
for s in "${shell_files[@]}"; do
  [[ -x "$s" ]] || fail "Script is not executable: $s"
done
pass "Executable permissions"

# 4) Ensure no trailing whitespace in markdown files
while IFS= read -r -d '' md; do
  if grep -nE "[[:blank:]]+$" "$md" >/dev/null; then
    fail "Trailing whitespace found in: $md"
  fi
done < <(find "$ROOT_DIR" -name "*.md" -type f -print0)
pass "Markdown trailing whitespace"

# 5) Validate commit hook behavior with one valid and one invalid message
if ! echo "feat(repo): add starter hygiene checks" | bash "$ROOT_DIR/scripts/hooks/commit-msg" /dev/stdin >/dev/null; then
  fail "commit-msg hook rejected a valid commit message"
fi

if echo "random message" | bash "$ROOT_DIR/scripts/hooks/commit-msg" /dev/stdin >/dev/null 2>&1; then
  fail "commit-msg hook accepted an invalid commit message"
fi
pass "Conventional Commits enforcement"

echo "All checks passed."

