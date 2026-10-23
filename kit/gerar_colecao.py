"""Recria a coleção pública, sem chaves reais."""
import json
from pathlib import Path

root = Path(__file__).parent / "postman"
root.mkdir(exist_ok=True)
items = []


def add(name, method, path, status, body=None, checks=(), noauth=False, raw=None):
    request = {"method": method, "header": [], "url": "{{baseUrl}}/api" + path,
               "description": "Esperado: HTTP " + str(status)}
    if noauth:
        request["auth"] = {"type": "noauth"}
    if body is not None:
        request["header"].append({"key": "Content-Type", "value": "application/json"})
        request["body"] = {"mode": "raw", "raw": json.dumps(body, ensure_ascii=False, indent=2),
                           "options": {"raw": {"language": "json"}}}
    if raw is not None:
        request["header"].append({"key": "Content-Type", "value": "text/plain"})
        request["body"] = {"mode": "raw", "raw": raw}
    tests = [f'pm.test("HTTP {status}", () => pm.response.to.have.status({status}));', *checks]
    items.append({"name": name, "request": request,
                  "event": [{"listen": "test", "script": {"type": "text/javascript", "exec": tests}}]})


data = {"nome": "{{nomeTeste}}", "tipo": "clp", "local": "Planta A", "ativo": True}
add("01 Saúde (sem chave)", "GET", "/saude", 200, noauth=True)
add("02 Listar sem chave → 401", "GET", "/equipamentos", 401, noauth=True)
add("03 Listar meu grupo", "GET", "/equipamentos", 200,
    checks=['pm.test("Lista e total", () => { const d=pm.response.json(); pm.expect(d.itens).to.be.an("array"); pm.expect(d.total).to.eql(d.itens.length); });'])
add("04 Criar equipamento", "POST", "/equipamentos", 201, data,
    checks=['pm.test("ID e Location", () => { const d=pm.response.json(); pm.expect(d.id).to.be.a("number"); pm.expect(pm.response.headers.get("Location")).to.eql("/api/equipamentos/"+d.id); pm.environment.set("equipamentoId", String(d.id)); });'])
items[-1]["event"].insert(0, {"listen": "prerequest", "script": {"type": "text/javascript", "exec": [
    'pm.collectionVariables.set("nomeTeste", "CLP-"+Date.now());']}})
add("05 Consultar por ID", "GET", "/equipamentos/{{equipamentoId}}", 200)
add("06 Repetir nome → 409", "POST", "/equipamentos", 409, data)
add("07 Alterar um campo (PATCH)", "PATCH", "/equipamentos/{{equipamentoId}}", 200,
    {"ativo": False}, checks=['pm.test("Ativo é false", () => pm.expect(pm.response.json().ativo).to.eql(false));'])
add("08 Substituir cadastro (PUT)", "PUT", "/equipamentos/{{equipamentoId}}", 200,
    dict(data, local="Planta B"))
add("09 Campos incompletos → 400", "POST", "/equipamentos", 400, {"nome": "Incompleto"})
add("10 Tipo de conteúdo incorreto → 415", "POST", "/equipamentos", 415, raw="isto nao e JSON")
add("11 Método indevido → 405", "PUT", "/equipamentos", 405, data)
add("12 Excluir", "DELETE", "/equipamentos/{{equipamentoId}}", 204,
    checks=['pm.test("204 sem corpo", () => pm.expect(pm.response.text()).to.eql(""));'])
add("13 Consultar excluído → 404", "GET", "/equipamentos/{{equipamentoId}}", 404)

collection = {"info": {"name": "Redes 2026-2 | Inventário REST",
                       "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                       "description": "Execute em ordem. Somente dados fictícios. Não compartilhe ambientes preenchidos com chaves."},
              "auth": {"type": "apikey", "apikey": [{"key": "key", "value": "X-API-Key", "type": "string"},
                        {"key": "value", "value": "{{apiKey}}", "type": "string"},
                        {"key": "in", "value": "header", "type": "string"}]},
              "variable": [{"key": "nomeTeste", "value": ""}], "item": items}
environment = {"name": "Redes | preencher localmente", "_postman_variable_scope": "environment",
               "values": [{"key": "baseUrl", "value": "https://SEU_DNS_EC2", "enabled": True},
                          {"key": "apiKey", "value": "", "type": "secret", "enabled": True},
                          {"key": "equipamentoId", "value": "", "enabled": True}]}
for name, value in (("redes-crud.postman_collection.json", collection),
                    ("redes.postman_environment.json", environment)):
    (root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
