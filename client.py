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

#manda le carte della mano a ogni giocatore, e la board coperta
def update_cards(client_socket):
    
    #clear()

    for _ in range(5):
        print("\n")

    #mando le carte della board coperte
    print("Carte nella board:")
    board = client_socket.recv(1024).decode('utf-8')
    print(board)
    
    #chiedo il prossimo pacchetto
    client_socket.send("NEXT".encode('utf-8'))

    #mando le carte in mano
    print("Carte in Mano:")
    hand = client_socket.recv(1024).decode('utf-8')
    print(hand)

    client_socket.send("DONE".encode('utf-8'))

#per inviare e ricevere messaggi 
def recv_message(client_socket):
    
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        
        if message == "MESSAGE":
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
            client_socket.send("READY".encode('utf-8'))
            
        elif message == "DONE":
            break
    
#loop di gioco
def client_loop():
    
    client_socket = start_client()

    #loop del gioco
    while True:
        
        message = client_socket.recv(1024).decode('utf-8')
        print(f"[LOG]: {message}")
        
        # se ricevo update aggiorno le carte
        if message == "UPDATE":
            update_cards(client_socket)
            pass
        
        # stampo le carte giocate nel turno
        if message == "UPDATE_CARDS":
            print("entrato qua zioe o ivfji ")
            recv_message(client_socket)
        
        # se ricevo un 1 si entra nel turno del giocatore
        elif message == "1":
            print("è il tuo turno!")
            
            #loop del turno
            while True:
                
                # il giocatore decide cosa vuole fare
                print("cosa vuoi fare?\n 0: carta da mano\n 1: carta dalla board\n 2: carta da un giocatore\n")
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
                    
                    #ricevo gli aggiornamenti
                    if client_socket.recv(1024).decode('utf-8') == "UPDATE":
                        update_cards(client_socket)

                    # ricevo la carta giocata dal server
                    if client_socket.recv(1024).decode('utf-8') == "UPDATE_CARDS":
                        recv_message(client_socket)

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