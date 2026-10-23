# 1. Preparar e conectar

**Objetivo:** obter os arquivos no seu computador e abrir uma sessão SSH na EC2. Nesta etapa, a aplicação ainda não foi iniciada.

## 1.1. Conferir ou criar a EC2

**Onde:** console AWS, no navegador.

Se reutilizar a EC2 da prática 1, confira os itens abaixo. Se criar outra, siga a sequência:

1. Abra **EC2 → Instâncias → Executar instância** na região autorizada da sua conta.
2. Identifique a instância, por exemplo `redes-rest-equipe01`. Escolha uma imagem oficial **Ubuntu Server 24.04 LTS, Canonical, x86_64** e um tipo pequeno permitido pela conta, como `t3.micro`.
3. Em **Par de chaves**, selecione uma chave cuja parte privada você possui ou crie uma no formato `.pem` e baixe-a no seu computador. Esse arquivo será usado no SSH.
4. Use uma VPC e uma sub-rede com acesso público: rota `0.0.0.0/0` para Internet Gateway, IPv4 público atribuído à instância e DNS público disponível. A VPC padrão, quando disponível e com essa configuração, atende ao laboratório. A opção de atribuição automática de IP público deve estar habilitada.
5. Configure um **Security Group dedicado** com as entradas da tabela. Mantenha a saída necessária para DNS e download dos pacotes.
6. Use um volume de sistema de 8–12 GiB, criptografado, e confira se será excluído com a instância. Confira a estimativa de custo antes de iniciar.
7. Inicie a instância e aguarde o estado **Em execução** e as verificações de status aprovadas.
8. Nos detalhes da instância, copie **DNS público (IPv4)** e **Endereço IPv4 público**. Anote também ID e região para localizar os recursos ao encerrar.

| Entrada | Porta TCP | Origem |
| --- | --- | --- |
| SSH | 22 | Seu IPv4 público atual/32, opção **Meu IP**, ou rede administrativa autorizada. |
| HTTP | 80 | Seu IPv4 público atual/32 (**Meu IP**) ou a rede de saída autorizada do laboratório. |
| Backend | 8000 | Nenhuma entrada; será acessível apenas dentro da EC2. |

**Esperado:** instância Ubuntu em execução, DNS e IPv4 públicos preenchidos e as duas entradas 22/80 configuradas. Não é preciso registrar domínio, usar Certbot ou instalar banco gerenciado.

**Verifique:** qual regra permite entrar por SSH? Por que liberar 80 não significa que a aplicação já está funcionando?

**Se não conseguir avançar:** sem IPv4 público ou DNS público, confira atribuição de IP e opções DNS da VPC; sem cota/permissão, resolva o acesso à conta antes de continuar. Não substitua o DNS público pelo privado.

## 1.2. Entender os valores que serão substituídos

| Marcador | O que colocar |
| --- | --- |
| `SUA_CHAVE.pem` | Nome do arquivo `.pem` baixado/selecionado para essa instância. |
| `SEU_DNS_EC2` | DNS público completo, copiado do console; sem `http://`, espaços ou barras. O IPv4 público também pode ser usado como endereço. |
| `IP_PUBLICO` | IPv4 público atual do console; alternativa ao DNS, caso a descoberta automática falhe. |
| `SEU_USUARIO_WINDOWS` | Nome da pasta do seu usuário em `C:\Users`, somente no WSL. |

O arquivo será copiado para `~/redes-rest/chave-ec2.pem`. Esse será o nome usado nos comandos seguintes, independentemente do nome original.

## 1.3. Baixar os artefatos no seu computador

**Onde:** terminal **A do seu computador**. Selecione a aba correspondente. Baixe a chave `.pem` para a pasta **Downloads** antes de executar. Se a sua pasta de downloads tiver outro nome/local, ajuste somente o caminho de origem no comando `cp`.

=== "WSL"

    Abra o aplicativo **Ubuntu/WSL** no Windows. Os comandos abaixo não são para o PowerShell. O Ubuntu no WSL já deve estar instalado.

    ```bash
    sudo apt update
    sudo apt install -y git openssh-client curl
    mkdir -p ~/redes-rest
    cp "/mnt/c/Users/SEU_USUARIO_WINDOWS/Downloads/SUA_CHAVE.pem" ~/redes-rest/chave-ec2.pem
    chmod 400 ~/redes-rest/chave-ec2.pem
    cd ~/redes-rest
    git clone https://github.com/rafaelrezo/pratica-rest-ec2.git
    ```

    Ajuste os dois marcadores no `cp`. A cópia para a pasta Linux evita depender das permissões do arquivo em `/mnt/c`. Os arquivos baixados no WSL podem ser abertos no Windows pelo Explorador em `\\wsl.localhost\Ubuntu\home\SEU_USUARIO_LINUX\redes-rest`; o nome da distribuição pode variar. Para abrir diretamente a pasta atual, execute `explorer.exe .` dentro de `~/redes-rest`.

=== "Ubuntu"

    Abra o aplicativo **Terminal** do seu computador Ubuntu.

    ```bash
    sudo apt update
    sudo apt install -y git openssh-client curl
    mkdir -p ~/redes-rest
    cp "$HOME/Downloads/SUA_CHAVE.pem" ~/redes-rest/chave-ec2.pem
    chmod 400 ~/redes-rest/chave-ec2.pem
    cd ~/redes-rest
    git clone https://github.com/rafaelrezo/pratica-rest-ec2.git
    ```

    Se o arquivo estiver em `Baixados` ou em outra pasta, altere o caminho de origem no `cp` para a localização real. Você pode encontrá-la no gerenciador de arquivos.

=== "macOS"

    Abra **Aplicativos → Utilitários → Terminal**. Confira `git --version`; se o macOS solicitar as ferramentas de linha de comando, conclua a instalação e repita a verificação. SSH e curl acompanham o sistema; não é necessário instalar Homebrew.

    ```bash
    mkdir -p ~/redes-rest
    cp "$HOME/Downloads/SUA_CHAVE.pem" ~/redes-rest/chave-ec2.pem
    chmod 400 ~/redes-rest/chave-ec2.pem
    cd ~/redes-rest
    git clone https://github.com/rafaelrezo/pratica-rest-ec2.git
    ```

    Se o arquivo tiver sido salvo fora de Downloads, ajuste a origem do `cp`. A pasta local será `/Users/SEU_USUARIO/redes-rest`.

**Esperado, nas três plataformas:** o clone termina sem erro. Confira:

```bash
ls -l ~/redes-rest/chave-ec2.pem
ls ~/redes-rest/pratica-rest-ec2/kit
```

A primeira saída deve mostrar permissão de leitura somente para o dono (`-r--------`). A segunda deve incluir `iniciar-lab.sh` e `validar-lab.sh`.

**Verifique:** em qual computador estão esses arquivos? O arquivo `.pem` é a credencial da API ou a credencial de acesso à máquina?

**Se aparecer erro:** `No such file` no `cp` indica nome/caminho de chave incorreto. Se o Git avisar que a pasta já existe, use o clone existente; não apague a chave ou seus trabalhos para refazer a etapa.

## 1.4. Conectar à EC2

**Onde:** ainda no terminal A do seu computador, em qualquer uma das três plataformas. Substitua o DNS:

```bash
ssh -i ~/redes-rest/chave-ec2.pem ubuntu@SEU_DNS_EC2
```

No primeiro acesso, o SSH mostra a impressão digital da chave do servidor. No console AWS, abra **Ações → Monitorar e solucionar problemas → Obter log do sistema** e procure `BEGIN SSH HOST KEY FINGERPRINTS`. Compare a impressão digital correspondente antes de digitar `yes`. Essa é a identidade do servidor, diferente da chave `.pem` que identifica seu acesso. [Procedimento oficial da AWS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connection-prereqs-general.html).

**Esperado:** mensagem de boas-vindas do Ubuntu e prompt semelhante a `ubuntu@ip-...:~$`. Confirme dentro da sessão:

```bash
whoami
hostname
```

`whoami` deve responder `ubuntu`. Mantenha esse terminal aberto: ele será o **terminal A — EC2**. Abra uma segunda aba/janela local para o **terminal B — seu computador**, que será usada na etapa de acesso.

**Verifique:** o que mudou no prompt? Se executar `ls` agora, você está consultando arquivos do seu computador ou da EC2?

**Se falhar:** timeout exige conferir instância, DNS e entrada 22 para seu IP atual. `Permission denied (publickey)` exige conferir o usuário `ubuntu`, o arquivo `.pem` e o par de chaves da instância. Veja os [passos de diagnóstico](06-diagnosticar.md#61-recuperar-o-acesso-ssh).

Avance para [2. Iniciar na EC2](02-iniciar.md).
