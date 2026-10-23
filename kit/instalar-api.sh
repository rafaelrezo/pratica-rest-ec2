#!/usr/bin/env bash
# Executar como ubuntu em EC2 Ubuntu 24.04 dedicada ao laboratório.
# Instala somente o backend; Nginx/TLS são configurados no roteiro.
set -euo pipefail
KIT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$EUID" -eq 0 ]]; then
  echo 'Execute como usuário ubuntu, sem sudo no script inteiro.' >&2
  exit 1
fi
if [[ ! -f /etc/redes-api.env ]]; then
  echo 'Use iniciar-lab.sh para preparar as credenciais e iniciar o kit completo.' >&2
  exit 1
fi
sudo apt update
sudo apt install -y python3-venv
if ! id redesapi >/dev/null 2>&1; then
  sudo useradd --system --home /var/lib/redes-api --shell /usr/sbin/nologin redesapi
fi
sudo install -d -m 755 /opt/redes-api
sudo install -d -m 700 -o redesapi -g redesapi /var/lib/redes-api
sudo install -m 644 "$KIT_DIR/api/app.py" "$KIT_DIR/api/requirements.txt" /opt/redes-api/
sudo python3 -m venv /opt/redes-api/.venv
sudo /opt/redes-api/.venv/bin/pip install -r /opt/redes-api/requirements.txt
sudo install -m 644 "$KIT_DIR/config/redes-api.service" /etc/systemd/system/redes-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now redes-api
sudo systemctl restart redes-api
echo 'Backend instalado. Confira: curl -i http://127.0.0.1:8000/api/saude'
echo 'O iniciar-lab.sh configura Nginx e HTTPS e valida o caminho completo.'
