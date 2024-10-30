import socket
import threading
import time

class GameServer:
    #inizializzo le variabili con un costruttore
    def __init__(self, host="localhost", port=60420):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.players = []
        self.login_lock = threading.Lock() #per evitare che più utenti agiscano allo stesso tempo su "players"
        self.start = threading.Event() #per far partire la partita una volta che sono entrati 3 giocatori
        
    #funzione per aggiungere i giocatori in memoria
    def add_player(self, username, addr):
        self.players.append([username, addr])

    #funzione per rimuove i giocatori in caso di disconnessione
    def remove_player(self, addr):
        for player in self.players:
            if player[1] == addr:
                self.players.pop(player)
                break
    
    #funzione per gestire i client
    def handle_client(self, conn, addr):
        
        running = True
        
        try:
            # Prompt for username
            conn.send("Enter your username: ".encode('utf-8'))  # Send a prompt for the username

            # Receive the username from the client
            username = conn.recv(1024).decode('utf-8')
            print(f"[PLAYER] {username} da {addr}")

            # Store the username in the players dictionary list
            with self.login_lock:
                self.add_player(username, addr)

            # Send a welcome message back to the client
            welcome_message = f"Benvenut3 {username}! il gioco iniziera a breve.."
            conn.send(welcome_message.encode('utf-8'))
    
            #quando si arriva a 3 giocatori il gioco inizia in automatico
            self.start.wait()
            time.sleep(1)
            print("avvio in corso...")

            # da qui inizia il gioco
            while running:
                # fare in modo che si entri in questa parte solo dopo che sono entrati tutti i giocatori
                # qua devo gestire gli input dei giocatori
                # far arrivare le mosse eseguite al processo principale
                pass
        
        #gestisco possibili errori
        except (socket.error, ConnectionResetError, WindowsError) as e:
            print(f"[DISCONNECT] {addr} si è disconnesso a causa di {e}")
            with self.login_lock:
                self.remove_player(addr)
        finally:
            running = False
            conn.close()
    
    #metodo per fare avviare il server
    def start_server(self):
       
        # iniziamo ad avviare il server
        self.server_socket.bind((self.host, self.port))

        # From here we listen for connections
        self.server_socket.listen(3)

        # segnalo che il server è online
        print(f"Server online su {self.host} ed in ascolto sulla porta {self.port}")

        # gestisco le connessioni
        while True:
            
            # accetto le connessioni fino ad un max di 3, e creo un thread per ogni connessione
            if (len(self.players)) != 3:

                #accetto le connessioni ed avvio un thread per ognuna di esse
                conn, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))

                # stampo il numero di giocatori connessi
                print(f"{threading.active_count()} thread attivi")

                # faccio partire il thread appena creato
                thread.start()
                
            #chiedo conferma per avviare la partita dopo che sono entrati tutti i giocatori
            if (len(self.players)) == 3: 
                
                print("Tutti i giocatori sono connessi. Inizio la partita...")
                time.sleep(1) 
                self.start.set()
                break


if __name__ == "__main__":
    server = GameServer()
    server.start_server()
