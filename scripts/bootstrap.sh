#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Bootstrapping repository at: $ROOT_DIR"

echo "Step 1/2: Installing hooks"
"$ROOT_DIR/scripts/install-hooks.sh"

echo "Step 2/2: Running repository checks"
"$ROOT_DIR/scripts/check.sh"

echo "Bootstrap complete."

