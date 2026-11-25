#!/usr/bin/env bash
set -u
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}"
errors=0
check_link() {
  local path="$1" expected="$2"
  if [[ -L "$path" && "$(readlink "$path")" == "$expected" && -e "$path" ]]; then
    printf '[OK] %s\n' "$path"
  else
    printf '[FAIL] Missing or incorrect link: %s\n' "$path"
    errors=$((errors + 1))
  fi
}
check_link "$HOME/.zprofile" "$ROOT_DIR/zprofile"
check_link "$HOME/.zshrc" "$ROOT_DIR/zshrc"
check_link "$CONFIG_DIR/starship.toml" "$ROOT_DIR/config/starship.toml"
check_link "$CONFIG_DIR/lazygit/config.yml" "$ROOT_DIR/config/lazygit/config.yml"

for tool in zsh starship fzf fd eza bat rg zoxide direnv lazygit lazydocker k9s yazi btop pdftoppm; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '[OK] %s: %s\n' "$tool" "$(command -v "$tool")"
  else
    printf '[WARN] %s not installed or not on PATH\n' "$tool"
  fi
done
if command -v zsh >/dev/null 2>&1; then
  if zsh -n "$ROOT_DIR/zprofile" "$ROOT_DIR/zshrc"; then
    printf '[OK] zsh syntax\n'
  else
    printf '[FAIL] zsh syntax\n'
    errors=$((errors + 1))
  fi
fi
if command -v starship >/dev/null 2>&1 && [[ -e "$CONFIG_DIR/starship.toml" ]]; then
  if STARSHIP_CONFIG="$CONFIG_DIR/starship.toml" starship prompt >/dev/null; then
    printf '[OK] Starship prompt rendered with installed config\n'
  else
    printf '[FAIL] Starship prompt failed\n'
    errors=$((errors + 1))
  fi
fi
if command -v lazygit >/dev/null 2>&1; then
  lazygit_dir="$(XDG_CONFIG_HOME="$CONFIG_DIR" lazygit --print-config-dir 2>/dev/null)" || lazygit_dir=''
  if [[ "$lazygit_dir" == "$CONFIG_DIR/lazygit" ]]; then
    printf '[OK] lazygit config directory: %s\n' "$lazygit_dir"
  else
    printf '[WARN] lazygit config directory: %s (expected %s/lazygit)\n' "${lazygit_dir:-unknown}" "$CONFIG_DIR"
  fi
fi
if (( errors )); then
  printf '%s configuration check(s) failed. Run ./terminal/install.sh to repair links.\n' "$errors"
  exit 1
fi
printf 'Configuration checks passed. Missing optional tools are warnings.\n'
