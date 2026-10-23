#!/usr/bin/env bash
# Inicia o kit pronto em uma EC2 Ubuntu 24.04 nova/dedicada ao laboratorio.
# Uso: bash kit/iniciar-lab.sh (descobre os enderecos via IMDSv2)
set -euo pipefail

if [[ "${1:-}" == '--help' || "$#" -gt 2 ]]; then
  echo 'Uso: bash kit/iniciar-lab.sh [DNS_PUBLICO_OU_IPV4]'
  echo 'Use uma EC2 Ubuntu 24.04 dedicada. Execute como ubuntu, sem sudo no script inteiro.'
  [[ "${1:-}" == '--help' ]] && exit 0
  exit 1
fi
KIT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LAB_KEYS_DIR="$HOME/chaves-redes"
if [[ "$EUID" -eq 0 || "$(id -un)" != ubuntu ]]; then
  echo 'Execute como ubuntu, sem sudo no script inteiro.' >&2
  exit 1
fi
source /etc/os-release
if [[ "$ID" != ubuntu || "$VERSION_ID" != 24.04 ]]; then
  echo 'Este kit requer Ubuntu Server 24.04 LTS.' >&2
  exit 1
fi
# IMDSv2 fica acessivel somente dentro da EC2. Nao requer credenciais AWS.
if [[ "$#" -eq 0 ]]; then
  LAB_DISCOVERY=$(python3 - <<'PY'
import sys
from urllib.request import Request, build_opener, ProxyHandler
opener = build_opener(ProxyHandler({}))
base = 'http://169.254.169.254/latest/'
try:
    req = Request(base + 'api/token', method='PUT',
                  headers={'X-aws-ec2-metadata-token-ttl-seconds': '60'})
    with opener.open(req, timeout=3) as response:
        token = response.read().decode()
    for name in ('public-hostname', 'public-ipv4'):
        req = Request(base + 'meta-data/' + name,
                      headers={'X-aws-ec2-metadata-token': token})
        with opener.open(req, timeout=3) as response:
            address = response.read().decode().strip()
        if address:
            print(address)
            break
except OSError:
    sys.exit('Nao foi possivel descobrir o endereco. Use: bash kit/iniciar-lab.sh DNS_PUBLICO_OU_IPV4')
PY
  ) || exit 1
  LAB_HOST="$LAB_DISCOVERY"
else
  # O segundo argumento antigo (IPv4) continua aceito para compatibilidade.
  LAB_HOST="$1"
fi
# Validar marcadores antes de instalar pacotes ou alterar configuracoes.
python3 - "$LAB_HOST" <<'PY'
import ipaddress
import re
import sys
host = sys.argv[1]
try:
    ipaddress.IPv4Address(host)
    sys.exit(0)
except ValueError:
    pass
labels = host.split('.')
if (len(labels) < 2 or len(host) > 253
        or any(not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?', x)
               for x in labels)
        or host == 'SEU_DNS_EC2'):
    sys.exit('Copie o DNS publico real do console, sem esquema, barra ou caminho.')
PY

if sudo test -e /etc/redes-api.env; then
  if [[ ! -f "$LAB_KEYS_DIR/redes-api.env" ]] ||
      ! sudo cmp -s "$LAB_KEYS_DIR/redes-api.env" /etc/redes-api.env; then
    echo 'Ja existe outra configuracao da API. Use uma EC2 nova/dedicada.' >&2
    exit 1
  fi
fi
if sudo test -e /etc/nginx/sites-available/redes; then
  if ! sudo cmp -s "$KIT_DIR/config/redes-http.conf" /etc/nginx/sites-available/redes &&
      ! sudo cmp -s "$KIT_DIR/config/redes-autoassinado.conf" /etc/nginx/sites-available/redes; then
    echo 'O site redes ja possui configuracao diferente. Use uma EC2 dedicada.' >&2
    exit 1
  fi
fi

echo 'Preparando o kit pronto: Nginx, API, banco e credenciais locais...'
sudo apt update
sudo apt install -y nginx curl python3-venv
if [[ ! -f "$LAB_KEYS_DIR/redes-api.env" ]]; then
  python3 "$KIT_DIR/api/gerar_chaves.py" --grupos 2 --saida "$LAB_KEYS_DIR"
fi
sudo install -o root -g root -m 600 "$LAB_KEYS_DIR/redes-api.env" /etc/redes-api.env
bash "$KIT_DIR/instalar-api.sh"

sudo install -d -m 755 /var/www/redes
sudo install -m 644 "$KIT_DIR/site/index.html" "$KIT_DIR/site/painel.html" /var/www/redes/
sudo install -m 644 "$KIT_DIR/config/redes-http.conf" /etc/nginx/sites-available/redes
if [[ -L /etc/nginx/sites-enabled/default ]]; then
  sudo unlink /etc/nginx/sites-enabled/default
fi
sudo ln -sfn /etc/nginx/sites-available/redes /etc/nginx/sites-enabled/redes
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
# UFW, se ativo, continua sendo configurado pelo dono da instancia.
echo 'Validando backend e HTTP pelo Nginx localmente...'
curl --fail --silent --show-error --retry 10 --retry-connrefused --retry-delay 1 \
  http://127.0.0.1:8000/api/saude
echo
curl --fail --silent --show-error http://127.0.0.1/api/saude
echo
umask 077
printf 'http://%s\n' "$LAB_HOST" > "$HOME/redes-lab.url"
echo "Kit iniciado: http://$LAB_HOST/painel.html"
echo "Postman baseUrl: http://$LAB_HOST"
echo "Credenciais privadas: $LAB_KEYS_DIR/entrega-grupos.csv"
echo 'g01: CRUD principal; g02: identidade de teste para validar isolamento.'
echo 'Consulte o CSV no seu terminal privado; nao inclua chaves no relatorio.'
echo 'Reexecutar preserva chaves e banco; o site de referencia sera republicado.'
