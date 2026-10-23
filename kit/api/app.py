"""API didática de inventário. Sem comunicação com equipamentos reais."""
import hmac
import json
import os
import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, request
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        MAX_CONTENT_LENGTH=16 * 1024,
        DATABASE=os.environ.get("LAB_DB", "/var/lib/redes-api/inventario.db"),
        API_KEYS_JSON=os.environ.get("LAB_API_KEYS_JSON", "{}"),
        CORS_ORIGINS=os.environ.get("LAB_CORS_ORIGINS", ""),
    )
    if config:
        app.config.update(config)
    keys = json.loads(app.config["API_KEYS_JSON"])
    if (not isinstance(keys, dict) or not keys
            or any(not isinstance(k, str) or not k or not isinstance(v, str)
                   or len(v) < 24 for k, v in keys.items())
            or len(set(keys.values())) != len(keys)):
        raise RuntimeError("Configure chaves distintas de pelo menos 24 caracteres.")
    allowed = {x.strip() for x in app.config["CORS_ORIGINS"].split(",") if x.strip()}
    # Confiar nestes cabeçalhos somente porque Gunicorn escuta em loopback
    # e Nginx os sobrescreve. Não expor a porta 8000 na rede.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    db_path = Path(app.config["DATABASE"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grupo TEXT NOT NULL, nome TEXT NOT NULL, tipo TEXT NOT NULL,
            local TEXT NOT NULL, ativo INTEGER NOT NULL,
            UNIQUE(grupo, nome))""")

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(db_path, timeout=5)
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_error):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    def error(message, status):
        return jsonify(erro=message), status

    @app.before_request
    def authorize():
        origin = request.headers.get("Origin")
        same_origin = origin == request.host_url.rstrip("/")
        g.cors_origin = origin if origin and (same_origin or origin in allowed) else None
        if origin and not g.cors_origin:
            return error("Origem não permitida.", 403)
        if request.method == "OPTIONS":
            return "", 204
        if request.path == "/api/saude" and request.method in ("GET", "HEAD"):
            return None
        supplied = request.headers.get("X-API-Key", "")
        for group, key in keys.items():
            if hmac.compare_digest(supplied.encode(), key.encode()):
                g.group = group
                return None
        return error("Chave ausente ou inválida.", 401)

    @app.after_request
    def headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        if getattr(g, "cors_origin", None):
            response.headers["Access-Control-Allow-Origin"] = g.cors_origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key"
            response.headers["Access-Control-Expose-Headers"] = "Location"
            response.vary.add("Origin")
        return response

    @app.errorhandler(HTTPException)
    def http_error(exc):
        response = exc.get_response()  # preservar Allow em respostas 405
        response.data = app.json.dumps({"erro": exc.description})
        response.content_type = "application/json"
        return response

    def as_dict(row):
        return {"id": row["id"], "nome": row["nome"], "tipo": row["tipo"],
                "local": row["local"], "ativo": bool(row["ativo"])}

    def find(item_id):
        return db().execute(
            "SELECT * FROM equipamentos WHERE id = ? AND grupo = ?",
            (item_id, g.group)).fetchone()

    def validate(partial=False):
        if not request.is_json:
            return None, error("Use Content-Type: application/json.", 415)
        data = request.get_json()  # JSON malformado gera 400
        fields = {"nome", "tipo", "local", "ativo"}
        if not isinstance(data, dict) or not data or set(data) - fields:
            return None, error("Objeto JSON vazio ou com campos desconhecidos.", 400)
        if not partial and set(data) != fields:
            return None, error("Informe nome, tipo, local e ativo.", 400)
        for field in ("nome", "local"):
            if field in data:
                if not isinstance(data[field], str) or not 1 <= len(data[field].strip()) <= 80:
                    return None, error(f"{field}: use texto de 1 a 80 caracteres.", 400)
                data[field] = data[field].strip()
        if "tipo" in data and data["tipo"] not in ("sensor", "clp", "ihm", "atuador", "outro"):
            return None, error("tipo: sensor, clp, ihm, atuador ou outro.", 400)
        if "ativo" in data and type(data["ativo"]) is not bool:
            return None, error("ativo deve ser true ou false (sem aspas).", 400)
        return data, None

    @app.get("/api/saude")
    def health():
        return jsonify(status="ok")

    @app.route("/api/equipamentos", methods=["GET", "POST"])
    def collection():
        if request.method == "GET":
            rows = db().execute("SELECT * FROM equipamentos WHERE grupo = ? ORDER BY id",
                                (g.group,)).fetchall()
            return jsonify(itens=[as_dict(row) for row in rows], total=len(rows))
        data, invalid = validate()
        if invalid:
            return invalid
        try:
            with db():
                cursor = db().execute(
                    "INSERT INTO equipamentos(grupo,nome,tipo,local,ativo) VALUES(?,?,?,?,?)",
                    (g.group, data["nome"], data["tipo"], data["local"], data["ativo"]))
            item_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            return error("Já existe equipamento com esse nome neste grupo.", 409)
        response = jsonify(as_dict(find(item_id)))
        response.status_code = 201
        response.headers["Location"] = f"/api/equipamentos/{item_id}"
        return response

    @app.route("/api/equipamentos/<int:item_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
    def item(item_id):
        row = find(item_id)
        if row is None:
            return error("Equipamento não encontrado neste grupo.", 404)
        if request.method == "GET":
            return jsonify(as_dict(row))
        if request.method == "DELETE":
            with db():
                db().execute("DELETE FROM equipamentos WHERE id = ? AND grupo = ?",
                             (item_id, g.group))
            return "", 204
        data, invalid = validate(partial=request.method == "PATCH")
        if invalid:
            return invalid
        merged = as_dict(row)
        merged.update(data)
        try:
            with db():
                db().execute("""UPDATE equipamentos SET nome=?,tipo=?,local=?,ativo=?
                                WHERE id=? AND grupo=?""",
                             (merged["nome"], merged["tipo"], merged["local"],
                              merged["ativo"], item_id, g.group))
        except sqlite3.IntegrityError:
            return error("Já existe equipamento com esse nome neste grupo.", 409)
        return jsonify(as_dict(find(item_id)))

    return app
