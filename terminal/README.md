# Terminal setup

A portable zsh and Starship setup based on the existing laptop configuration. The optional Homebrew bundle adds fzf, fd, eza, bat, ripgrep, zoxide, direnv, lazygit, lazydocker, k9s, yazi, btop, Poppler (including pdftoppm) and zsh plugins. On macOS it also installs JetBrains Mono Nerd Font. The shell still works when these tools are absent. fnm and pyenv are detected if installed separately.

## Install

Clone this repository to its permanent location, then run:

```bash
./terminal/install.sh --with-brew
```

Homebrew must already be installed and on PATH. Omit `--with-brew` to install only the configuration, for example on Linux or on a machine where tools are managed separately. Start a new login shell afterwards. The installer does not install Homebrew, change your login shell, or configure your terminal application. On macOS, select **JetBrainsMono Nerd Font** in your terminal application after installation. The font cask is skipped on Linux; install a Nerd Font using your distribution or terminal host instead.

The installer links `.zprofile`, `.zshrc`, `${XDG_CONFIG_HOME:-~/.config}/starship.toml` and `lazygit/config.yml` to this repository. Existing files or links are moved to a uniquely named directory under `~/.terminal-setup-backups/`; the directory is printed when used. Repeating the command leaves already-correct links alone. Keep the clone in place: moving or deleting it breaks the links. To restore, remove the relevant link and move the corresponding backup file back to its original location.

Use `~/.zprofile.local` for machine-specific login environment and `~/.zshrc.local` for interactive settings. These files are sourced if present and are not managed by the installer. Keep credentials and machine-specific settings there, not in this repository. Set `XDG_CONFIG_HOME` before running the installer if you use a non-default config directory; the same value must be available in your shell environment.

## Diagnose and test

Run `./terminal/doctor.sh` after installation in a new shell. It checks managed links, tool availability, zsh syntax, Starship prompt rendering and the lazygit config directory. Missing tools and a mismatched lazygit directory are warnings; broken managed links and syntax or prompt errors cause a non-zero exit. Starship may fall back to defaults for some invalid configuration values, so rendering alone does not validate every setting. `STARSHIP_CONFIG` or `LG_CONFIG_FILE` overrides can change what your interactive session uses.

Run `./terminal/tests/install.sh` to test installation, backups, repeated execution, manual restore and doctor failure in an isolated temporary home. It is also included in `./scripts/check.sh`.

The shell runs the zsh completion security audit at each startup; zsh may prompt if it finds insecure completion directories. Resolve the reported ownership or permissions before accepting completion files.

## Tool guide

Run `terminal-help` in a new interactive zsh session for a short guide to the available commands and shortcuts. You can also read [GUIDE.txt](./GUIDE.txt) directly. Press `q` to exit the pager.

Yazi uses Poppler for PDF previews. The terminal must also support an image preview protocol; support depends on your terminal and environment. See [Yazi image preview documentation](https://yazi-rs.github.io/docs/image-preview/) if previews do not appear.

## Prompt and interfaces

Starship shows the directory, Git state, detected Go, Node and Python versions, package and Docker context, Kubernetes and AWS context, slow commands and the last command status. The prompt and lazygit use Nerd Font glyphs; select a Nerd Font in your terminal for correct rendering. Kubernetes context is enabled, so check it before running cluster commands. The Vue indicator checks `package.json` for a Vue dependency.

fzf provides Ctrl-T for files, Ctrl-R for history and Alt-C for directories. `z` uses zoxide for directory navigation. The additional terminal interfaces use their defaults:

- `lazygit`: inspect and manage Git changes in a repository.
- `lazydocker`: inspect Docker containers, images and logs; requires a running Docker-compatible engine.
- `k9s`: navigate Kubernetes resources using your current kubeconfig and context.
- `yazi`: browse files and previews.
- `btop`: inspect system resource usage and processes.

Configuration is intentionally small; adjust the tracked files to propagate changes to other machines.
