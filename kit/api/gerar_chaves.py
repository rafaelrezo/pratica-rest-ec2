"""Executar na EC2. Gera arquivos privados; nunca incluí-los no kit público."""
import argparse
import json
import os
import secrets
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--grupos", type=int, default=8)
parser.add_argument("--saida", default="chaves")
args = parser.parse_args()
if not 1 <= args.grupos <= 100:
    parser.error("Use de 1 a 100 grupos.")
target = Path(args.saida)
target.mkdir(mode=0o700, parents=True, exist_ok=True)
paths = [target / "redes-api.env", target / "entrega-grupos.csv"]
if any(path.exists() for path in paths):
    parser.error("Arquivos já existem. Escolha outro diretório para evitar rotação acidental.")
keys = {f"g{i:02}": secrets.token_urlsafe(32) for i in range(1, args.grupos + 1)}
env = "LAB_API_KEYS_JSON='" + json.dumps(keys) + "'\n"
env += 'LAB_DB=/var/lib/redes-api/inventario.db\nLAB_CORS_ORIGINS=""\n'
csv = "grupo,chave\n" + "".join(f"{group},{key}\n" for group, key in keys.items())
for path, content in zip(paths, (env, csv)):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as file:
        file.write(content)
print("Arquivos privados criados em", target.resolve())
print("Consulte o CSV no seu terminal privado. Nao inclua chaves em relatorios ou no kit.")
