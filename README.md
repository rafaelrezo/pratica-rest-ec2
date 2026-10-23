# Prática REST na EC2

**[Abrir a prática completa, com abas WSL, Ubuntu e macOS](https://rafaelrezo.github.io/pratica-rest-ec2/)**

Inicie uma API e uma aplicação web prontas e investigue recursos, métodos HTTP, JSON, status, persistência e autorização. Postman e navegador utilizam o mesmo inventário fictício das Plantas A/B/C. Não é necessário programar para realizar a prática.

Todo o roteiro está neste repositório, em Markdown, e é publicado automaticamente como documentação navegável. A prática pode ser concluída sem abrir PDF. Os arquivos PDF/LaTeX da entrega inicial permanecem como histórico.

O percurso principal usa **HTTP, sem configuração de certificados**. Trabalhe somente com dados/chaves didáticos e permita a porta 80 apenas para seu IP ou rede autorizada. HTTPS fica como aprofundamento opcional; REST não depende de configurar TLS.

## Percurso do aluno

| Etapa | O que você fará | Fonte no repositório |
| --- | --- | --- |
| Comece aqui | Objetivos, locais de execução e pré-requisitos. | [Introdução](docs/index.md) |
| 1. Preparar e conectar | Preparar a EC2, baixar os arquivos no seu computador e abrir SSH. | [Preparação](docs/01-preparar.md) |
| 2. Iniciar na EC2 | Executar os scripts prontos e localizar as credenciais geradas. | [Inicialização](docs/02-iniciar.md) |
| 3. Acessar | Testar HTTP, importar JSON e configurar Postman/navegador. | [Acesso](docs/03-acessar.md) |
| 4. Investigar REST | Prever e executar GET/POST/PATCH/PUT/DELETE e comprovar os efeitos. | [Experimentos REST](docs/04-investigar.md) |
| 5. Usar a aplicação web | Relacionar cada clique a uma requisição da mesma API. | [Aplicação web](docs/05-aplicacao-web.md) |
| 6. Diagnosticar | Provocar falhas delimitadas, localizar causas e recuperar o serviço. | [Diagnóstico](docs/06-diagnosticar.md) |
| 7. Registrar e encerrar | Salvar evidências e encerrar os recursos da equipe. | [Encerramento](docs/07-encerrar.md) |

Cada etapa informa **onde executar**, **o que fazer**, **qual resultado esperar** e **perguntas para verificar a compreensão**. As abas por sistema funcionam no [site da documentação](https://rafaelrezo.github.io/pratica-rest-ec2/); na visualização Markdown do GitHub aparece a sintaxe dessas abas.

## Início rápido

Se já concluiu os pré-requisitos e está **conectado por SSH à sua EC2 Ubuntu 24.04, como `ubuntu`**:

```bash
cd ~
sudo apt update
sudo apt install -y git
git clone https://github.com/rafaelrezo/pratica-rest-ec2.git
cd ~/pratica-rest-ec2
bash kit/iniciar-lab.sh
bash kit/validar-lab.sh
```

Se a pasta já existir, entre nela e use `git pull --ff-only` em uma cópia sem alterações locais. O início descobre DNS/IPv4 via IMDSv2 e gera g01/g02 automaticamente. Se a descoberta estiver desabilitada, aceita `bash kit/iniciar-lab.sh SEU_DNS_EC2` com o DNS ou o IPv4 público real.

Para começar do zero e usar Postman no seu computador, siga a [etapa 1 da documentação](https://rafaelrezo.github.io/pratica-rest-ec2/01-preparar/). Os comandos acima iniciam o serviço; a investigação REST vem nas etapas seguintes.

## Validação e revisão

A API e o validador têm testes locais registrados. **Ainda falta ensaio integral em uma EC2 real e nas três plataformas locais.** Consulte o [estado da validação](https://rafaelrezo.github.io/pratica-rest-ec2/validacao/) e o [registro em Markdown](docs/validacao.md), que distinguem revisão documental, testes executados e ensaios pendentes.

A [revisão didática](REVISAO-DIDATICA.md) registra as ambiguidades encontradas e os ajustes de sequência, localização dos comandos e perguntas de verificação.

## Arquivos prontos

| Arquivo/pasta | Função |
| --- | --- |
| `kit/iniciar-lab.sh` | Prepara e inicia a aplicação na EC2 dedicada. |
| `kit/validar-lab.sh` | Faz a validação básica sem digitar credenciais. |
| `kit/api/` | API Flask/Gunicorn e geração de credenciais locais. |
| `kit/config/` | Nginx HTTP e unidade systemd. |
| `kit/site/` | Portal e cliente web prontos. |
| `kit/postman/` | Coleção de 13 requisições e ambiente sem chave preenchida. |
| `docs/` | Roteiro completo, perguntas e registro de validação. |

O script mantém banco e chaves ao repetir a inicialização e republica a página de referência. Credenciais e banco gerados ficam fora do repositório. Os detalhes de acesso e encerramento estão no roteiro.

## Manter esta documentação

Edite os arquivos de `docs/`. Ao enviar alterações à branch `main`, o workflow publica o site com as abas. Os alunos não precisam instalar ferramentas de documentação.

Para uma prévia local, em um ambiente Python de manutenção:

```bash
python3 -m venv .venv-docs
.venv-docs/bin/pip install -r requirements-docs.txt
.venv-docs/bin/mkdocs serve
```

O comando mostra o endereço local da prévia. Para conferir links e a construção antes de publicar, use `.venv-docs/bin/mkdocs build --strict`.
