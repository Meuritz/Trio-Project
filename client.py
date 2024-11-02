import socket
from os import system, name

# Define the server address and port
SERVER_HOST = "localhost"
SERVER_PORT = 60420


#funzione per connetersi al server di gioco
def start_client():
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to the server
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connected to server: {SERVER_HOST}:{SERVER_PORT}")
    
    # Receive the prompt for the username
    prompt = client_socket.recv(1024).decode('utf-8')
    print(prompt)
    
    # Send the username to the server
    username = input()
    client_socket.send(username.encode('utf-8'))
    
    return client_socket


# define our clear function
def clear():

    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

def client_loop():
    
    client_socket = start_client()

    while True:
        message = client_socket.recv(1024).decode('utf-8')
        
        if message == "0":  #aggiorno le carte del giocatore ed il campo
            clear()
            print("Carte in Mano:\n")
            print(client_socket.recv(1024).decode('utf-8'))
            pass

if __name__ == "__main__":
    client_loop()
    print("uscendo per qualche motivo!")