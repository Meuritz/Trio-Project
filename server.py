import socket
import threading

#player id and player name
players = {}  #players = {02020, Meuritz}

def handle_client(conn, addr):
    """
    Assegna un username e gestisce i client connessi
    """    
    # Prompt for username
    conn.send("Enter your username: ".encode('utf-8'))  # Send a prompt for the username
    
    # Receive the username from the client
    username = conn.recv(1024).decode('utf-8')
    print(f"[PLAYER] {username} da {addr}")
    
    # Store the username in the players dictionary
    players[addr] = username
    #devo creare una struttura che immagazini un numero progressivo, l'adress dei giocatori e il loro username
    
    # Send a welcome message back to the client
    welcome_message = f"Welcome, {username}! il gioco iniziera a breve.."
    conn.send(welcome_message.encode('utf-8'))
    
    #da qui inizia il gioco
    while(True):
        #fare in modo che si entri in questa parte solo dopo che sono entrati tutti i giocatori
        #qua devo gestire gli input dei giocatori
        #far arrivare le mosse eseguite al processo principale
        pass
    

def start_server():
    #iniziamo ad avviare il server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Host and port
    Host = "localhost"
    Port = 60420

    server_socket.bind((Host, Port))

    # From here we listen for connections
    server_socket.listen(3)
    #il server è in funzione!
    print(f"Server online su {Host} ed in ascolto sulla porta {Port}")

    #server mainloop
    while True:
        #accetto le connessioni fino ad un max di 3, e creo un thread per ogni connessione

        if((threading.active_count() - 1) != 3): 
            
            conn, addr = server_socket.accept()
            
            thread = threading.Thread(target=handle_client, args=(conn, addr))  # Create a new thread for the client
            
            #stampo i thread attivi
            print(f"{threading.active_count()} thread attivi")

            #faccio partire il thread appena creato
            thread.start()  
        
        #da qui inizia il gioco vero e proprio
        #devo gestire i turni dei giocatori --> il server decide chi inizia
        #devo prendere la mossa del giocatore di turno e usarla per aggiornare il gioco

        #per gestire le carte posso usare una combinazione di dizionario e lista

        
        


if __name__ == "__main__":
    start_server()