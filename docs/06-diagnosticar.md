# 6. Diagnosticar

**Objetivo:** localizar uma falha a partir de evidências e comprovar a recuperação. Para cada caso, registre **sintoma → hipótese → teste → resultado → correção**. Ter recebido HTTP 400, por exemplo, é diferente de não receber resposta.

## 6.1. Recuperar o acesso SSH

Use este trecho apenas se não conseguir abrir o terminal A.

1. **Console AWS:** confira a região, se a instância está em execução e o DNS/IP público atual.
2. **Seu computador:** confira se `~/redes-rest/chave-ec2.pem` existe. O usuário do comando deve ser `ubuntu`.
3. **Timeout:** confira a entrada TCP 22 no Security Group para o seu IP público atual. Ao mudar de rede, a origem **Meu IP** pode precisar de atualização.
4. **Permission denied (publickey):** confira se o arquivo é do par de chaves selecionado na instância e se foi copiado com as permissões da etapa 1.
5. Reconecte com o comando SSH da [etapa 1](01-preparar.md#14-conectar-a-ec2), sem reiniciar ou recriar a máquina para testar.

**Verifique:** por que uma chave incorreta e uma porta bloqueada costumam produzir sintomas diferentes? O serviço REST precisa estar funcionando para abrir SSH?

## 6.2. Conferir o caminho antes das operações REST

Se o script de validação falhar ou nenhum cliente alcançar a API, execute os testes nesta ordem.

**Teste 1 — aplicação dentro da EC2. Terminal A:**

```bash
curl -i http://127.0.0.1:8000/api/saude
sudo systemctl status redes-api --no-pager
```

**Esperado:** 200, JSON de saúde e serviço `active (running)`. Se falhar, consulte `sudo journalctl -u redes-api -n 30 --no-pager`. Recupere o serviço com `sudo systemctl start redes-api` se estiver parado. Se houver erro de instalação/configuração, leia o primeiro erro do script antes de reexecutar o início.

**Teste 2 — Nginx HTTP dentro da EC2. Terminal A:**

```bash
sudo nginx -t
curl -i http://127.0.0.1/api/saude
```

Esse teste passa pelo Nginx da própria EC2, na porta 80. Espere configuração válida e 200. Se a aplicação responde no teste 1, mas o proxy falha, consulte:

```bash
sudo systemctl status nginx --no-pager
sudo tail -n 30 /var/log/nginx/error.log
```

**Teste 3 — acesso a partir do seu computador. Terminal B:**

```bash
curl -i http://SEU_DNS_EC2/api/saude
```

Espere 200. Se os testes 1 e 2 passam e este dá timeout, confira nome/IP atuais, entrada 80 para seu IP atual, caminho público e rede de origem. Se o endereço mudou, siga a etapa 6.6.

**Verifique:** o que cada teste acrescenta ao anterior? Um ping responde se a aplicação REST consegue criar um registro?

## 6.3. Provocar e corrigir 401

**Onde:** Postman, em uma requisição **manual**, com g01 selecionado.

1. Prepare GET `{{baseUrl}}/api/equipamentos`, com **Body → none**.
2. Em **Authorization**, selecione **No Auth** e envie.
3. Preveja o resultado e anote a resposta.
4. Restaure **API Key**, `X-API-Key`, `{{apiKey}}`, envio em **Header**. Envie de novo.

**Esperado:** sem credencial, 401; com g01 válida, 200. Não basta apagar uma linha de Headers se a autorização estiver sendo adicionada automaticamente pela aba Authorization.

**Verifique:** se você recebeu um JSON com status 401, quais partes do caminho já responderam? Abrir outra porta corrigiria a credencial ausente?

## 6.4. Distinguir corpo inválido de formato incorreto

**Onde:** Postman, com g01 e autenticação ativa. A URL é `{{baseUrl}}/api/equipamentos`.

1. Selecione **POST → Body → raw → JSON**. Envie `{"nome":"Incompleto"}`.
2. Espere **400**: o JSON é sintaticamente válido, mas faltam campos exigidos.
3. Em **Body → raw**, mude o seletor de **JSON** para **Text**. Em Headers, confirme que o `Content-Type` efetivo é **`text/plain`**, sem uma segunda linha conflitante. Envie `isto nao e JSON`.
4. Espere **415**: esse formato de corpo não é aceito pela rota.
5. Para recuperar, volte a **raw → JSON** e ao `Content-Type: application/json`; use os quatro campos da [etapa de criação](04-investigar.md#44-criar-um-recurso-por-post), com um nome novo.
6. Espere **201**, anote o ID e exclua somente esse registro de ensaio com g01. DELETE deve retornar 204.

**Verifique:** qual a diferença entre “JSON incompleto” e “formato não aceito”? Por que o cliente precisa conhecer o contrato, além de alcançar a porta 80?

## 6.5. Provocar e recuperar 502

**Onde:** somente na EC2 dedicada da sua equipe e nos clientes dessa instância. O teste para apenas o backend; mantenha a sessão SSH aberta.

1. Confirme saúde externa 200 no Postman ou no terminal B.
2. No **terminal A — EC2**, execute:

    ```bash
    sudo systemctl stop redes-api
    ```

3. Repita o GET externo `/api/saude`. Abra também a página inicial `/` da EC2 no navegador, com recarga.
4. No terminal A, execute `curl -i http://127.0.0.1:8000/api/saude`.
5. Explique a diferença entre a página estática responder e o endpoint da API falhar.
6. **Recupere o serviço antes de continuar:**

    ```bash
    sudo systemctl start redes-api
    sudo systemctl status redes-api --no-pager
    ```

7. Aguarde `active (running)`, repita o GET externo e confirme 200. Na pasta `~/pratica-rest-ec2`, execute `bash kit/validar-lab.sh` e confirme `OK`.

**Esperado:** enquanto o backend estiver parado, o Nginx retorna **502** para a API, a página estática continua disponível e o acesso direto a 8000 falha. Após iniciar, a saúde volta a 200. A resposta de erro 502 pode estar em HTML, diferente dos erros JSON da aplicação.

**Verifique:** quem produziu o 502? Por que trocar a chave da API não resolveria? Qual observação confirmou a recuperação completa do serviço?

Se o teste for interrompido no meio, reconecte e execute primeiro `sudo systemctl start redes-api` para recuperar o ambiente.

## 6.6. Corrigir mudança de endereço

1. No console, confira o DNS e o IPv4 públicos atuais da instância. Depois de **parar/iniciar**, eles podem mudar.
2. Se mudaram, reconecte pelo novo endereço e execute `bash kit/iniciar-lab.sh` dentro de `~/pratica-rest-ec2`. A URL em `~/redes-lab.url` será atualizada.
3. Atualize `baseUrl` nos dois ambientes Postman para `http://NOVO_ENDERECO`, sem `/api`. Abra a página pelo novo endereço e mantenha `/api` no campo da interface.
4. Confira se o Security Group permite TCP 80 a partir do IP atual do seu computador.
5. Repita saúde HTTP e listagem autenticada.

**Esperado:** saúde 200 e listagem 200. Banco e chaves permanecem ao repetir o script; a página de referência é republicada.

**Verifique:** quais valores mudaram no cliente? Por que essa mudança de endereço não exige criar novamente os cadastros?

## 6.7. Se apenas o navegador falhar

1. Confirme no Postman que saúde e listagem com g01 respondem.
2. Confira se a página está em `http://SEU_DNS_EC2/painel.html`, e não `file://` ou uma prévia em outro domínio.
3. Mantenha o campo **URL base da API = `/api`** e use a chave de g01.
4. Abra **Console** e **Network** no navegador; clique **Conectar / listar** e procure a requisição da API.
5. Se não houver chamada e a página pedir uma chave, preencha o campo. Se houver resposta 401, confira a chave. Se o navegador tentar forçar HTTPS, use HTTP para o endereço deste laboratório. Se houver origem externa/OPTIONS rejeitado, volte à página publicada na própria EC2, que é o caminho desta prática.

**Esperado:** GET 200 e listagem na tela. Não exponha a porta 8000 nem desative a segurança do navegador para contornar esse problema.

**Verifique:** por que uma resposta HTTP de erro e um bloqueio antes de receber HTTP exigem diagnósticos diferentes?

??? note "Depois de recuperar os serviços, confira seu raciocínio"

    - No 401 com JSON, o caminho até a aplicação funcionou; ela rejeitou a credencial. A correção é restaurar a autenticação correta.
    - No 400/415, a requisição chegou, mas conteúdo ou formato não atende ao contrato. Abrir portas não corrige o JSON.
    - No 502 provocado, o Nginx estava disponível e não conseguiu falar com o backend parado. A página estática não depende desse processo para ser servida.
    - Um teste local bem-sucedido não comprova, sozinho, regras e conectividade externas. Por isso os três pontos de teste são complementares.
    - A recuperação precisa de nova evidência: saúde 200 e operação autenticada/validação concluída, além de serviço ativo.

Avance para [7. Registrar e encerrar](07-encerrar.md).
