#!/usr/bin/env bash
# Executar na EC2 apos iniciar-lab.sh. Nao requer digitar chaves.
set -euo pipefail
KIT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$#" -gt 1 || "${1:-}" == '--help' ]]; then
  echo 'Uso: bash kit/validar-lab.sh [http://DNS_PUBLICO_EC2]'
  [[ "${1:-}" == '--help' ]] && exit 0
  exit 1
fi
if [[ "$#" -eq 1 ]]; then
  LAB_BASE="$1"
elif [[ -f "$HOME/redes-lab.url" ]]; then
  LAB_BASE="$(cat "$HOME/redes-lab.url")"
else
  echo 'Execute iniciar-lab.sh primeiro, ou informe http://DNS_PUBLICO_EC2.' >&2
  exit 1
fi
python3 "$KIT_DIR/validar-api.py" "$LAB_BASE"
