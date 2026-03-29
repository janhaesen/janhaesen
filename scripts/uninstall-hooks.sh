#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# uninstall-hooks.sh — removes installed Git hooks and restores any backups
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

echo ""
echo -e "${BOLD}Uninstalling Git hooks…${RESET}"
echo ""

REMOVED=0

for hook_src in "$HOOKS_SRC"/*; do
  hook_name=$(basename "$hook_src")
  hook_dest="$HOOKS_DEST/$hook_name"

  if [[ -L "$hook_dest" ]]; then
    rm "$hook_dest"
    echo -e "  ${GREEN}✔  Removed symlink: $hook_name${RESET}"
    (( REMOVED++ )) || true

    # Restore backup if one exists
    if [[ -e "${hook_dest}.bak" ]]; then
      mv "${hook_dest}.bak" "$hook_dest"
      echo -e "  ${CYAN}↩  Restored backup: $hook_name${RESET}"
    fi
  else
    echo -e "  ${CYAN}–  Not installed (skipped): $hook_name${RESET}"
  fi
done

echo ""
echo -e "${GREEN}${BOLD}✔  Done. $REMOVED hook(s) removed.${RESET}"
echo ""

