# 3. Acessar

**Objetivo:** alcançar sua API por HTTP e preparar Postman e navegador. Não há certificado para gerar, copiar ou importar nesta prática. Deixe o terminal **A — EC2** aberto e use o terminal **B — seu computador** para comandos locais.

## 3.1. Conferir a URL e testar o acesso

1. No **terminal A — EC2**, execute `cat ~/redes-lab.url` e copie a URL completa, iniciada por `http://`.
2. No **terminal B — seu computador**, substitua o DNS no comando abaixo. Ele é igual para WSL, Ubuntu e macOS:

    ```bash
    curl -i http://SEU_DNS_EC2/api/saude
    ```

3. Observe o status e o corpo da resposta. Se a URL gerada usar um IPv4 público, use esse mesmo IP no lugar do DNS.

**Esperado:** status 200 e JSON `{"status":"ok"}`. Esse teste parte do seu computador e atravessa a rede até o Nginx e a aplicação.

**Verifique:** o teste local do script já provava esse caminho externo? A rota de saúde usa a chave de g01 ou apenas confirma que a aplicação responde?

**Se falhar:** confira o esquema **`http://`**, o endereço atual e a entrada TCP **80** para seu IP no Security Group. Para localizar a falha, siga a [sequência de diagnóstico](06-diagnosticar.md#62-conferir-o-caminho-antes-das-operacoes-rest).

## 3.2. Localizar os arquivos do Postman

**Onde:** seu computador. O repositório já foi baixado na etapa 1; use sua aba para localizar os dois JSON.

=== "WSL"

    Se usa Postman no **Windows**, copie os JSON do clone no WSL para Downloads. No terminal Ubuntu/WSL, substitua `SEU_USUARIO_WINDOWS`:

    ```bash
    mkdir -p "/mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads/redes-rest"
    cp ~/redes-rest/pratica-rest-ec2/kit/postman/*.json "/mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads/redes-rest/"
    ```

    Nos seletores de arquivo dos aplicativos Windows, use `Downloads\redes-rest`. A pasta contém a coleção e o ambiente, sem a chave SSH.

=== "Ubuntu"

    No Terminal do seu computador Ubuntu, confira:

    ```bash
    ls ~/redes-rest/pratica-rest-ec2/kit/postman
    ```

    No seletor de arquivos do Postman, abra `redes-rest/pratica-rest-ec2/kit/postman` dentro da sua pasta pessoal. `Ctrl+L` permite informar o caminho completo, começando por `/home/SEU_USUARIO/`.

=== "macOS"

    No Terminal do seu Mac, confira:

    ```bash
    ls ~/redes-rest/pratica-rest-ec2/kit/postman
    ```

    No seletor de arquivos do Postman, use `Command+Shift+G` e informe `~/redes-rest/pratica-rest-ec2/kit/postman`. A pasta fica dentro de `/Users/SEU_USUARIO/`.

**Esperado:** arquivos `redes-crud.postman_collection.json` e `redes.postman_environment.json` disponíveis no seu computador.

**Verifique:** esses arquivos contêm cadastros ou definem requisições e variáveis? Por que tê-los apenas na EC2 não basta para importá-los no Postman local?

## 3.3. Importar e selecionar o ambiente

**Onde:** Postman Desktop no seu computador. No WSL, pode ser o aplicativo instalado no Windows.

1. Clique **Import** e selecione **`redes-crud.postman_collection.json`** na pasta da etapa anterior.
2. Importe também **`redes.postman_environment.json`**. A coleção define requisições; o ambiente define variáveis.
3. Em **Environments/Ambientes**, abra **Redes | preencher localmente** e preencha:

    | Variável | Valor |
    | --- | --- |
    | `baseUrl` | `http://SEU_DNS_EC2`, com o endereço real, sem `/api` e sem barra final. |
    | `apiKey` | Somente a chave da linha **g01** de `~/chaves-redes/entrega-grupos.csv`, consultada no terminal A; sem `g01,`, aspas ou espaços. |
    | `equipamentoId` | Vazio por enquanto. |

4. Guarde a chave como valor local/privado ou em Vault, conforme a versão. Não compartilhe ambientes preenchidos. O tipo `secret` oculta a exibição; não garante sozinho que o valor não seja sincronizado.
5. **Selecione esse ambiente** no seletor do Postman. Preencher sem selecionar não ativa as variáveis.
6. Abra a requisição **01 Saúde (sem chave)** da coleção e clique **Send/Enviar**.

**Esperado:** 200 e `{"status":"ok"}`. A URL resolvida deve começar com **`http://`** e conter `/api/saude` uma única vez. Não é preciso alterar configurações de certificado no Postman.

**Verifique:** qual a diferença entre coleção e ambiente? Por que `/api` não faz parte de `baseUrl` neste kit?

## 3.4. Conferir uma chamada autenticada

1. Abra **03 Listar meu grupo** na coleção importada.
2. Confira **Authorization → Inherit auth from parent**: a coleção adiciona `X-API-Key` a partir de `{{apiKey}}`.
3. Clique **Send** e observe status e corpo.

**Esperado:** 200, com `itens` e `total`. Se vier 401, confira o ambiente selecionado e o valor de g01. Essa etapa testa a chave; saúde 200, sozinha, não a testava.

**Verifique:** que informação foi acrescentada à requisição protegida? Uma chave no cabeçalho cifra a comunicação?

## 3.5. Abrir a página web

**Onde:** navegador no seu computador. No WSL, use o navegador do Windows.

1. Abra explicitamente **`http://SEU_DNS_EC2/painel.html`**, com o endereço real.
2. Mantenha **URL base da API = `/api`**. Não use o endereço interno `127.0.0.1:8000`.
3. Informe somente a chave de **g01** no campo de senha.
4. Clique **Conectar / listar**.

**Esperado:** mensagem **Conectado** e a lista dessa identidade, possivelmente vazia. Abra a página publicada na EC2, não o arquivo local por `file://`.

**Verifique:** por que a página usa `/api` relativo à sua origem? Qual componente entrega o HTML e encaminha as chamadas à API?

Se o navegador tentar mudar automaticamente para HTTPS, confira a URL e permita HTTP apenas para o endereço deste laboratório, conforme as opções do navegador. O roteiro usa dados e chaves exclusivamente didáticos e não exige HTTPS; não altere verificações TLS do Postman.

??? note "Depois de responder, confira seu raciocínio"

    - Saúde externa 200 confirma o caminho de rede, proxy e rota de saúde; a listagem autenticada também verifica a chave.
    - O Postman monta a URL com `baseUrl` mais `/api/...`. A página está na EC2 e usa `/api` relativo ao próprio endereço.
    - HTTP não cifra os dados. A chave serve ao exercício de autenticação e autorização, mas não fornece criptografia.
    - Selecionar o ambiente ativa suas variáveis; importar uma coleção sozinho não preenche a chave da equipe.

Se saúde, ambiente e página estiverem prontos, avance para [4. Investigar REST](04-investigar.md).
