## Cognitive Load Analysis

### Task Summary

Estudantes de graduação, com redes básicas e iniciantes em APIs, iniciam um kit pronto na EC2 e investigam REST pelo Postman e pelo navegador. A revisão considera leitura autônoma, sem execução observada por alunos.

### Load Breakdown

**Intrinsic Load: Medium**

- Aproximadamente seis elementos interagem em uma chamada protegida: ambiente/identidade, método, URL/ID, cabeçalhos, corpo e interpretação do resultado.
- Relacionar recurso, representação e persistência exige comparação entre chamadas; essa dificuldade é parte do objetivo.

**Extraneous Load: High no roteiro inicial; reduzida na revisão**

- Atenção dividida entre README e PDF para concluir o contrato e os experimentos.
- Mudança entre terminal local e SSH sem localização explícita em todos os passos.
- Arquivos disponíveis no servidor, mas necessários no Postman local; dificuldade adicional para quem usa WSL com aplicativos Windows.
- Várias escolhas implícitas: ambiente ativo, autenticação herdada, ID real e tratamento de resposta vazia.

**Germane Load: High no roteiro revisado**

- Prever status e efeitos, confirmar por GET e explicar diferenças entre requisições.
- Relacionar ações da página ao contrato e ao armazenamento comum.
- Diagnosticar por evidência, testar a hipótese e comprovar recuperação.

### Overall Assessment

O conteúdo mantém sua exigência conceitual; a preparação de infraestrutura fica nos scripts. O roteiro segmentado apresenta uma decisão operacional por vez e oferece pontos de parada. A carga real depende do conhecimento dos alunos e deve ser observada em ensaio.

### Problem Areas

1. Fontes separadas exigiam procurar o próximo passo no PDF.
2. Três plataformas locais e duas máquinas podiam ser confundidas.
3. Requisições subsequentes dependiam de estados e IDs não suficientemente explicitados.
4. Erros eram listados sem uma sequência completa de correção.

### Modification Suggestions

- **Problem:** Atenção dividida entre documentos.
- **Principle:** Split-attention.
- **Fix:** Roteiro completo em Markdown, com navegação por etapas e sem dependência de PDF.

- **Problem:** Local e plataforma implícitos.
- **Principle:** Redução de busca e integração desnecessárias.
- **Fix:** Terminais A/EC2 e B/local, abas vinculadas WSL/Ubuntu/macOS e transferência explícita dos JSON para os aplicativos locais.

- **Problem:** Estado das requisições invisível para o iniciante.
- **Principle:** Exemplo guiado seguido de retirada gradual de apoio.
- **Fix:** Primeiro GET detalhado; depois previsão, execução e comparação. Salvar ID real, configurar autenticação e adiar DELETE até concluir isolamento/persistência.

- **Problem:** Diagnóstico sem recuperação explícita.
- **Principle:** Segmentação e autoexplicação.
- **Fix:** Cada experimento identifica ação, resultado, pergunta e recuperação; a falha 502 termina com reinício e validação do serviço.

### Expertise Reversal Check

Os apoios atendem iniciantes. Quem já domina SSH e Postman pode usar os checkpoints para avançar, preservando as perguntas conceituais e a produção de evidências. Não é necessário repetir conteúdo de todas as abas: cada aluno seleciona seu sistema. A revisão não substitui observação de uso real nem ensaios nas três plataformas.

### Ajuste de escopo: HTTP e fundamentos de REST

O professor retirou certificados do percurso principal para concentrar o esforço em REST. O início passa a publicar HTTP, a etapa de acesso mantém somente URL, JSON e credenciais didáticas e o diagnóstico deixa de exigir SAN/importação de certificados. O uso fica delimitado a dados fictícios, com entrada 80 restrita à origem do laboratório. Os fundamentos de REST precedem os experimentos e o diagrama da arquitetura passa a ser renderizado em Mermaid.
