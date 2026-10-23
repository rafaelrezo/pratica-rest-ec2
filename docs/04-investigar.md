# 4. Investigar REST

**Objetivo:** prever, executar e explicar o efeito de requisições sobre um recurso. Você trabalhará no **Postman do seu computador**, com g01, enquanto a API roda na EC2.

## Fundamentos: o que significa REST nesta prática?

**REST — Representational State Transfer — é um estilo de arquitetura** para organizar interações entre clientes e serviços. Neste laboratório, você observa essas interações por HTTP. REST não é uma linguagem de programação, um formato de arquivo ou um sinônimo de CRUD.

### Recursos e representações

O **recurso** é algo que a API identifica e permite consultar/manipular. Aqui, o cadastro de um equipamento é um recurso: `/api/equipamentos/7` identifica um item; `/api/equipamentos` identifica a coleção.

A **representação** é a descrição transferida na mensagem. O JSON com `id`, `nome`, `tipo`, `local` e `ativo` representa um cadastro. A página transforma essa representação em uma linha da tabela; o Postman exibe o JSON diretamente. REST não exige JSON: esse é o formato escolhido por este contrato.

### Princípios que você poderá observar

| Princípio | O que significa | Exemplo no kit |
| --- | --- | --- |
| Cliente e servidor | Interface e armazenamento têm responsabilidades distintas. | Postman/página enviam pedidos; a API mantém os cadastros. |
| Interface uniforme | Identificação de recursos, representações e mensagens permitem uma interação consistente. | URLs identificam coleção/item; método, cabeçalhos, corpo e status descrevem a operação. |
| Requisições sem estado de sessão | Cada requisição leva as informações necessárias à sua interpretação. | Toda chamada protegida envia sua chave; o servidor não depende de uma chamada anterior de login. |
| Cacheabilidade | A resposta informa se pode ser armazenada/reutilizada por caches. | O backend envia `Cache-Control: no-store`; a resposta não deve ser guardada em cache. Isso não impede o banco persistente. |
| Organização em camadas | Intermediários podem participar da comunicação. | O cliente fala com Nginx; o proxy encaminha para a aplicação. |

Essas ideias derivam da [definição original de REST de Roy Fielding](https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm). O estilo também admite envio de código ao cliente como restrição opcional. O kit é um CRUD didático inspirado em REST: ele não exercita a navegação por hipermídia, na qual links das representações orientam próximas ações, nem demonstra sozinho todas as restrições do estilo.

### Método HTTP, efeito e resposta são coisas distintas

| Método | Intenção neste contrato | O que observar ao repetir |
| --- | --- | --- |
| GET | Consultar uma representação. | Não cria ou altera o cadastro solicitado. |
| POST | Pedir a criação de um item na coleção. | Não suponha idempotência; neste kit, repetir o nome conflita com a regra de unicidade. |
| PUT | Substituir a representação editável de um item existente. | Repetir a mesma substituição mantém o mesmo efeito final. |
| PATCH | Aplicar uma alteração parcial. | A idempotência depende da operação: atribuir `ativo=false` difere de pedir para inverter o valor. |
| DELETE | Remover o item. | O efeito final continua sendo ausência, mesmo que os status de chamadas sucessivas sejam diferentes. |

**Idempotência** se refere ao efeito pretendido de repetir uma operação; não exige respostas idênticas. **Segurança do método**, na semântica HTTP, significa que o cliente não pede mudança de estado: GET é seguro; DELETE não é, mesmo sendo idempotente. Isso não é uma classificação de criptografia ou autenticação. [Semântica dos métodos na RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#name-method-definitions).

Um status responde a uma requisição delimitada: 201 indica criação; 204 indica sucesso sem conteúdo; 401 indica ausência de credencial válida; 404 pode indicar item indisponível naquele escopo. Para verificar o estado do cadastro após uma escrita, faça outra consulta GET.

**Verifique antes de executar:** onde está o recurso e onde aparece sua representação? A ausência de sessão impede persistir dados? Trocar HTTP por HTTPS mudaria os caminhos e as operações do contrato? No primeiro GET, procure `Cache-Control` nos cabeçalhos da resposta e relacione seu valor com a tabela acima.

??? note "Confira a ideia central"

    O recurso é mantido pelo servidor; JSON e tabela são formas de representá-lo. Chamadas sem sessão de usuário podem consultar um banco persistente. HTTPS acrescenta proteção ao transporte, enquanto o contrato de recursos, métodos e representações pode permanecer o mesmo.

## 4.1. Ler o contrato antes do primeiro cadastro

Um **recurso** é identificado por uma URL: `/api/equipamentos` é a coleção e `/api/equipamentos/7` é um item. JSON é a **representação** enviada ou recebida; HTTP define métodos e status. REST é um estilo de arquitetura. Este CRUD aplica parte de suas ideias; JSON e métodos HTTP, isoladamente, não demonstram todas as restrições de REST.

| Campo | Regra desta API |
| --- | --- |
| `id` | Gerado pelo servidor; não enviar no corpo. |
| `nome` | Texto de 1–80 caracteres após retirar espaços das pontas; único por identidade. |
| `tipo` | `sensor`, `clp`, `ihm`, `atuador` ou `outro`. |
| `local` | Texto de 1–80 caracteres. |
| `ativo` | Booleano JSON `true`/`false`, sem aspas. |

| Método | Caminho | Sucesso esperado |
| --- | --- | --- |
| GET | `/api/saude` | 200; sem chave. |
| GET | `/api/equipamentos` | 200; objeto com `itens` e `total`. |
| GET | `/api/equipamentos/{id}` | 200; representação do item. |
| POST | `/api/equipamentos` | 201; item criado e cabeçalho `Location`. |
| PATCH | `/api/equipamentos/{id}` | 200; item atualizado parcialmente. |
| PUT | `/api/equipamentos/{id}` | 200; representação editável substituída. |
| DELETE | `/api/equipamentos/{id}` | 204; sem corpo. |

As chamadas protegidas usam `X-API-Key`. POST e PUT exigem os quatro campos editáveis; PATCH aceita um ou mais. Campos desconhecidos são rejeitados. Use os caminhos sem barra final. Não há filtros, busca ou paginação e o corpo é limitado a 16 KiB.

**Verifique:** qual parte da URL identifica a coleção? Qual parte identifica um item? Em uma requisição, onde ficam método, credencial e JSON?

## 4.2. Fazer o primeiro GET manualmente

Para aprender as partes da requisição, crie agora uma **requisição nova, fora da coleção importada**. Use a coleção automática somente na etapa 4.12. Assim, os scripts da coleção não interferem na exploração manual.

1. Crie uma requisição HTTP pelo botão **New/Novo** ou **+** do Postman.
2. Selecione o método **GET**.
3. Na URL, coloque `{{baseUrl}}/api/saude`.
4. Em **Authorization**, selecione **No Auth**. Deixe **Body** vazio.
5. Clique **Send**. Observe status, cabeçalhos e corpo em abas separadas da resposta.

**Esperado:** 200 e `{"status":"ok"}`.

**Verifique:** quem é cliente e quem é servidor? Esse GET provou que você pode criar um cadastro ou apenas que a rota de saúde responde?

## 4.3. Distinguir saúde de autenticação

1. Na mesma requisição, altere apenas a URL para `{{baseUrl}}/api/equipamentos` e envie com **No Auth**.
2. Anote o status e a mensagem em `erro`.
3. Em **Authorization**, selecione **API Key**. Preencha **Key = `X-API-Key`**, **Value = `{{apiKey}}`** e **Add to = Header**.
4. Envie novamente para a mesma URL.

**Esperado:** primeiro 401; depois 200, com `{"itens":[],"total":0}` se g01 ainda não tiver registros. Se já existirem, `total` deverá corresponder à quantidade em `itens`.

Mantenha essa autenticação nas próximas requisições manuais. Se criar outra requisição fora da coleção, configure-a novamente. Na coleção importada, as protegidas usam **Inherit auth from parent** e os testes sem chave usam **No Auth** de propósito.

**Verifique:** o que mudou entre as duas chamadas? O 401 prova que o servidor está fora do ar? Por que a chave é enviada no cabeçalho em vez da URL?

**Se receber 401 com a chave:** confira ambiente selecionado, valor de g01, nome do cabeçalho e opção **Header**. Não cole o cabeçalho inteiro em `apiKey`; ela contém somente o segredo.

## 4.4. Criar um recurso por POST

Antes de enviar, preveja: haverá novo ID? Qual status deve voltar?

1. Selecione **POST** e URL `{{baseUrl}}/api/equipamentos`, mantendo a autenticação de g01.
2. Em **Body → raw → JSON**, cole:

    ```json
    {
      "nome": "CLP-A-01",
      "tipo": "clp",
      "local": "Planta A",
      "ativo": true
    }
    ```

3. Em **Headers**, confira `Content-Type: application/json`. O seletor JSON costuma adicioná-lo.
4. Envie. Observe o ID no corpo e `Location` nos cabeçalhos da **resposta**.
5. Copie o ID real para `equipamentoId` no ambiente selecionado. Salve/aplique a variável conforme a interface da sua versão. No teste manual, você faz isso; o script da coleção só será usado depois.

**Esperado:** 201 e um objeto com os quatro campos e `id`. O `Location` será `/api/equipamentos/ID_REAL`. Não presuma ID 1: a validação automática pode ter consumido IDs.

**Verifique:** por que não enviamos `id`? O que permite ao cliente descobrir onde está o recurso criado?

**Se retornar 409:** já existe esse nome em g01. Selecione outro nome, como `CLP-A-02`, envie e use o ID retornado. Preserve esse novo nome no PUT e no teste de duplicidade seguintes.

## 4.5. Consultar e conferir por GET

1. Selecione **GET** e URL `{{baseUrl}}/api/equipamentos/{{equipamentoId}}`. Se usar a mesma aba do POST, selecione **Body → none**.
2. Envie e compare o JSON recebido com o cadastrado.
3. Envie também GET `{{baseUrl}}/api/equipamentos` e localize o ID dentro de `itens`.
4. Volte ao POST da etapa anterior e reenvie o mesmo JSON, sem mudar o nome.

**Esperado:** GET do item 200; GET da coleção 200; POST repetido 409, sem criar um segundo item com o mesmo nome nessa identidade.

**Verifique:** por que repetir GET não cria um equipamento? Nesta API, por que repetir esse POST produz conflito? Uma requisição POST é sinônimo de “enviar qualquer coisa”?

**Se o GET retornar 404:** confira o ID salvo e a identidade selecionada. A existência de uma resposta HTTP 404 é diferente de um timeout.

## 4.6. Alterar parcialmente com PATCH

1. Selecione **PATCH**, URL `{{baseUrl}}/api/equipamentos/{{equipamentoId}}`.
2. Em **Body → raw → JSON**, use:

    ```json
    {"ativo": false}
    ```

3. Envie; depois faça GET do mesmo item, sem corpo.
4. Repita o mesmo PATCH e confira novamente por GET.

**Esperado:** PATCH e GET retornam 200; `ativo` é `false`, com nome, tipo e local preservados. Repetir a atribuição mantém o mesmo valor.

**Verifique:** que evidência demonstra alteração parcial? Por que esta atribuição pode ser idempotente? Isso significa que qualquer operação PATCH sempre será idempotente? A semântica depende da operação definida pelo contrato. [PATCH na RFC 5789](https://www.rfc-editor.org/rfc/rfc5789.html).

## 4.7. Comparar com PUT

1. Mantenha a URL do item e troque o método para **PUT**. Envie apenas `{"ativo":true}` como JSON.
2. Faça GET e confira se o registro foi alterado.
3. Agora envie PUT com **toda a representação editável**. Se criou outro nome, mantenha esse nome no corpo:

    ```json
    {
      "nome": "CLP-A-01",
      "tipo": "clp",
      "local": "Planta B",
      "ativo": true
    }
    ```

4. Faça outro GET e compare os campos.

**Esperado:** PUT incompleto 400 e item preservado; PUT completo 200; GET confirma `local = Planta B` e `ativo = true`. Neste contrato, PUT atualiza um item existente e retorna 404 para ID inexistente.

**Verifique:** por que foi necessário enviar nome, tipo e ativo quando o interesse era mudar o local? Qual diferença entre PUT e PATCH foi demonstrada? [Semântica HTTP na RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#name-put).

## 4.8. Testar autorização com g02

Use o item ainda existente de g01. **Não o exclua antes deste teste.**

1. Duplique o ambiente de g01 e dê à cópia o nome **Redes | g02**.
2. Mantenha o mesmo `baseUrl` e o mesmo `equipamentoId`; substitua **somente `apiKey`** pelo segredo da linha g02 do CSV.
3. Selecione **Redes | g02**. Na requisição manual, mantenha API Key `{{apiKey}}` e envie GET do ID de g01.
4. Envie PATCH desse ID com `{"ativo":false}`; depois DELETE do mesmo ID, com **Body → none**.
5. Selecione novamente o **ambiente original de g01** e faça GET do item.

**Esperado:** com g02, GET/PATCH/DELETE retornam 404. Com g01, GET volta a retornar 200 e o item continua intacto. A chave de g02 é válida; o item está fora de seu escopo. Um GET da coleção com g02 deve retornar 200, sem expor o item de g01.

**Verifique:** qual observação distingue uma chave inválida de uma chave válida sem acesso àquele item? Por que simplesmente conhecer o ID não deveria permitir alterar o cadastro?

## 4.9. Comprovar persistência

1. No Postman, com **g01**, faça GET do item e anote ID e campos.
2. No **terminal A — EC2**, execute:

    ```bash
    sudo systemctl restart redes-api
    sudo systemctl status redes-api --no-pager
    ```

3. Quando o serviço estiver `active (running)`, repita o GET no Postman. Se a primeira chamada coincidir com a inicialização, aguarde alguns segundos e repita.

**Esperado:** GET 200 e o mesmo registro. Os dados ficam em SQLite em disco; reiniciar o processo não apaga o banco.

**Verifique:** o armazenamento está no Postman, na página ou no servidor? Requisições sem sessão de usuário impedem que o servidor mantenha um banco de dados?

## 4.10. Excluir e confirmar o resultado

1. No Postman, com **g01**, selecione **DELETE**, URL do item e **Body → none**.
2. Envie e observe status e corpo.
3. Faça GET do mesmo ID.
4. Repita DELETE do mesmo ID.

**Esperado:** DELETE inicial 204 e corpo vazio; GET e DELETE seguintes 404. O item permanece ausente. Não tente interpretar o corpo vazio do 204 como JSON.

**Verifique:** a resposta diferente na segunda exclusão significa que o efeito final mudou? Por que uma interface que sempre exige JSON terá problema com 204?

## 4.11. Registrar as evidências

Preencha no relatório, sem chaves:

| Método e caminho | Corpo resumido | Status previsto | Status recebido | Efeito conferido por GET |
| --- | --- | --- | --- | --- |
| POST da coleção | Quatro campos | | | |
| GET do item | Sem corpo | | | |
| PATCH do item | Apenas ativo | | | |
| PUT incompleto | Apenas ativo | | | |
| PUT completo | Quatro campos | | | |
| GET do item com g02 | Sem corpo | | | |
| DELETE do item | Sem corpo | | | |

**Verifique:** sua evidência mostra somente um status ou também comprova a mudança esperada no recurso?

## 4.12. Executar a coleção pronta

Volte ao **ambiente de g01**. Agora abra as requisições importadas e execute-as em ordem, de 01 a 13, clicando **Send** e observando **Test Results**. Se seu aplicativo permitir, também pode usar **Run collection**. Não execute duas sequências simultaneamente no mesmo ambiente.

| Ordem | Operação | Status esperado |
| --- | --- | --- |
| 01 | Saúde sem chave | 200 |
| 02 | Listagem sem chave | 401 |
| 03 | Listagem de g01 | 200 |
| 04 | Criar, salvar ID e conferir Location | 201 |
| 05 | Consultar o ID | 200 |
| 06 | Repetir o nome | 409 |
| 07 | PATCH | 200 |
| 08 | PUT completo | 200 |
| 09 | POST incompleto | 400 |
| 10 | POST como text/plain | 415 |
| 11 | PUT na coleção sem ID | 405 |
| 12 | DELETE | 204 |
| 13 | GET do excluído | 404 |

O POST da coleção gera um nome com instante atual e salva o ID retornado em `equipamentoId`. Os testes usam o contrato desta API; a coleção não substitui sua explicação. Se rodar apenas um item isolado, pode faltar o recurso criado nos anteriores.

**Verifique:** por que testes que esperam 400, 401 ou 404 devem passar ao receber esses códigos? Qual pré-condição é quebrada se executar a consulta depois da exclusão esperando 200?

??? note "Depois dos experimentos, confira seu raciocínio"

    - POST na coleção cria um novo recurso; `id` e `Location` permitem localizá-lo. A regra de nome único explica o 409 na repetição desse cadastro.
    - GET consulta uma representação sem criar outro item. A listagem e a consulta por ID são recursos distintos.
    - PATCH mudou um campo. Neste contrato, PUT exige os quatro campos e o incompleto não deve alterar o recurso.
    - Atribuir `ativo=false` repetidamente tem o mesmo efeito final; PATCH também pode representar operações com outros efeitos. Não generalize a idempotência para qualquer PATCH.
    - g02 é uma identidade válida; o GET de sua coleção 200 junto do GET do item de g01 404 evidencia a restrição de escopo.
    - O banco permanece no servidor entre requisições e reinícios do processo. Isso é compatível com chamadas sem uma sessão de usuário.
    - DELETE 204 não contém JSON. Receber 404 ao repetir não muda o efeito final: o recurso continua ausente.

Avance para [5. Usar a aplicação web](05-aplicacao-web.md).
