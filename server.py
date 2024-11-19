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

                #UPDATE il client si prepara a ricevere le carte
                conn.send("UPDATE".encode('utf-8'))

                #mando la board coperta
                conn.send(game.get_gameboard().encode('utf-8'))

                #aspetto conferma prima di continuare
                if conn.recv(1024).decode('utf-8') == "NEXT":
                    pass
                
                #mando le carte in mano al giocatore
                conn.send(game.print_cards(self.players.index(player)).encode('utf-8'))

                #prima di uscire aspetto che tutti i client abbiano mandato la conferma finale
                if conn.recv(1024).decode('utf-8') == "DONE":
                    ack += 1

            if(ack == 3):
                print("[LOG] Carte inviate con successo!")
            else:
                print("[LOG] Errore nel invio delle carte")

    #per mandare le carte che sono state giocate durante il turno
    def send_message(self, messages):
        
        
        for player in self.players:
                
            conn = player[1]

            conn.send("UPDATE".encode('utf-8'))

            for message in messages:
                
                conn.send("MESSAGE".encode('utf-8'))
                conn.send(message.encode('utf-8'))
            
            if conn.recv(1024).decode('utf-8') == "READY":
                conn.send("NEXT".encode('utf-8'))
            
            conn.send("DONE".encode('utf-8'))

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
            
            player = self.players[turn] #giocatore
            conn = player[1] #per comunicare con il giocatore
            player_name = player[0] #nome del giocatore di turno
            card_played = [] #le carte che sono state giocate
            messages = [] #i messaggi da inviare dopo ogni update  
            
            #dico al giocatore che è il suo turno
            conn.send("1".encode('utf-8'))

            #faccio giocare il giocatore fino a che non usa una carta diversa dalla prima usata
            for i in range(2):

                #ricevo la mossa dal giocatore
                move = conn.recv(1024).decode('utf-8')

                #il giocatore gioca una carta dalla mano
                if move == "0":
                    
                    #recupero la carta
                    card_index = conn.recv(1024).decode('utf-8')
                    card = game.player_hand[turn][int(card_index)]
                    messages.append(f"{player_name} ha giocato un {card}")

                    #la rimuovo dalla mano del giocatore
                    game.player_hand[turn].remove(card)
                    
                    #mando le carte aggiornate
                    self.give_cards(game)
                    time.sleep(1)  # import time
                    self.send_message(messages)

                    #se la carta è uguale alla prima giocata o è la prima
                    if len(card_played) == 0 or card == card_played[0]:
                        card_played.append(int(card))
                        print(f"carte giocate: {len(card_played)}")
                        conn.send("OK".encode('utf-8'))
                    
                    #se la carta è diversa dalla prima carta giocata
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
            
            if len(card_played) == 3:
                game.tris_counter[turn] += 1            

            #cambio il turno
            if turn == 2:
                turn = 0
            else:
                turn += 1


if __name__ == "__main__":
    server = GameServer()
    server.start_server()
    server.start_game()
