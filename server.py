import socket
import threading

class GameServer:
    
    def __init__(self, host="localhost", port=60420):
        self.host = host
        self.port = port
        self.players = []
        self.login_lock = threading.Lock()
        self.start = 0
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def add_player(self, username, addr):
        self.players.append([username, addr])

    def remove_player(self, addr):  
        for player in self.players:
            if player[1] == addr:
                self.players.pop(player)
                break
    
    def handle_client(self, conn, addr):
        """
        Assegna un username e gestisce i client connessi
        """
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

            # da qui inizia il gioco
            while running:
                # fare in modo che si entri in questa parte solo dopo che sono entrati tutti i giocatori
                # qua devo gestire gli input dei giocatori
                # far arrivare le mosse eseguite al processo principale
                pass

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

        # il server è in funzione!
        print(f"Server online su {self.host} ed in ascolto sulla porta {self.port}")

        # server mainloop
        while True:
            
            # accetto le connessioni fino ad un max di 3, e creo un thread per ogni connessione
            if (threading.active_count() - 1) != 3:
                conn, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))  # Create a new thread for the client

                # stampo i thread attivi
                print(f"{threading.active_count()} thread attivi")

                # faccio partire il thread appena creato
                thread.start()
            

if __name__ == "__main__":
    server = GameServer()
    server.start_server()
