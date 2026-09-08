#!/usr/bin/env bash
set -euo pipefail
scripts=$(cd -- "$(dirname -- "$0")" && pwd -P)
exec python3 "$scripts/manage.py" uninstall "$@"
