# Chat Room Usando Socket - Conexão TCP
#### Curso: Ciência da Computação
#### Trabalho de Rede de Computadores I
#### Professor: Jorge Lima de Oliveira Filho
#### Desenvolvedores: João Carlos Ribas Chaves Júnior, Yan Costa Macedo.

# Servidor

### Bibliotecas utilizadas:
```
import socket
import threading
```
- A biblioteca socket é a biblioteca que possibilita a conexão e criação dos sockets, além do envia dos dados entre cliente e servidor. 
```
import socket
```
-A biblioteca threading é a biblioteca que é necessária para execução de várias tarefas ao mesmo tempo.
```
import threading
```

### Dados de Conexão
- Variáveis utilizadas para conexão com o servidor.
```
host = '127.0.0.1'
port = 55555
```

### Inicializador do Servidor:
```
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
```
- A variável server utiliza a conexão com o socket definindo os argumentos que queremos utilizar, o AF_INET(socket de internet ipv4) e o SOCK_STREAM(protocolo TCP)
- a função bind do server aloca uma tupla com o endereço ip e a porta do servidor
- a função listen coloca o server em modo escuta

### Variavéis Globais
```
clients = []
nicknames = []
bans_path = r'/bans.txt'
```
- A lista clients é uma lista gerada para armazenar os clientes conectados ao servidor
- A lista clients é uma lista gerada para armazenar os nicknames dos clientes conectados ao servidor
- A variável bans_path é utilizada como PATH do arquivo com a lista de bans

### Funções:
#### Função broadcast
- Transmite as mensagens para todos os clientes conectados no servidor
##### Parametros:
- message: mensagem para ser enviado

```
def broadcast(message):
    for client in clients:
        client.send(message)
```

#### Função handle:
- Se encarrega com as mensagens do cliente
- Primeiro é armazenado a mensagem recebida do cliente
- Se a mensagem chegada do cliente for um comando de admin KICK, então:
    - Verifica se o usuário é o admin
    - aplica a função kick_user para o nickname recebido
- Se não for o usuario admin, apenas nega o comando
- Se a mensagem chegada do cliente for um comando de admin BAN, então:
    - Verifica se o usuário é o admin
    - aplica a função kick_user e armazena o nome do usuário no arquivo 'bans.txt'

##### Parametros:
- client: cliente conectado ao servidor

```
def handle(client):
    while True:
        try:

            msg = message = client.recv(1024)
            if msg.decode('ascii').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('ascii')[5:]
                    kick_user(name_to_kick)
                    print(f'{name_to_kick} was banned!')
                else:
                    client.send('Command was refused!'.encode('ascii'))
            elif msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open(bans_path, 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned!')
                else:
                    client.send('Command was refused!'.encode('ascii'))
            # Broadcasting messages
            else:
                broadcast(message)
        except:
            # Removing and closing clients
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} left the chat!'.encode('ascii'))
                nicknames.remove(nickname)
                break

```

#### Função receive:
- Função principal do servidor que recebe e escuta os clientes
- Aceita conexão dos clientes com o servidor
- Carrega a lista de nomes banidos e nega o acesso de usuários banidos
- Uma vez que um cliente está conectado, envia a string  'NICK' para requisitar o nickname do cliente
- Caso for o usuario 'admin' ele envia a string 'PASS' para requisitar o password e verifica o password do admin, aceitando ou negando a conexão
- faz a interação de cliente conectado ao servidor com os clientes e inicializa as threads
##### Parametros:
(none)

```
def receive():
    while True:
        # Accept connection
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        # Request nickname
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        # Load banned nicknames
        with open(bans_path, 'r') as f:
            bans = f.readlines()
        # Deny access to banned nicknames
        if nickname+'\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue
        # Check if user is admin by nickname: admin
        if nickname == 'admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')
            # Check password admin ###Need update-version to use Hash map
            if password != 'adminpass123':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        # Restore Nickname
        nicknames.append(nickname)
        clients.append(client)

        # Print and broadcast nickname
        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chat!'.encode('ascii'))
        client.send('Connected to the server!'.encode('ascii'))

        # Start handling thread for client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
```

#### Função kick_user:
- Função de kick de usuários
- Remove o cliente da lista de clientes
- Envia um aviso ao cliente que foi foi kickado e em seguida encerra a conexão com esse cliente
- Envia um aviso a todos clientes através do broadcast que o usuário x foi kickado
##### Parametros:
- name: Nome do usuário a ser kickado

```
def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by an admin!'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by an admin!'.encode('ascii'))
```

### Corpo principal do código
- Inicia a interação com o servidor a partir da execução da função receive

```
print("Server is listening...")
receive()
```

# Cliente

### Bibliotecas utilizadas:
```
import socket
import threading
```
- A biblioteca socket é a biblioteca que possibilita a conexão e criação dos sockets, além do envia dos dados entre cliente e servidor. 
```
import socket
```
-A biblioteca threading é a biblioteca que é necessária para execução de várias tarefas ao mesmo tempo.
```
import threading
```

### Conexão com o Servidor

```
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))
```
- A variável client utiliza a conexão com o socket definindo os argumentos que queremos utilizar, o AF_INET(socket de internet ipv4) e o SOCK_STREAM(protocolo TCP)
- A função connect se conecta ao endereço e porta

### Variavel Global 

```
stop_thread = False
```
- Variável para controlar a finalização das threads
- Utilizadas para caso o usuário esteja/seja banido ou o password do admin esteja errado

### Funções:
#### Função receive:
- Função que recebe e escuta mensagens do servidor
- Se a mensagem recebida do servidor for 'NICK'
    - Envia o nickname para o servidor
    - Verifica se a próxima mensagem recebida do servidor foi 'PASS' para enviar uma senha
        - Caso tenha recebido a mensagem 'REFUSE', recebe uma mensagem de que a senha está errada
    -Verifica se a proxima mensagem recebida do servidor foi 'BAN':
        -Caso tenha recebido, recebe a mensagem que foi banido e encerra a conexão do cliente com o servidor
##### Parametros:
(none)

```
def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                # If 'PASS' Send password
                if next_message == 'PASS':
                    client.send(password.encode('ascii'))
                    # Refuse Password
                    if client.recv(1024).decode('ascii') == 'REFUSE':
                        print("Connection was refused! Wrong password!")
                        stop_thread = True
                # If 'BAN' Print "connection refused" and close connection
                elif next_message == 'BAN':
                    print('Connection refused because of ban!')
                    client.close()
                    stop_thread = True
            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occurred!")
            client.close()
            break
```

#### Função write:
- Função de Escrever do cliente
- Ao escrever e enviar uma mensagem, é enviado para o servidor o 'nickname: message' do usuário
- Se a mensagem do usuário iniciar com /
    - Verifica se é o usuário 'admin'
        - Se o comando for /kick envia para o servidor a mensagem 'KICK name_to_kick'
        -Se o comando for /ban envia para o servidor a mensagem 'BAN name_to_ban'
    - Se não for o usuário admin, printa que ele nao tem essa permissão
##### Parametros:
(none)

```
def write():
    while True:
        if stop_thread:
            break
        message = f'{nickname}: {input("")}'
        # If command / used to AdminCommand
        if message[len(nickname)+2:].startswith('/'):
            if nickname == 'admin':
                # If '/kick username' KICK
                if message[len(nickname)+2:].startswith('/kick'):
                    client.send(
                        f'KICK {message[len(nickname)+2+6:]}'.encode('ascii'))
                    # If '/ban username' BAN
                elif message[len(nickname)+2:].startswith('/ban'):
                    client.send(
                        f'BAN {message[len(nickname)+2+5:]}'.encode('ascii'))
            # If non-admin user executes the admin command
            else:
                print("Commands can only be executed by the admin!")
        # Send messages to server
        else:
            client.send(message.encode('ascii'))
```

### Corpo principal do código
- Inicia as tarefas de Escuta e Escrita do cliente

```
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
```

# Eventos, Estados e Mensagens:
#### Os eventos, estados e mensagens - lógica do código e como funciona:

<br />
<div style="line-height: 2;">
    <ol>
        <li>Servidor se prepara e aguarda solicitações - o servidor é criado, e é preparado na rede local, com nome 'localhost' porta padrão 55555 e a partir daí fica no aguardo de novas solicitações;</li>
        <li>Cliente solicita conexão - o cliente envia ao servidor uma solicitação de conexão do socket para iniciar as interações;
        </li>
        <li>Servidor aceita a conexão - o servidor aceita a conexão solicitada pelo cliente e espera a solicitação do que fazer em seguida;
        </li>
        <li>Servidor aguarda solicitações de conteúdo - o servidor começa a aguardar que o cliente que estabeleceu a conexão envie uma solicitação sobre qual conteúdo deseja;
        </li>
        <li>Servidor transmite as mensagens dos clientes entre os clientes
        </li>
        <li>Servidor envia mensagem 'NICK' para o cliente para requisitar o nickname
        </li>
        <li>Servidor envia mensagem 'PASS' para o cliente para requisitar o password
        </li>
        <li>Servidor envia mensagem 'BAN' para o cliente para insinuar que o cliente foi banido
        </li>
        <li>Servidor envia mensagem 'REFUSE' para o cliente para rejeitar a conexão com o cliente
        </li>
        <li>Servidor fecha o socket do cliente - o servidor fecha a conexão com o socket do cliente, visto que não há mais dados para serem enviados;
        </li>
        <li>Cliente fecha o socket - o cliente fecha o socket visto que todo o processo foi finalizado.
        </li>
    </ol>
</div>

<br />

# Funcionamento do software:
O programa desenvolvido faz a comunicação entre vários clientes utilizando um chat através de um socket TCP e um servidor. O usuário pode entrar como usuário normal ao colocar um nickname, ou um usuario 'admin'. O usuário 'admin' deve inserir a senha de admin para entrar. O usuário normal pode enviar mensagens que serão recebidas para todos os outros clientes conectados. O usuário 'admin' além de poder enviar mensagens, também possui a função de dar KICK e BAN nos outros usuários, sendo o primeiro, um expulsão momentanêa da sala e o BAN é um banimento permantente do usuário no servidor. O servidor possui logs de quais clientes foram conectados.

# Propósito do software:
O propósito so software é conectar vários clientes a um servidor para que possam fazer interações através de mensagens entre si.

# Motivação da escolha do protocolo de transporte:
O protocolo escolhido foi o TCP, sendo escolhido por conta de garantir maior integradade de transmissão de mensagens, fazendo com que os dados transferidos cheguem sem nehum tipo de perda ou atraso.

# Requisitos mínimos de funcionamento:
- Rede local 
- Máquina com python 3.7
