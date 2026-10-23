# 7. Registrar e encerrar

## 7.1. Conferir o que foi demonstrado

Antes de encerrar a instância, use a lista para organizar sua entrega:

- [ ] Registrei a URL e o resultado da validação automática, sem chaves.
- [ ] Executei POST/GET/PATCH/PUT/DELETE manualmente e confirmei os efeitos por GET.
- [ ] Expliquei as diferenças entre PUT/PATCH e entre 200/201/204/400/401/404/409/415/502 nos casos observados.
- [ ] Demonstrei autorização entre g01/g02 e persistência após reiniciar o backend.
- [ ] Executei as 13 requisições da coleção na ordem e interpretei seus testes.
- [ ] Usei a página e o Postman sobre o mesmo cadastro, com evidência de Network.
- [ ] Diagnostiquei uma falha, corrigi sua causa e comprovei a recuperação.

Não inclua `X-API-Key`, valores do CSV, chave SSH ou chave privada TLS nas capturas/arquivos de entrega.

## 7.2. Responder às perguntas de fechamento

1. Descreva o percurso de um clique em **Salvar**, do navegador até o banco e de volta à tela.
2. Como outro cliente poderia utilizar essa API? Quais informações do contrato precisaria conhecer?
3. Por que saúde 200, sozinha, não comprova autenticação, persistência ou funcionamento de todo o CRUD?
4. Por que o usuário do navegador consegue observar suas próprias requisições, mesmo usando HTTPS?
5. Qual teste distingue um erro de credencial de um backend parado? Quais foram suas evidências?

Entregue a tabela da investigação REST, o resultado da coleção, uma evidência da aplicação web e um registro de diagnóstico. Responda com suas observações e justificativas; apenas copiar as saídas do script não explica o funcionamento.

## 7.3. Limpar os cadastros e os clientes

1. Com g01, liste o inventário e exclua apenas os itens de ensaio que você criou. Confira por nova listagem.
2. Na página, clique **Esquecer chave** e feche-a.
3. Remova os segredos dos ambientes Postman que serão compartilhados ou usados por outras pessoas.
4. Remova o certificado didático importado no Postman e no navegador quando não for mais utilizar o laboratório. No Firefox, volte ao gerenciador de certificados da etapa de acesso e remova apenas o certificado deste laboratório.

**Verifique:** qual evidência confirma a remoção de um item? Por que limpar o campo da página não remove o cadastro no servidor?

## 7.4. Encerrar os recursos da equipe

1. Salve seu relatório e as evidências no seu computador. Os scripts já estão no repositório; não precisa copiá-los de volta da EC2.
2. No console AWS, selecione a instância pelo **ID e região anotados**. Se concluiu a prática, use **Estado da instância → Encerrar/Terminar instância** e confirme a instância correta.
3. Confira o estado encerrado e os volumes EBS, snapshots e endereços reservados eventualmente criados pela equipe. Remova apenas recursos seus e sem uso.
4. Pare de divulgar a URL antiga. Um IPv4 público liberado pode ser reutilizado por outra instância.

**Esperado:** evidências preservadas e recursos de laboratório sem uso encerrados. **Parar** a EC2 não equivale a **terminar** nem garante custo zero: armazenamento e outros recursos podem continuar cobrando.

**Verifique:** quais recursos ainda poderiam gerar cobrança depois que o processo da API fosse parado? Qual diferença entre parar o backend, reiniciar o serviço e terminar a EC2?
