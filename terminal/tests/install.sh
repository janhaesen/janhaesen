#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TEST_DIR="$(mktemp -d "${TMPDIR:-/tmp}/terminal-test.XXXXXXXX")"
trap 'rm -rf "$TEST_DIR"' EXIT
export HOME="$TEST_DIR/home"
export XDG_CONFIG_HOME="$TEST_DIR/custom config"
mkdir -p "$HOME" "$XDG_CONFIG_HOME/lazygit"
printf 'old shell\n' > "$HOME/.zshrc"
printf 'old prompt\n' > "$XDG_CONFIG_HOME/starship.toml"
ln -s "$TEST_DIR/missing" "$HOME/.zprofile"
printf 'old lazygit\n' > "$XDG_CONFIG_HOME/lazygit/config.yml"
"$ROOT_DIR/install.sh" >/dev/null
backup=("$HOME"/.terminal-setup-backups/backup.*)
[[ ${#backup[@]} == 1 && -d "${backup[0]}" ]]
[[ "$(cat "${backup[0]}/zshrc")" == 'old shell' ]]
[[ "$(cat "${backup[0]}/starship.toml")" == 'old prompt' ]]
[[ "$(cat "${backup[0]}/lazygit.yml")" == 'old lazygit' ]]
[[ -L "${backup[0]}/zprofile" && "$(readlink "${backup[0]}/zprofile")" == "$TEST_DIR/missing" ]]
[[ "$(readlink "$HOME/.zshrc")" == "$ROOT_DIR/zshrc" ]]
[[ "$(readlink "$XDG_CONFIG_HOME/starship.toml")" == "$ROOT_DIR/config/starship.toml" ]]
"$ROOT_DIR/install.sh" >/dev/null
backups_after=("$HOME"/.terminal-setup-backups/backup.*)
[[ ${#backups_after[@]} == 1 ]]
"$ROOT_DIR/doctor.sh" >/dev/null
# Follow the documented manual restore procedure.
rm "$HOME/.zshrc"
mv "${backup[0]}/zshrc" "$HOME/.zshrc"
[[ "$(cat "$HOME/.zshrc")" == 'old shell' ]]
if "$ROOT_DIR/doctor.sh" >/dev/null; then
  echo 'doctor must reject a missing managed link' >&2
  exit 1
fi
printf 'Terminal installation tests passed.\n'
