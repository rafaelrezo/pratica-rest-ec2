# 3. Acessar

**Objetivo:** alcançar sua API a partir do seu computador e preparar Postman e navegador. Deixe o terminal **A — EC2** aberto e use o terminal **B — seu computador** para os comandos locais.

## 3.1. Conferir o certificado no servidor

**Onde:** terminal **A — EC2**.

```bash
sha256sum ~/redes.crt
openssl x509 -in ~/redes.crt -noout -dates -ext subjectAltName
```

Anote o hash SHA-256 de 64 caracteres da primeira saída. A segunda deve apresentar validade de sete dias e o DNS/IPv4 públicos atuais no SAN. Nesta comparação usamos o **hash do arquivo**, não a impressão digital exibida pelo navegador.

**Verifique:** o nome da URL está no SAN? Por que um certificado para outro nome não serve, mesmo que o servidor responda?

## 3.2. Copiar e conferir no seu computador

**Onde:** terminal **B — seu computador**, sem SSH ativo. Substitua `SEU_DNS_EC2` em sua aba.

=== "WSL"

    No terminal Ubuntu/WSL:

    ```bash
    scp -i ~/redes-rest/chave-ec2.pem ubuntu@SEU_DNS_EC2:~/redes.crt ~/redes-rest/redes.crt
    sha256sum ~/redes-rest/redes.crt
    ```

    Compare o hash com o anotado no servidor. Em seguida, copie os arquivos públicos para uma pasta que o **Postman e o navegador do Windows** possam abrir. Substitua `SEU_USUARIO_WINDOWS`:

    ```bash
    mkdir -p "/mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads/redes-rest"
    cp ~/redes-rest/redes.crt "/mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads/redes-rest/"
    cp ~/redes-rest/pratica-rest-ec2/kit/postman/*.json "/mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads/redes-rest/"
    ```

    Nos seletores de arquivo dos aplicativos Windows, use `Downloads\redes-rest`. Essa pasta contém o certificado público e os dois JSON, sem a chave SSH.

=== "Ubuntu"

    No Terminal do seu computador Ubuntu:

    ```bash
    scp -i ~/redes-rest/chave-ec2.pem ubuntu@SEU_DNS_EC2:~/redes.crt ~/redes-rest/redes.crt
    sha256sum ~/redes-rest/redes.crt
    ```

    Compare o hash com o anotado no servidor. O certificado está em `/home/SEU_USUARIO/redes-rest/redes.crt`; os dois JSON estão em `redes-rest/pratica-rest-ec2/kit/postman` dentro da sua pasta pessoal. No seletor de arquivos, `Ctrl+L` permite informar o caminho completo.

=== "macOS"

    No Terminal do seu Mac:

    ```bash
    scp -i ~/redes-rest/chave-ec2.pem ubuntu@SEU_DNS_EC2:~/redes.crt ~/redes-rest/redes.crt
    shasum -a 256 ~/redes-rest/redes.crt
    ```

    Compare o hash com o anotado no servidor. O certificado está em `/Users/SEU_USUARIO/redes-rest/redes.crt`; os dois JSON estão em `redes-rest/pratica-rest-ec2/kit/postman` dentro da sua pasta pessoal. No seletor de arquivos, `Command+Shift+G` permite informar o caminho da pasta.

**Esperado:** os dois hashes são iguais, desconsiderando o nome/caminho do arquivo na saída. Se forem diferentes, confira o servidor e repita a cópia antes de importar o certificado.

**Verifique:** por que a cópia foi feita pelo SSH verificado? Por que não copiamos `redes.key`?

## 3.3. Testar HTTPS a partir do seu computador

**Onde:** terminal **B — seu computador**, igual nas três plataformas.

```bash
curl --cacert ~/redes-rest/redes.crt -i https://SEU_DNS_EC2/api/saude
```

**Esperado:** status 200 e JSON `{"status":"ok"}`. O `--cacert` usa seu certificado didático para validar a conexão, mantendo a verificação de nome e validade.

**Verifique:** esse teste atravessa qual caminho que ainda não tinha sido comprovado pelo script dentro da EC2? O resultado testa sua chave de g01?

**Se falhar:** timeout indica conferir DNS, rede e porta 443; erro de certificado exige conferir o arquivo, SAN e data. Não use `curl -k` para obter a evidência pedida. Siga a [sequência de diagnóstico](06-diagnosticar.md#62-conferir-o-caminho-antes-das-operacoes-rest).

## 3.4. Preparar a confiança no Postman

**Onde:** aplicativo **Postman Desktop no seu computador**. Quem usa WSL pode usar o Postman instalado no Windows.

1. Abra **Settings/Configurações → Certificates/Certificados**. Em algumas versões, o caminho começa em **Settings → App settings**.
2. Na seção **CA certificates**, habilite a opção e selecione o arquivo **`redes.crt` local** da etapa 3.2.
3. Mantenha **SSL certificate verification** ligada nas configurações de requisição.

O arquivo vai em **CA certificates**, e não em **Add client certificate**. O laboratório usa certificado de servidor e chave da API; não usa certificado de cliente/mTLS. [Referência oficial do Postman](https://learning.postman.com/docs/use/send-requests/authorization/certificates/).

**Verifique:** por que configurar confiança TLS no Postman não substitui o cabeçalho `X-API-Key`?

## 3.5. Importar os arquivos e selecionar o ambiente

**Onde:** Postman Desktop.

1. Clique em **Import** e selecione **`redes-crud.postman_collection.json`** na pasta local indicada na sua aba da etapa 3.2.
2. Importe também **`redes.postman_environment.json`**. O primeiro arquivo define requisições; o segundo define variáveis.
3. Em **Environments/Ambientes**, abra **Redes | preencher localmente** e preencha:

    | Variável | Valor |
    | --- | --- |
    | `baseUrl` | `https://SEU_DNS_EC2`, com o nome real, sem `/api` e sem barra final. |
    | `apiKey` | Somente o valor da chave da linha **g01** do CSV; sem `g01,`, aspas ou espaços. |
    | `equipamentoId` | Vazio por enquanto. |

4. Guarde a chave como valor local/privado ou em Vault, conforme os recursos disponíveis. Não exporte nem compartilhe um ambiente preenchido. O tipo `secret` oculta a exibição, mas não garante sozinho que o valor não seja sincronizado.
5. **Selecione esse ambiente** no seletor do Postman. Preencher o ambiente sem selecioná-lo não ativa as variáveis.
6. Abra a requisição **01 Saúde (sem chave)** da coleção e clique **Send/Enviar**.

**Esperado:** 200 e `{"status":"ok"}`. A URL deve apontar para o DNS real e conter `/api/saude` uma única vez. Se `{{baseUrl}}` continuar sem resolução, confira o ambiente selecionado.

**Verifique:** qual a diferença entre uma coleção e um ambiente? Por que não incluímos `/api` em `baseUrl`?

## 3.6. Abrir a página web

**Onde:** navegador no seu computador. No WSL, use o navegador do Windows.

1. Abra `https://SEU_DNS_EC2/painel.html` com seu DNS real.
2. Como o certificado é autoassinado, o navegador pode mostrar um aviso. Depois de conferir o arquivo e o nome nas etapas anteriores, estabeleça a confiança para esse laboratório. O Postman e o navegador têm configurações de confiança próprias.
3. Para uma sequência reproduzível, no **Firefox** abra **Configurações → Privacidade e Segurança**, procure **Certificados**, clique **Ver certificados → Autoridades → Importar** e selecione seu `redes.crt`. Confirme a confiança para identificar sites e recarregue a página. O certificado didático foi criado para permitir esse uso.
4. Como alternativa, se o Firefox oferecer **Avançado → Aceitar o risco e continuar/Prosseguir**, a exceção pode ser usada somente para o endereço e certificado do seu laboratório já conferidos. A opção pode não existir em um navegador gerenciado; nesse caso use a importação anterior se permitida. Os [avisos e limites são descritos pela Mozilla](https://support.mozilla.org/pt-BR/kb/o-que-significam-os-codigos-de-alerta-de-seguranca).
5. Na página, mantenha **URL base da API = `/api`**, informe somente a chave de **g01** no campo de senha e clique **Conectar / listar**.

**Esperado:** mensagem **Conectado** e a lista de equipamentos dessa identidade. Pode estar vazia. Não abra `painel.html` pelo gerenciador de arquivos com `file://`.

**Verifique:** por que o Postman usa `https://SEU_DNS_EC2` em `baseUrl`, mas a página usa `/api`? Qual componente entrega o HTML e encaminha as chamadas à API?

??? note "Depois de responder, confira seu raciocínio"

    - O certificado identifica o servidor HTTPS; a chave g01 autoriza chamadas à API. Uma condição não substitui a outra.
    - Saúde externa 200 comprova acesso pela rede, TLS, proxy e rota de saúde; ainda não comprova uma operação de banco autenticada.
    - O Postman monta a URL com `baseUrl` mais `/api/...`. A página já está na EC2 e usa `/api` relativo à sua origem.
    - Selecionar o ambiente ativa suas variáveis; importar uma coleção sozinho não preenche a chave da equipe.

Se saúde, ambiente e página estiverem prontos, avance para [4. Investigar REST](04-investigar.md).
