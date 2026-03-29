#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# install-hooks.sh — installs Git hooks from scripts/hooks/ into .git/hooks/
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo -e "${RED}✖  Not inside a Git repository.${RESET}"
  exit 1
}

HOOKS_SRC="$REPO_ROOT/scripts/hooks"
HOOKS_DEST="$REPO_ROOT/.git/hooks"

if [[ ! -d "$HOOKS_SRC" ]]; then
  echo -e "${RED}✖  Hook source directory not found: $HOOKS_SRC${RESET}"
  exit 1
fi

echo ""
echo -e "${BOLD}Installing Git hooks…${RESET}"
echo -e "${CYAN}  Source : $HOOKS_SRC${RESET}"
echo -e "${CYAN}  Target : $HOOKS_DEST${RESET}"
echo ""

INSTALLED=0

for hook_src in "$HOOKS_SRC"/*; do
  hook_name=$(basename "$hook_src")
  hook_dest="$HOOKS_DEST/$hook_name"

  # Back up any existing hook that isn't already our symlink
  if [[ -e "$hook_dest" && ! -L "$hook_dest" ]]; then
    mv "$hook_dest" "${hook_dest}.bak"
    echo -e "  ${CYAN}↩  Backed up existing $hook_name → ${hook_name}.bak${RESET}"
  fi

  ln -sf "$hook_src" "$hook_dest"
  chmod +x "$hook_src"
  echo -e "  ${GREEN}✔  Linked $hook_name${RESET}"
  (( INSTALLED++ )) || true
done

echo ""
if [[ $INSTALLED -eq 0 ]]; then
  echo -e "${RED}⚠  No hooks found in $HOOKS_SRC${RESET}"
else
  echo -e "${GREEN}${BOLD}✔  $INSTALLED hook(s) installed successfully.${RESET}"
fi
echo ""

