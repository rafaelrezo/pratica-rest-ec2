"""Validação simples do kit pronto; executada na EC2, sem expor as chaves."""
import argparse
import csv
import json
import ssl
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="https://DNS_PUBLICO_EC2, sem /api")
    parser.add_argument("--certificado", type=Path, default=Path.home() / "redes.crt")
    parser.add_argument("--chaves", type=Path,
                        default=Path.home() / "chaves-redes/entrega-grupos.csv")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    url = urlsplit(base)
    if url.scheme != "https" or not url.hostname or url.path or url.query or url.fragment or url.username:
        parser.error("Use https://DNS_PUBLICO_EC2, sem caminho, credencial ou query.")
    try:
        context = ssl.create_default_context(cafile=str(args.certificado))
        with args.chaves.open(newline="") as file:
            keys = {row["grupo"]: row["chave"] for row in csv.DictReader(file)}
        primary, other = keys["g01"], keys["g02"]
    except (OSError, KeyError, ssl.SSLError) as exc:
        sys.exit(f"Preparação incompleta ({type(exc).__name__}). Execute iniciar-lab.sh antes.")

    def request(method, path, expected, key=primary, payload=None):
        headers = {}
        if key:
            headers["X-API-Key"] = key
        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode()
        req = Request(base + path, data=data, headers=headers, method=method)
        try:
            response = urlopen(req, context=context, timeout=15)
        except HTTPError as exc:
            response = exc
        with response:
            raw = response.read()
            status = response.status
            location = response.headers.get("Location")
        print(f"{method:6} {path:35} esperado {expected}, recebido {status}")
        if status != expected:
            raise RuntimeError("Status diferente do contrato. Confira URL, serviço e logs.")
        if status == 204:
            if raw:
                raise RuntimeError("DELETE 204 deveria ter corpo vazio.")
            return None, location
        return json.loads(raw), location

    path = None
    failed = False
    try:
        request("GET", "/api/saude", 200, key=None)
        request("GET", "/api/equipamentos", 401, key=None)
        created, location = request("POST", "/api/equipamentos", 201,
                                    payload={"nome": f"VALIDACAO-{time.time_ns()}",
                                             "tipo": "clp", "local": "Planta A", "ativo": True})
        path = f"/api/equipamentos/{created['id']}"
        if location != path:
            raise RuntimeError("Location não identifica o recurso criado.")
        request("GET", path, 200)
        changed, _ = request("PATCH", path, 200, payload={"ativo": False})
        if changed["ativo"] is not False:
            raise RuntimeError("PATCH não alterou o cadastro.")
        request("PUT", path, 400, payload={"ativo": True})
        request("GET", path, 404, key=other)
        request("DELETE", path, 204)
        request("GET", path, 404)
        path = None
        print("OK: HTTPS, chave, criação, leitura, alteração, isolamento e exclusão.")
        print("Agora repita as operações no Postman e na página, observando as mensagens HTTP.")
    except (OSError, URLError, ValueError, KeyError, RuntimeError) as exc:
        # Não imprimir Request/headers: os segredos devem ficar fora dos logs.
        print(f"FALHA ({type(exc).__name__}): confira URL, certificado, serviço e contrato.", file=sys.stderr)
        failed = True
    finally:
        if path:
            try:
                request("DELETE", path, 204)
            except Exception:
                print("Limpeza pendente: exclua apenas o item VALIDACAO criado neste teste.", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
