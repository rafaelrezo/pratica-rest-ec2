# Aprofundamento opcional: HTTPS

REST organiza a interação com recursos e representações. **HTTPS protege o transporte HTTP com TLS**. São assuntos relacionados, mas configurar certificados não é necessário para investigar os métodos, os status e o contrato desta API.

O percurso principal usa HTTP, dados fictícios, chaves de laboratório e acesso restrito à origem autorizada no Security Group. Isso permite concentrar a atividade no funcionamento da API e da aplicação web. Em HTTP, corpo e cabeçalhos não são cifrados; a chave da API identifica a equipe, mas não cifra o tráfego.

Para uma aplicação com dados ou credenciais reais, HTTPS deve fazer parte da publicação. Um estudo posterior pode abordar certificado, nome do servidor, confiança, validade e término de TLS no proxy, preservando os mesmos métodos e caminhos da API.

O site desta documentação usa HTTPS fornecido pelo GitHub Pages. Esse endereço é diferente do serviço didático na EC2, cujo acesso neste roteiro começa com **`http://`**.

**Pergunta opcional:** ao acrescentar TLS no Nginx, seria necessário reescrever POST, GET, PUT, PATCH e DELETE ou a mudança principal estaria na conexão entre cliente e proxy?
