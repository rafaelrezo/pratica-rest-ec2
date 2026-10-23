#!/usr/bin/env bash
# Inicia o kit pronto em uma EC2 Ubuntu 24.04 nova/dedicada ao laboratorio.
# Uso: bash kit/iniciar-lab.sh (descobre os enderecos via IMDSv2)
set -euo pipefail

if [[ "${1:-}" == '--help' || ( "$#" -ne 0 && "$#" -ne 2 ) ]]; then
  echo 'Uso: bash kit/iniciar-lab.sh [DNS_PUBLICO_EC2 IPV4_PUBLICO]'
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
            print(response.read().decode())
except OSError:
    sys.exit('Nao foi possivel descobrir DNS/IP. Use: bash kit/iniciar-lab.sh DNS_PUBLICO IPV4_PUBLICO')
PY
  ) || exit 1
  mapfile -t LAB_ADDRESSES <<< "$LAB_DISCOVERY"
  LAB_DNS="${LAB_ADDRESSES[0]:-}"
  LAB_IP="${LAB_ADDRESSES[1]:-}"
else
  LAB_DNS="$1"
  LAB_IP="$2"
fi
# Validar marcadores antes de instalar pacotes ou alterar configuracoes.
python3 - "$LAB_DNS" "$LAB_IP" <<'PY'
import ipaddress
import re
import sys
dns, ip = sys.argv[1:]
labels = dns.split('.')
if (len(labels) < 2 or len(dns) > 253
        or any(not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?', x)
               for x in labels)
        or dns == 'SEU_DNS_EC2'):
    sys.exit('Copie o DNS publico real do console, sem esquema, barra ou caminho.')
try:
    ipaddress.IPv4Address(ip)
except ValueError:
    sys.exit('Copie o IPv4 publico real do console AWS.')
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
sudo apt install -y nginx curl openssl python3-venv
if [[ ! -f "$LAB_KEYS_DIR/redes-api.env" ]]; then
  python3 "$KIT_DIR/api/gerar_chaves.py" --grupos 2 --saida "$LAB_KEYS_DIR"
fi
sudo install -o root -g root -m 600 "$LAB_KEYS_DIR/redes-api.env" /etc/redes-api.env
bash "$KIT_DIR/instalar-api.sh"

sudo install -d -m 755 /var/www/redes
sudo install -m 644 "$KIT_DIR/site/index.html" "$KIT_DIR/site/painel.html" /var/www/redes/
sudo install -d -m 700 /etc/nginx/tls
# Reutilizar certificado valido para estes enderecos; renovar se necessario.
if ! { sudo test -f /etc/nginx/tls/redes.key &&
       sudo openssl x509 -in /etc/nginx/tls/redes.crt -noout -checkend 86400 &&
       sudo openssl x509 -in /etc/nginx/tls/redes.crt -noout -checkhost "$LAB_DNS" &&
       sudo openssl x509 -in /etc/nginx/tls/redes.crt -noout -checkip "$LAB_IP"; } >/dev/null 2>&1; then
  sudo openssl req -x509 -nodes -newkey rsa:2048 -days 7 \
    -keyout /etc/nginx/tls/redes.key -out /etc/nginx/tls/redes.crt \
    -subj '/CN=Laboratorio de Redes' \
    -addext "subjectAltName=DNS:$LAB_DNS,IP:$LAB_IP" \
    -addext 'basicConstraints=critical,CA:TRUE' \
    -addext 'keyUsage=critical,digitalSignature,keyEncipherment,keyCertSign' \
    -addext 'extendedKeyUsage=serverAuth'
fi
sudo chmod 600 /etc/nginx/tls/redes.key
sudo chmod 644 /etc/nginx/tls/redes.crt
sudo install -m 644 "$KIT_DIR/config/redes-autoassinado.conf" /etc/nginx/sites-available/redes
if [[ -L /etc/nginx/sites-enabled/default ]]; then
  sudo unlink /etc/nginx/sites-enabled/default
fi
sudo ln -sfn /etc/nginx/sites-available/redes /etc/nginx/sites-enabled/redes
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
sudo install -o ubuntu -g ubuntu -m 644 /etc/nginx/tls/redes.crt "$HOME/redes.crt"
# UFW, se ativo, continua sendo configurado pelo dono da instancia.
echo 'Validando backend e HTTPS localmente...'
curl --fail --silent --show-error --retry 10 --retry-connrefused --retry-delay 1 \
  http://127.0.0.1:8000/api/saude
echo
curl --fail --silent --show-error --cacert "$HOME/redes.crt" \
  --resolve "$LAB_DNS:443:127.0.0.1" "https://$LAB_DNS/api/saude"
echo
openssl x509 -in "$HOME/redes.crt" -noout -fingerprint -sha256
umask 077
printf 'https://%s\n' "$LAB_DNS" > "$HOME/redes-lab.url"
echo "Kit iniciado: https://$LAB_DNS/painel.html"
echo "Postman baseUrl: https://$LAB_DNS"
echo "Certificado publico: $HOME/redes.crt"
echo "Credenciais privadas: $LAB_KEYS_DIR/entrega-grupos.csv"
echo 'g01: CRUD principal; g02: identidade de teste para validar isolamento.'
echo 'Consulte o CSV no seu terminal privado; nao inclua chaves no relatorio.'
echo 'Reexecutar preserva chaves e banco; o site de referencia sera republicado.'
