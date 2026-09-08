#!/usr/bin/env bash
set -euo pipefail
scripts=$(cd -- "$(dirname -- "$0")" && pwd -P)
command -v python3 >/dev/null
command -v git >/dev/null
exec python3 "$scripts/manage.py" install "$@"
