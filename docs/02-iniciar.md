# 2. Iniciar na EC2

**Objetivo:** iniciar os artefatos prontos e comprovar que a API responde. Os comandos desta página são iguais para quem usa WSL, Ubuntu ou macOS, pois são executados **dentro da EC2**.

## 2.1. Obter o kit no servidor

**Onde:** terminal **A — EC2**, conectado por SSH, com usuário `ubuntu`.

```bash
cd ~
sudo apt update
sudo apt install -y git
git clone https://github.com/rafaelrezo/pratica-rest-ec2.git
cd ~/pratica-rest-ec2
```

Há dois clones: o do seu computador fornece os JSON ao Postman; o da EC2 fornece os arquivos que o servidor executa. Não envie o `.pem` para dentro do repositório ou da EC2.

**Esperado:** dentro de `~/pratica-rest-ec2`, `ls kit` lista os scripts. Se a pasta já existir, entre nela e use `git pull --ff-only` para atualizar uma cópia sem alterações locais.

**Verifique:** por que baixar o repositório no seu computador, sozinho, não inicia um serviço na EC2?

## 2.2. Iniciar o ambiente

**Onde:** terminal **A — EC2**, na pasta `~/pratica-rest-ec2`.

```bash
bash kit/iniciar-lab.sh
```

Execute como `ubuntu`; o script chama `sudo` quando necessário. Aguarde a conclusão. Ele instala pacotes, inicia a API e o banco, publica a página e a API por HTTP na porta 80. O endereço é obtido por IMDSv2, os metadados da própria EC2.

**Esperado ao final:** duas respostas de saúde com `{"status":"ok"}`, a URL terminada em `/painel.html`, o endereço para `baseUrl` e a localização das credenciais. Os pacotes podem levar alguns minutos na primeira execução.

Se aparecer uma mensagem de falha, pare nessa etapa. Para falha de descoberta de DNS/IP, copie o DNS ou o IPv4 público atual do console e execute:

```bash
bash kit/iniciar-lab.sh SEU_DNS_EC2
```

Se o Ubuntu da EC2 já tiver UFW ativo, consulte `sudo ufw status`. Antes de liberar o acesso web, preserve SSH:

```bash
# Somente se o UFW estiver ativo:
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx HTTP'
```

**Verifique:** quais serviços foram preparados pelo script? Qual componente recebe as chamadas na porta 80? Por que o backend usa `127.0.0.1:8000`?

## 2.3. Executar a validação básica

**Onde:** terminal **A — EC2**, na mesma pasta.

```bash
bash kit/validar-lab.sh
```

**Esperado:** cada linha apresenta método, caminho e status esperado/recebido, seguida de `OK`. A sequência inclui 200, 401, 201, 200, 200, 400, 404, 204 e 404. O script cria e remove um registro próprio de ensaio.

Uma chamada que espera 401 e recebe 401 está correta: o teste verifica o comportamento previsto, não se todas as chamadas retornam 200. A execução automática prepara o laboratório; os experimentos seguintes investigam o significado de cada resposta.

**Verifique:** por que o erro 401 é esperado em um desses testes? O `OK` obtido dentro da EC2 já comprova que seu computador consegue alcançá-la pela Internet?

**Se não passar:** anote a primeira linha diferente e siga [6. Diagnosticar](06-diagnosticar.md). Não comece os experimentos de escrita antes de recuperar saúde e autenticação.

## 2.4. Localizar endereço e identidades

**Onde:** terminal **A — EC2**, privado, fora das capturas do relatório.

```bash
cat ~/redes-lab.url
cat ~/chaves-redes/entrega-grupos.csv
```

O CSV tem cabeçalho `grupo,chave` e duas linhas. Use a chave da linha **g01** no trabalho principal. A linha **g02** representa outra identidade, usada para verificar autorização na mesma API. Não precisa trocar chaves com outra equipe. Cada EC2 gera valores aleatórios diferentes.

| Item | Finalidade |
| --- | --- |
| `chave-ec2.pem`, no seu computador | Autenticar seu acesso SSH à máquina. |
| Chave de g01/g02, no CSV da EC2 | Autenticar requisições HTTP em `X-API-Key`. |

**Verifique:** a chave SSH e a chave g01 têm a mesma finalidade? Qual delas deverá entrar no cabeçalho da requisição protegida?

Se já usava a versão HTTPS, atualize o clone com `git pull --ff-only` e execute novamente `iniciar-lab.sh`. O script passa a servir HTTP e preserva chaves e banco. Nos clientes, atualize `baseUrl` e a URL da página para `http://`.

Avance para [3. Acessar](03-acessar.md).
