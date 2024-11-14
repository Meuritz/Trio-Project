import socket
import threading
import time
from gamelib import Trio

class GameServer:
    #inizializzo le variabili con un costruttore
    def __init__(self, host="localhost", port=60420):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.players = []
        self.login_lock = threading.Lock() #per evitare che più utenti agiscano allo stesso tempo su "players"
        self.start = threading.Event() #per far partire la partita una volta che sono entrati 3 giocatori
        self.connected_players = 0

    #funzione per aggiungere i giocatori in memoria
    def add_player(self, username, addr, conn):
        self.players.append([username, addr, conn])

    #funzione per rimuove i giocatori in caso di disconnessione DA RIVEDERE 
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
                self.add_player(username, conn, addr)
            
            # stampo il numero di giocatori connessi
            print(f"{self.connected_players} giocatori connessi")

            # Send a welcome message back to the client
            welcome_message = f"Benvenut3 {username}! il gioco iniziera a breve.."
            conn.send(welcome_message.encode('utf-8'))
    
            #quando si arriva a 3 giocatori il gioco inizia in automatico
            self.start.wait()
            time.sleep(1)

            # da qui inizia il gioco
            while running:
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
        self.server_socket.listen(2)

        # segnalo che il server è online
        print(f"Server online su {self.host} ed in ascolto sulla porta {self.port}")

        # gestisco le connessioni
        while True:
            
            # accetto le connessioni fino ad un max di 3, e creo un thread per ogni connessione
            if (self.connected_players) != 3:

                #accetto le connessioni ed avvio un thread per ognuna di esse
                conn, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))

                # faccio partire il thread appena creato
                thread.start()

                #aumento di 1 il numero dei giocatori
                self.connected_players += 1
                
            #chiedo conferma per avviare la partita dopo che sono entrati tutti i giocatori ed hanno messo il loro username
            if (len(self.players)) == 3: 
                
                print("\nTutti i giocatori sono connessi, inizio la partita...")
                time.sleep(1) 
                self.start.set()
                break    
        
    #0 aggiorno le carte in mano ad i giocatori
    def give_cards(self, game):
        #do le carte ad i giocatori
            
            ack = 0
            
            for player in self.players:
                
                conn = player[1]

                #0 il client si prepara a ricevere le carte
                conn.send("0".encode('utf-8'))

                #mando la board coperta
                conn.send(game.get_gameboard().encode('utf-8'))

                if conn.recv(1024).decode('utf-8') == "NEXT":
                    pass

                conn.send(game.print_cards(self.players.index(player)).encode('utf-8'))

                if conn.recv(1024).decode('utf-8') == "DONE":
                    ack += 1

            if(ack == 3):
                print("[LOG] Carte inviate con successo!")
            else:
                print("[LOG] Errore nel invio delle carte")

    #this method handles the game
    def start_game(self):

        update = True
        turn = 0

        #creo un oggetto trio e gli passo i giocatori
        game = Trio(self.players)
        game.prepare_game()

        #fino a che un giocatore non arriva a 3 tris
        while(game.tris_counter[0] != 3 and game.tris_counter[1] != 3 and game.tris_counter[2] != 3):
                    
            #se ce stato un cambiamento nelle carte dei giocatori le aggiorno
            if update == True:
                self.give_cards(game)
                update = False
            
            player = self.players[turn]
            conn = player[1]
            player_name = player[0]
            card_played = []
            
            #dico al giocatore che è il suo turno
            conn.send("1".encode('utf-8'))

            #faccio giocare il giocatore fino a che non usa una carta diversa dalla prima usata
            for i in range(2):
                
                print("sono nel for loop!")

                #ricevo la mossa dal giocatore
                move = conn.recv(1024).decode('utf-8')

                #il giocatore gioca una carta dalla mano
                if move == "0":
                    
                    #recupero la carta
                    card_index = conn.recv(1024).decode('utf-8')
                    card = game.player_hand[turn][int(card_index)]

                    #comunico la carta giocata al player di turno
                    conn.send(f"Hai giocato un {card}!".encode('utf-8'))

                    #comunico la carta giocata agli altri player
                    for player in self.players:
                        if player[1] != conn:
                            spectator = player[1]
                            spectator.send(f"{player_name} ha giocato un {card}".encode('utf-8'))

                    #se la carta è uguale alla prima giocata o è la prima
                    if len(card_played) == 0:
                        card_played.append(int(card))
                        print(f"carte giocate: {len(card_played)}")
                        conn.send("OK".encode('utf-8'))

                    elif card == card_played[0]:
                        print(f"carte giocate: {card_played[0]}, {card}")
                        card_played.append(int(card))
                        conn.send("OK".encode('utf-8'))
                    
                    #se la carta è diversa dall prima carta giocata
                    else:
                        conn.send("STOP".encode('utf-8'))
                        print("[LOG] il turno del giocatore è terminato!")
                        break
                    
                #scopri una carta dalla board
                elif move == "1":
                    pass

                #chiedi una carta ad uno dei giocatori
                elif move == "2":
                    pass

            turn += 1


if __name__ == "__main__":
    server = GameServer()
    server.start_server()
    server.start_game()
