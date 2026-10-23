# Estado da validação

Este registro distingue a revisão do roteiro dos ensaios de execução. Uma instrução pode estar documentada e revisada sem ter sido executada em todas as plataformas.

## Revisão das instruções — 23/10/2026

O percurso foi revisado para alunos de Engenharia de Controle e Automação com conhecimentos básicos de redes e pouca experiência em publicação de APIs. A revisão considera execução individual, sem distribuição docente de chaves ou intervenção no servidor.

| Ponto conferido | Ajuste aplicado |
| --- | --- |
| Local de execução | Cada bloco identifica computador do aluno, EC2, Postman, navegador ou console AWS. |
| Sistemas locais | Abas WSL, Ubuntu e macOS para download, chave, cópia e conferência do certificado. |
| Postman no Windows com WSL | Arquivos públicos copiados para Downloads do Windows; não se pressupõe acesso ao clone da EC2. |
| Valores a substituir | Marcadores definidos antes dos comandos; chave local recebe um nome comum. |
| Dependência entre ações | ID real salvo após POST; autorização e persistência testadas antes de excluir o item. |
| Operações HTTP | Método, caminho, autenticação, corpo e resultado esperados em cada experimento. |
| Confirmação da aprendizagem | Perguntas de verificação junto das ações, previsões e comprovação por GET. |
| Falhas e recuperação | Sequência de testes, resultado discriminante e passo de recuperação explícito. |
| Dependência de PDF | Retirada do percurso; toda a prática está nas páginas Markdown do repositório. |

## Execuções técnicas já realizadas

| Verificação | Resultado e alcance |
| --- | --- |
| Contrato da API | Seis casos unittest aprovados; cobrem CRUD, erros, autorização, persistência, CORS e proxy. |
| Validador com HTTPS | Executado contra Gunicorn em loopback; saúde, autenticação, criação, leitura, PATCH, PUT incompleto, isolamento e exclusão aprovados. |
| Dados de ensaio | Verificada a limpeza do item criado pelo validador e a ausência de chaves na saída. |
| Credenciais | Chaves distintas, arquivos privados e recusa de sobrescrita conferidos. |
| Certificado | Nome/IP corretos aceitos e incorretos rejeitados na verificação OpenSSL. |
| Scripts | Sintaxe Bash/Python conferida. |

## Verificações desta revisão da documentação

- Construção com `mkdocs build --strict` aprovada, com MkDocs 1.6.1 e Material 9.7.5.
- Abas **WSL/Ubuntu/macOS** acionadas em Chrome automatizado por Playwright: conteúdo correto visível, demais abas ocultas e seleção preservada ao mudar de página.
- Página de acesso conferida também com largura de 390 px, sem rolagem horizontal do documento.
- Exemplos JSON e sequência manual do roteiro conferidos contra a API pelo cliente de testes Flask, incluindo autorização e persistência ao reconstruir a aplicação.
- Contratos das 13 requisições da coleção conferidos com variáveis resolvidas pelo mesmo cliente de testes. Isso não equivale à execução no aplicativo Postman ou de seus scripts JavaScript.
- Links internos e âncoras das páginas geradas conferidos.

Essas verificações testam o conteúdo e a navegação da documentação; não demonstram que os comandos locais foram executados em um Mac ou em WSL real.

O registro original dessas execuções permanece em [VALIDACAO.txt no repositório](https://github.com/rafaelrezo/pratica-rest-ec2/blob/main/VALIDACAO.txt). As referências aos PDFs naquele arquivo descrevem uma entrega anterior, preservada como histórico.

## O que ainda precisa de ensaio

- Inicialização integral APT/systemd em **uma EC2 Ubuntu 24.04 real**, incluindo metadados IMDSv2, Security Group e DNS.
- Importação do certificado e execução da coleção no **Postman Desktop**.
- Execução do percurso em **WSL, Ubuntu e macOS reais**, incluindo os seletores de arquivos e confiança no navegador.
- Execução por aluno iniciante, para observar dúvidas que uma revisão documental não identifica.

Nenhum recurso pago AWS foi criado durante esta revisão. O teste HTTPS local não equivale a um ensaio completo de implantação na AWS.

## Como registrar um ensaio completo

Use a tabela abaixo ao executar o percurso no ambiente de destino. Registre os resultados efetivamente observados, sem credenciais.

| Sistema local e versões | Etapa | Resultado esperado | Resultado observado | Ajuste necessário |
| --- | --- | --- | --- | --- |
| WSL / Postman / navegador | 1–7 | Percurso concluído com as verificações | A preencher | A preencher |
| Ubuntu / Postman / navegador | 1–7 | Percurso concluído com as verificações | A preencher | A preencher |
| macOS / Postman / navegador | 1–7 | Percurso concluído com as verificações | A preencher | A preencher |

Inclua a data, o commit usado, a AMI e a região da EC2, o resultado dos scripts e os trechos que precisaram de adaptação. Isso permite ampliar a cobertura sem anunciar como testado um ambiente ainda não ensaiado.
