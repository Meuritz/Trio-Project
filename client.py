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
        print(message)
        
        # aggiorno le carte
        if message == "0":  # aggiorno le carte del giocatore ed il campo
            # clear()
            print("Carte in Mano:\n")
            print(client_socket.recv(1024).decode('utf-8'))
            client_socket.send("DONE".encode('utf-8'))
        
        # turno del giocatore
        elif message == "1":
            print("è il tuo turno!")
            while True:
                # il giocatore decide cosa vuole fare
                print("cosa vuoi fare?\n 0: carta da mano\n 1: carta dalla board\n 2: carta da un giocatore)\n")
                move = ""
                
                # ciclo fino a che il giocatore non sceglie un opzione valida
                while True:
                    move = input("-->")
                    if  0 <= int(move) <= 2:
                        client_socket.send(move.encode('utf-8'))
                        break
                    else:
                        print("scelta non valida!")

                # carta da mano
                if move == "0":

                    # prendo in input la carta giocata e la mando al server
                    card = input("Quale carta vuoi giocare? [0-8]\n -->")
                    client_socket.send(card.encode("utf-8"))
                    
                    # ricevo la carta giocata dal server
                    print(client_socket.recv(1024).decode('utf-8'))

                    #aspetto che il server mi dica se posso continuare
                    response = client_socket.recv(1024).decode('utf-8')
                    print(f"[LOG] response = {response}") 

                    if response == "STOP":
                        break
                
                # carta dalla board
                elif move == "1":
                    pass
                
                # carta da un giocatore
                elif move == "2":
                    pass

if __name__ == "__main__":

    client_loop()
    print("uscendo per qualche motivo!")