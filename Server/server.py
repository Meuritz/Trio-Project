import socket
import threading
import time
from gamelib import Trio
from termcolor import colored
from os import system, name

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
        self.comm_lock = threading.Lock()

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
        
        # ricevo l'username dal client
        username = conn.recv(1024).decode('utf-8')
        print(f"[PLAYER] {username} da {addr}")

        # metto l'username insieme al suo indirizzo in un array
        with self.login_lock:
            self.add_player(username, conn, addr)
        
        # stampo il numero di giocatori connessi
        print(f"{len(self.players)} giocatori connessi")

        # mamdo un messaggio di benvenuto al client
        welcome_message = f"Benvenut3 {username}! il gioco iniziera a breve.."
        conn.send(welcome_message.encode('utf-8'))

        #quando si arriva a 3 giocatori il gioco inizia in automatico
        self.start.wait()
        time.sleep(1)

        # da qui inizia il gioco
        while running:
            pass
    
    #funzione principale del server
    def start_server(self):
       
        # iniziamo ad avviare il server, facendo il bind di quest'ultimo ad ip e porta
        self.server_socket.bind((self.host, self.port))

        # rimaniamo in ascolto per le connessioni
        self.server_socket.listen(2)

        # scrivo sul terminale che il server è online
        print(colored(f"Server online su {self.host} ed in ascolto sulla porta {self.port}", color="green"))

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
                print("[SERVER] Carte inviate con successo!")
            else:
                print("[SERVER] Errore nel invio delle carte")

    #per mandare le carte che sono state giocate durante il turno
    def send_message(self, messages):
        ack = 0
        
        for player in self.players:
            conn = player[1]

            # dico al client che sto per inviare dei messaggi
            conn.send("UPDATE_MSG".encode('utf-8'))

            # mando i messaggi ad ogni client 
            for card_message in messages:
                print(f"[SERVER] Inviando messaggio a {player[0]}: {card_message}")  # Print the message being sent
                conn.send("MESSAGE".encode('utf-8'))
                conn.send(card_message.encode('utf-8'))

                # aspetto che il clien mi mandi conferma di ricezione
                if conn.recv(1024).decode('utf-8') == "READY":
                    pass

            # dico al client che tutti i messaggi sono stati inviati
            conn.send("DONE".encode('utf-8'))

            # aspetto che tutti i giocatori mandino la conferma della ricezione
            if conn.recv(1024).decode('utf-8') == "DONE":
                ack += 1

        #stampo sul terminale un messaggio diverso in base all'esito del invio
        if ack == len(self.players):
            print(colored("[SERVER] messaggi inviati con successo!", "green"))
        else:
            print(colored("[SERVER] errore nel invio dei messaggi :(", "red"))
        
    #recupera i nomi dei giocatori eccetto quello di turno
    def get_player_choice(self, turn):
        """
        questa funzione serve per far scegliere al giocatore di turno, il giocatore da cui
        prendere la carta
        """
        names = []
        
        i = 0
        
        for player in self.players:
            
            if self.players.index(player) == turn:
                continue
            else:
                names.append(f"[{i}] {player[0]}")
                i += 1
        
        return names

    def send_msg(self, message):
        
        ack = ""
        
        for player in self.players:
            conn = player[1]
            conn.send("MSG".encode('utf-8'))
            conn.send(message.encode('utf-8'))

    #questa funzione gestisce il gioco
    def start_game(self):
        
        """
        questa funzione gestisce il gioco vero e proprio, si occupa della logica
        e di inviare e ricevere messaggi e risposte dai client
        """

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
            conn.send("PLAY".encode('utf-8'))

            #faccio giocare il giocatore fino a che non usa una carta diversa dalla prima usata
            for i in range(3):
                
                print(f"sono nel turno del giocatore {player_name}")

                #ricevo la mossa dal giocatore
                move = conn.recv(1024).decode('utf-8')
                print(f"[GAME] Move = {move}")
                
                #0: il giocatore gioca una carta dalla mano
                if move == "0":
                    
                    """
                    quando un giocatore vuole giocare una carta direttamente dalla propria mano
                    """

                    #recupero la carta
                    card_index = int(conn.recv(1024).decode('utf-8'))
                    card = game.player_hand[turn][card_index]
                    messages.append(f"{player_name} ha giocato un {card}")
                    
                    #la rimuovo dalla mano del giocatore
                    game.player_hand[turn].remove(card)

                    #mando le carte aggiornate
                    self.give_cards(game)
                    
                    #mando le carte giocate in precedenza
                    self.send_message(messages)
                    
                    #aspetto che i client finiscano di aggiornare le carte
                    time.sleep(1)

                    #se la carta è uguale alla prima giocata o è la prima
                    if len(card_played) == 0 or card == card_played[0][0]:
                        
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "HAND"])
                        #dico al client che puo continuare a giocare
                        conn.send("OK".encode('utf-8'))

                        print(f"[GAME]carte giocate: {len(card_played)}")
                        print(f"[GAME]carta giocata: {card}")
                        
                    #se la carta è diversa dalla prima carta giocata
                    else:
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "HAND"])
                        #termino il turno del giocatore
                        conn.send("STOP".encode('utf-8'))
                        print(f"[GAME]carta giocata: {card}")
                        print(f"[GAME] il turno del giocatore {player_name} è terminato!")
                        break
                    
                #1: scopri una carta dalla board
                elif move == "1":
                    
                    """
                    quando un giocatore vuole scoprire una carta dalla board
                    richiama dei metodi della classe del gioco che si occupano di recuperare la carta
                    e metterla nella board del gioco
                    """

                    #prendo l'indice della carta da scoprire
                    card_index = int(conn.recv(1024).decode('utf-8'))
                    
                    #scopro la carta
                    game.draw_from_board(card_index)
                    
                    #prendo la carta scoperta
                    card = game.get_from_board(card_index)

                    #tolgo la carta dalla board(diversa dalla board mostrata)
                    game.remove_from_board(card_index)

                    #creo un messaggio e lo metto nel buffer dei messaggi
                    messages.append(f"{player_name} ha scoperto un {card}")
                    
                    #mando le carte aggiornate
                    self.give_cards(game)
                    
                    #mando le carte giocate in precedenza
                    self.send_message(messages)

                    #aspetto che i client finiscano di aggiornare le carte
                    time.sleep(1)

                    #se la carta è uguale alla prima giocata o è la prima
                    if len(card_played) == 0 or card == card_played[0][0]:
                        
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "BOARD", card_index])
                        #dico al client che puo continuare a giocare
                        conn.send("OK".encode('utf-8'))
                        
                        print(f"[GAME]carte giocate: {len(card_played)}")
                        print(f"[GAME]carta giocata: {card}")
                        
                    #se la carta è diversa dalla prima carta giocata
                    else:
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "BOARD", card_index])
                        conn.send("STOP".encode('utf-8'))
                        print(f"[GAME]carta giocata: {card}")
                        print(f"[GAME] il turno del giocatore {player_name} è terminato!")
                        break
             
                #2 chiedi una carta ad uno dei giocatori
                elif move == "2":
                    
                    """
                    questa sezione di codice permette al client di scegliere un giocatore
                    e quale carte vuole prendere tra alta e bassa
                    """

                    #recupero la scelta possibile 
                    names = self.get_player_choice(turn)
                    
                    #mando la scelta al giocatore di turno
                    conn.send(names[0].encode('utf-8'))
                    if conn.recv(1024).decode('utf-8') == "NEXT":
                        pass
                    conn.send(names[1].encode('utf-8'))
                    if conn.recv(1024).decode('utf-8') == "DONE":
                        pass
                    
                    #sistemo i nomi per operazioni successive
                    for i in range(2):
                       x = names[i].lstrip(f"[{i}] ")
                       names[i] = x
                
                    #ricevo la scelta del giocatore
                    player_choice = int(conn.recv(1024).decode('utf-8'))    
                                                                
                    #ricevo la scelta tra carta alta o bassa
                    card_choice = int(conn.recv(1024).decode('utf-8'))

                    #varibile per contenere l'INDEX DEL GIOCATORE SCELTO
                    selected_index = ""
                
                    #recupero l'index del giocatore scelto usando il nome, e lo metto nella variabile creata in precedenza
                    for player in self.players:
                        if names[player_choice] == player[0]:
                            selected_index = self.players.index(player)
                            break
                    
                    card = ""
                
                    #in base alla scelta alta/bassa chiamo un funzione diversa
                    if card_choice == 0:
                        card = game.get_max_card_player(selected_index)
                    else:    
                        card = game.get_min_card_player(selected_index)
                
                    #tolgo la carta dalla mano del giocatore scelto
                    game.player_hand[selected_index].remove(card)
                    
                    #creo un messaggio e lo metto nel buffer dei messaggi
                    messages.append(f"{player_name} ha preso un {card} da {names[player_choice]}")
                    
                    #mando le carte aggiornate
                    self.give_cards(game)
                    
                    #mando le carte giocate in precedenza
                    self.send_message(messages)

                    #aspetto che i client finiscano di aggiornare le carte
                    time.sleep(1)
                
                    #se la carta è uguale alla prima giocata o è la prima
                    if len(card_played) == 0 or card == card_played[0][0]:
                        
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "PLAYER", selected_index])
                        #dico al client che puo continuare a giocare
                        conn.send("OK".encode('utf-8'))
                        
                        print(f"[GAME]carte giocate: {len(card_played)}")
                        print(f"[GAME]carta giocata: {card}")
                        
                    #se la carta è diversa dalla prima carta giocata
                    else:
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "PLAYER", selected_index])
                        #termino il turno del giocatore
                        conn.send("STOP".encode('utf-8'))
                        print(f"[GAME]carta giocata: {card}")
                        print(f"[GAME] il turno del giocatore {player_name} è terminato!")
                        break
                                                      
            #assegno il tris se è stato fatto
            if card_played[0][0] == card_played[0][1] == card_played[0][2]:
                game.tris_counter[turn] += 1
                print(colored(f"[LOG] il {player_name} fatto un tris!", "yellow"))
                self.send_msg(f"il giocatore {player_name} ha fatto un tris!")
                time.sleep(1.5)

            #restituisco le carte se non c'è stato un tris
            else:
                self.send_msg(f"il giocatore {player_name} non ha fatto un tris :(")
                print(colored("[LOG] rimetto a posto le carte", "yellow"))
                update = True

                for cards in card_played:
                    
                    #rimetto la carta nella mano del giocatore di turno
                    if cards[1] == "HAND":
                        game.add_card_player(cards[0], turn)
                    
                    #rimetto la carta nella board
                    elif cards[1] == "BOARD":
                        game.add_board(cards[0], cards[2])
                        game.reset_gameboard()

                    #rimetto la carta nella mano del giocatore dal quale proviene                  
                    elif cards[1] == "PLAYER":
                        game.add_card_player(cards[0], cards[2])    
                        
            #cambio il turno
            if turn == 2:
                turn = 0
            else:
                turn += 1

# funzione per fare clear indipendente dal sistema operativo
def clear():

    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

#main
if __name__ == "__main__":
    
    clear()

    print (colored(r"""        
░▒▓████████▓▒░ ░▒▓███████▓▒░   ░▒▓█▓▒░   ░▒▓██████▓▒░  
   ░▒▓██▓▒░    ░▒▓█▓▒  ▒▓█▓▒░  ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ 
   ░▒▓██▓▒░    ░▒▓█▓▒  ▒▓█▓▒░  ░▒▓█▓▒░  ░▒▓█▓▒  ▒▓█▓▒░ 
   ░▒▓██▓▒░    ░▒▓███████▓▒░   ░▒▓█▓▒░  ░▒▓█▓▒  ▒▓█▓▒░ 
   ░▒▓██▓▒░    ░▒▓█▓▒  ▒▓█▓▒░  ░▒▓█▓▒░  ░▒▓█▓▒  ▒▓█▓▒░ 
   ░▒▓██▓▒░    ░▒▓█▓▒  ▒▓█▓▒░  ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░ 
   ░▒▓██▓▒░    ░▒▓█▓▒  ▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓██████▓▒░                                                                                                           
                                               """, "light_magenta", attrs=["blink"]))
    
    print(colored("Benvenuti alla interfaccia server!","yellow", attrs=["bold"]))
    
    while True:
        print("\nMenu:")
        print("[1] Avvia il Server")
        print("[2] Esci")
        
        choice = input(colored("-->", attrs=["bold", "blink"]))
        
        if choice == "1":
            server = GameServer()
            server.start_server()
            server.start_game()

        elif choice == "2":
            print("Uscendo...")
            break
        else:
            print("Invalid choice. Please try again.")

