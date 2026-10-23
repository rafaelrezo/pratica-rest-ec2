# Prática REST na EC2

Inicie uma aplicação pronta de inventário das Plantas A/B/C e descubra como uma página web e o Postman utilizam a mesma API. Não é necessário programar.

O kit contém API, banco persistente, página web, HTTPS, coleção Postman e dois scripts. As chaves da API são geradas na sua EC2; você não precisa recebê-las do professor.

## 1. Iniciar

Use uma EC2 **Ubuntu Server 24.04 LTS**, nova ou dedicada à prática, com IPv4 e DNS públicos, acesso à Internet e usuário `ubuntu`. Pode reutilizar a EC2 da prática 1. No Security Group, permita TCP 22 apenas para seu IP/rede administrativa e 80/443 para o acesso web. A porta 8000 permanece fechada. Se o UFW estiver ativo, permita OpenSSH e Nginx Full. A conta AWS, suas permissões e os custos da instância são pré-requisitos.

Conecte por SSH, verificando a identidade da instância, e execute na EC2:

```bash
sudo apt update
sudo apt install -y git
git clone https://github.com/rafaelrezo/pratica-rest-ec2.git pratica-rest-ec2
cd ~/pratica-rest-ec2
bash kit/iniciar-lab.sh
bash kit/validar-lab.sh
```

Se recebeu o ZIP, extraia e envie `kit/` por SCP para a EC2; execute os dois scripts nessa pasta.

O início instala e configura os componentes prontos. A primeira execução requer Internet e pode levar alguns minutos. A descoberta do endereço usa os metadados IMDSv2 da EC2. Se estiverem desabilitados, copie DNS e IPv4 públicos do console:

```bash
bash kit/iniciar-lab.sh SEU_DNS_EC2 IP_PUBLICO
bash kit/validar-lab.sh
```

A validação imprime método, caminho, status esperado e recebido. Ela cria e exclui apenas um item de ensaio. Um resultado `OK` indica que você pode começar a investigação no Postman e no navegador.

## 2. Acessar

Na sessão SSH privada, consulte a URL e as credenciais geradas:

```bash
cat ~/redes-lab.url
cat ~/chaves-redes/entrega-grupos.csv
openssl x509 -in ~/redes.crt -noout -fingerprint -sha256
```

Use **g01** no trabalho principal. **g02** é uma segunda identidade para testar autorização, sem precisar de outra equipe. As chaves são aleatórias e específicas de cada EC2. Não as inclua no relatório, em prompts ou no Git.

Na sua estação, copie somente o certificado público pelo SSH já verificado:

```bash
scp -i SUA_CHAVE.pem ubuntu@SEU_DNS_EC2:~/redes.crt .
openssl x509 -in redes.crt -noout -fingerprint -sha256
curl --cacert redes.crt -i https://SEU_DNS_EC2/api/saude
```

Compare as impressões digitais. Importe `redes.crt` nas CA Certificates do Postman Desktop, mantendo a verificação TLS ligada. No navegador, confira e estabeleça a confiança específica para esse certificado didático. O certificado autoassinado não possui confiança pública automática.

Abra `https://SEU_DNS_EC2/painel.html`, informe a chave de g01 e clique em **Conectar / listar**.

## 3. Investigar REST

Importe a coleção e o ambiente de `kit/postman/`. Configure `baseUrl` com a URL HTTPS da sua EC2, **sem `/api`**, e `apiKey` com a chave de g01, como valor privado. O PDF `02-api-rest-postman.pdf` detalha o contrato e os experimentos.

| Experimento | O que observar |
| --- | --- |
| GET `/api/saude`, sem chave | 200: a aplicação responde. |
| GET `/api/equipamentos`, sem/com chave | 401/200: autenticação e representação da coleção. |
| POST `/api/equipamentos` | JSON enviado, 201, ID e `Location`. |
| GET do ID criado | O recurso existe e possui uma representação. |
| PATCH e PUT do ID | Alteração parcial e substituição completa; PUT incompleto gera 400. |
| DELETE do ID e outro GET | 204 sem corpo; depois, 404. |
| Usar g02 para ler um ID de g01 | 404: chave válida com escopo diferente. |
| Criar pela página e consultar pelo Postman | Dois clientes utilizam a mesma API e o mesmo armazenamento. |

Abra **Network/Rede** nas ferramentas do navegador. Relacione cada clique com método, URL, corpo JSON, status e mudança na tela. Explique como esse contrato permite criar outros clientes para a mesma API.

Não precisa modificar Python/HTML, compilar frontend ou usar v0 para concluir a prática. O prompt do v0 permanece em `kit/prompts/` como aprofundamento opcional.

## 4. Diagnosticar e encerrar

Na EC2, se necessário:

```bash
sudo systemctl status redes-api --no-pager
curl -i http://127.0.0.1:8000/api/saude
sudo journalctl -u redes-api -n 30 --no-pager
sudo nginx -t
```

Se os testes locais passam e a estação não acessa, confira DNS/IP, regras 443 e caminho de rede. Se houver erro TLS, confira confiança, SAN e validade. Saúde 200 com listagem 401 indica um problema de credencial, e não ausência do serviço.

Reexecutar `iniciar-lab.sh` mantém chaves e banco e republica a página pronta. O certificado dura sete dias: o script o renova se estiver próximo do vencimento ou se o endereço mudar; copie e confira o novo `redes.crt` na estação. A configuração da API fica em `/etc/redes-api.env` e o banco em `/var/lib/redes-api/inventario.db`, fora do repositório.

Salve as evidências, exclua os cadastros de ensaio e termine a EC2 da equipe quando concluir. Confira os recursos remanescentes da conta. O inventário usa somente dados fictícios e não controla equipamentos reais.
