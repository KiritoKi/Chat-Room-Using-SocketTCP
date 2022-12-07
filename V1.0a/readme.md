# Chat Room Usando Socket - Conexão TCP
#### Curso: Ciência da Computação
#### Trablho de Rede de Computadores I
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
- A variável server utiliza a conexão com o socket definindo os argumentos que queremos utilizar, o AF_INET(socket de internet ipv4) e o SOCK_STREAM(protocolo TPC)
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
- Função principal que recebe e escuta o servidor
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

### Conexão com o Servidor

```
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))
```
- A variável client utiliza a conexão com o socket definindo os argumentos que queremos utilizar, o AF_INET(socket de internet ipv4) e o SOCK_STREAM(protocolo TPC)
- A função connect se conecta ao endereço e porta

### Variavel Global 

```
stop_thread = False
```
# Eventos, Estados e Mensagens:
#### Os eventos, estados e mensagens - lógica do código e como funciona:
