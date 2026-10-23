"""Verificação do contrato HTTP e do isolamento entre grupos, sem AWS."""
import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "api"))
from app import create_app


class Contract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config = {"TESTING": True, "DATABASE": str(Path(self.temp.name) / "db.sqlite"),
                       "API_KEYS_JSON": json.dumps({"g01": "a" * 32, "g02": "b" * 32}),
                       "CORS_ORIGINS": "https://painel.example.org"}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.headers = {"X-API-Key": "a" * 32}
        self.payload = {"nome": "CLP-01", "tipo": "clp", "local": "Planta A", "ativo": True}

    def tearDown(self):
        self.temp.cleanup()

    def create(self):
        return self.client.post("/api/equipamentos", headers=self.headers, json=self.payload)

    def test_crud_and_status(self):
        self.assertEqual(self.client.get("/api/saude").json, {"status": "ok"})
        self.assertEqual(self.client.get("/api/equipamentos").status_code, 401)
        created = self.create()
        self.assertEqual(created.status_code, 201)
        path = created.headers["Location"]
        self.assertEqual(self.client.get(path, headers=self.headers).json["nome"], "CLP-01")
        self.assertEqual(self.create().status_code, 409)
        changed = self.client.patch(path, headers=self.headers, json={"ativo": False})
        self.assertFalse(changed.json["ativo"])
        full = dict(self.payload, nome="CLP-02")
        self.assertEqual(self.client.put(path, headers=self.headers, json=full).status_code, 200)
        self.assertEqual(self.client.delete(path, headers=self.headers).status_code, 204)
        self.assertEqual(self.client.get(path, headers=self.headers).status_code, 404)

    def test_validation(self):
        self.assertEqual(self.client.post("/api/equipamentos", headers=self.headers,
                                        data="x").status_code, 415)
        for payload in ({}, [], {"nome": "incompleto"}, dict(self.payload, ativo="true"),
                        dict(self.payload, campo="indevido"), dict(self.payload, nome=" "),
                        dict(self.payload, tipo=["clp"])):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/api/equipamentos", headers=self.headers,
                                                 json=payload).status_code, 400)
        self.assertEqual(self.client.post("/api/equipamentos", headers=self.headers,
                                         content_type="application/json", data="{").status_code, 400)
        self.assertEqual(self.client.post("/api/equipamentos", headers=self.headers,
                                         json=dict(self.payload, local="x" * 17000)).status_code, 413)

    def test_group_isolation_and_persistence(self):
        path = self.create().headers["Location"]
        other = {"X-API-Key": "b" * 32}
        self.assertEqual(self.client.get("/api/equipamentos", headers=other).json["total"], 0)
        for method in ("get", "patch", "put", "delete"):
            response = getattr(self.client, method)(path, headers=other)
            self.assertEqual(response.status_code, 404)
        response = self.client.post("/api/equipamentos", headers=other, json=self.payload)
        self.assertEqual(response.status_code, 201)  # mesmo nome, outro grupo
        new_client = create_app(self.config).test_client()
        self.assertEqual(new_client.get(path, headers=self.headers).status_code, 200)

    def test_cors_and_reverse_proxy(self):
        preflight = self.client.options("/api/equipamentos", headers={
            "Origin": "https://painel.example.org", "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-api-key"})
        self.assertEqual(preflight.status_code, 204)
        self.assertEqual(preflight.headers["Access-Control-Allow-Origin"], "https://painel.example.org")
        response = self.client.post("/api/equipamentos", json=self.payload,
                                    headers={**self.headers, "Origin": "https://indevido.example.org"})
        self.assertEqual(response.status_code, 403)
        response = self.client.post("/api/equipamentos", json=self.payload, headers={
            **self.headers, "Origin": "https://api.example.org", "X-Forwarded-Proto": "https",
            "X-Forwarded-Host": "api.example.org"})
        self.assertEqual(response.status_code, 201)

    def test_method_and_missing_resource(self):
        response = self.client.put("/api/equipamentos", headers=self.headers, json=self.payload)
        self.assertEqual(response.status_code, 405)
        self.assertIn("GET", response.headers["Allow"])
        self.assertEqual(self.client.get("/api/inexistente", headers=self.headers).status_code, 404)

    def test_no_default_secrets(self):
        for keys in ({}, {"g01": "curta"}, {"g01": "a" * 32, "g02": "a" * 32}):
            with self.assertRaises(RuntimeError):
                create_app(dict(self.config, API_KEYS_JSON=json.dumps(keys)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
