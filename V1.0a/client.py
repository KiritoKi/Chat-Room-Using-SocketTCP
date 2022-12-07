import socket
import threading

# Choosing Nickname
nickname = input("Choose a nickname: ")
if nickname == 'admin':
    password = input("Enter password for admin: ")

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

stop_thread = False

# Listening to Server and Sending Nickname
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

# Sending Messages To Server
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


# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
