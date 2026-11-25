#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
INSTALL_PACKAGES=false
case "${1:-}" in
  '') ;;
  --with-brew) INSTALL_PACKAGES=true ;;
  -h|--help) printf 'Usage: %s [--with-brew]\n' "$0"; exit 0 ;;
  *) printf 'Unknown argument: %s\n' "$1" >&2; exit 2 ;;
esac
if (( $# > 1 )); then
  echo 'Only one option is supported.' >&2
  exit 2
fi

if "$INSTALL_PACKAGES"; then
  if ! command -v brew >/dev/null 2>&1; then
    echo 'Homebrew is required for --with-brew; install it first and retry.' >&2
    exit 1
  fi
  brew bundle --file "$ROOT_DIR/Brewfile"
fi

CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}"
BACKUP_DIR=''
install_link() {
  local source="$1" destination="$2" current
  mkdir -p "$(dirname "$destination")"
  if [[ -L "$destination" ]]; then
    current="$(readlink "$destination")"
    if [[ "$current" == "$source" ]]; then
      printf 'Already configured: %s\n' "$destination"
      return
    fi
  fi
  if [[ -e "$destination" || -L "$destination" ]]; then
    if [[ -z "$BACKUP_DIR" ]]; then
      mkdir -p "$HOME/.terminal-setup-backups"
      BACKUP_DIR="$(mktemp -d "$HOME/.terminal-setup-backups/backup.XXXXXXXX")"
      printf 'Backups: %s\n' "$BACKUP_DIR"
    fi
    local backup_name="$3"
    mv "$destination" "$BACKUP_DIR/$backup_name"
  fi
  ln -s "$source" "$destination"
  printf 'Linked: %s\n' "$destination"
}

install_link "$ROOT_DIR/zprofile" "$HOME/.zprofile" zprofile
install_link "$ROOT_DIR/zshrc" "$HOME/.zshrc" zshrc
install_link "$ROOT_DIR/config/starship.toml" "$CONFIG_DIR/starship.toml" starship.toml
install_link "$ROOT_DIR/config/lazygit/config.yml" "$CONFIG_DIR/lazygit/config.yml" lazygit.yml
printf 'Done. Start a new login shell to load the configuration.\n'
