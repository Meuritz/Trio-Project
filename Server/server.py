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
        self.connected_players = 0
        self.login_lock = threading.Lock() #per evitare che più utenti agiscano allo stesso tempo su "players"
        self.start = threading.Event() #per far partire la partita una volta che sono entrati 3 giocatori
        

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
        
        # ricevo l'username dal client
        username = conn.recv(1024).decode('utf-8')
        print(f"[PLAYER] {username} da {addr}")

        # aggiungo i dati del giocatore in memoria
        with self.login_lock:
            self.add_player(username, conn, addr)
        
        # stampo il numero di giocatori connessi
        print(f"{len(self.players)} giocatori connessi")

        # mando un messaggio al client
        welcome_message = f"Benvenut3 {username}! il gioco iniziera a breve.."
        conn.send(welcome_message.encode('utf-8'))

        # aspetta fino a che non entrano 3 giocatori
        self.start.wait()
        time.sleep(1)

        # da qui inizia il gioco
        while True:
            pass
    
    #funzione principale del server
    def start_server(self):
       
        # bind del server
        self.server_socket.bind((self.host, self.port))

        # il server rimane in ascolto
        self.server_socket.listen(2)

        print(colored(f"Server online su {self.host} ed in ascolto sulla porta {self.port}", color="green"))

        # gestisco le connessioni
        while True:
            
            # accetto le connessioni fino ad un max di 3, e creo un thread per ogni connessione
            if (self.connected_players) != 3:

                # accetta la connessione
                conn, addr = self.server_socket.accept()

                # avvia un thread per gestire la connessione
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))

                # avvia il thread appena creato
                thread.start()

                #aumento di 1(tiene conto dei giocatori connessi)
                self.connected_players += 1
                
            #quando ci sono 3 giocatori
            if (len(self.players)) == 3: 
                
                print(colored("\nTutti i giocatori sono connessi, inizio la partita...", "green"))
                time.sleep(1) 
                
                #sblocco il lock del gioco
                self.start.set()
                break
        
    #Funzione per mandare la board e la mano a ciuscun giocatore
    def send_Game(self, game):
            
            ack = 0
            
            for player in self.players:
                
                conn = player[1]

                #indico al client che sto per inviare Board e Carte
                conn.send("UPDATE".encode('utf-8'))
                
                #manda i punteggi dei giocatori
                conn.send(game.get_Points().encode('utf-8'))

                #aspetto conferma prima di continuare ad inviare
                if conn.recv(1024).decode('utf-8') == "NEXT":
                    pass

                #mando la board(coperta)
                conn.send(game.get_gameboard().encode('utf-8'))

                #aspetto conferma prima di continuare ad inviare
                if conn.recv(1024).decode('utf-8') == "NEXT":
                    pass
                
                #mando le carte
                conn.send(game.print_cards(self.players.index(player)).encode('utf-8'))

                #prima di uscire aspetto che tutti i client abbiano mandato la conferma finale
                if conn.recv(1024).decode('utf-8') == "DONE":
                    ack += 1

            #stampo l'esito del invio
            if(ack == 3):
                print(colored("[SERVER] Carte inviate con successo!", "green"))
            else:
                print(colored("[SERVER] Errore nel invio delle carte", "red"))

    #per mandare le carte che sono state giocate durante il turno
    def send_Played_Cards(self, messages):
        
        ack = 0
        
        #per ogni giocatore
        for player in self.players:
            
            conn = player[1]

            # dico al client che sto per inviare dei messaggi
            conn.send("UPDATE_MSG".encode('utf-8'))

            # mando i messaggi ad ogni client 
            for card_message in messages:
                print(colored(f"[SERVER] Inviando messaggio a {player[0]}: {card_message}", "yellow"))  # Print the message being sent
                
                #invio del messaggio
                while True:    
                    try:
                        conn.settimeout(3)    
                        conn.send("MESSAGE".encode('utf-8'))
                        conn.send(card_message.encode('utf-8'))

                        # aspetto che il client mi mandi conferma di ricezione
                        if conn.recv(1024).decode('utf-8') == "READY":
                            conn.settimeout(None)
                            print("[LOG]: invio riuscito!")
                        
                    except socket.timeout:
                        print("[LOG]: invio fallito, riprovo")
                        continue
                    
                    #se l'invio è avvenuto
                    break
                
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
    
    # manda un singolo messaggio a tutti i client
    def send_Msg(self, message):
        
        for player in self.players:
            conn = player[1]
            conn.send("MSG".encode('utf-8'))
            conn.send(message.encode('utf-8'))
    
    # recupera i nomi dei giocatori eccetto quello di turno
    def get_player_choice(self, turn):
        """
        questa funzione prende i nomi dei giocatori eccetto quello del giocatore di turno
        e li ritorna
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
    
    #per chiudere il socket del server
    def close_connection(self):
        self.server_socket.close()

    # Funzione principale del gioco
    def start_game(self):
        
        update = True
        turn = 0

        #passiamo i nomi dei giocatori alla classe del gioco
        player_name = [player[0] for player in self.players]
        game = Trio(player_name)
        game.prepare_game()

        #fino a che un giocatore non arriva a 3 tris
        while(game.tris_counter[0] != 3 and game.tris_counter[1] != 3 and game.tris_counter[2] != 3):
                    
            #se ce stato un cambiamento nelle carte dei giocatori le aggiorno
            if update == True:
                self.send_Game(game)
                update = False
            
            player = self.players[turn] #giocatore
            player_name = player[0] #nome del giocatore di turno
            conn = player[1] #per comunicare con il giocatore
            
            card_played = [] #le carte giocate nel turno
            messages = [] #per comunicare le carte giocate  
            
            #mando il client del giocatore di turno in modalità "attiva"
            conn.send("PLAY".encode('utf-8'))

            #gioca fino ad un massimo di 3 turni
            for i in range(3):
                
                print(colored(f"[GAME]turno del giocatore {player_name}", "cyan"))

                #ricevo la mossa dal giocatore
                move = conn.recv(1024).decode('utf-8')
                print(colored(f"[GAME] Move = {move}", "yellow"))
                
                #0: Carta da mano
                if move == "0":

                    #recupero la carta
                    card_index = int(conn.recv(1024).decode('utf-8'))
                    card = game.player_hand[turn][card_index]
                    messages.append(f"{player_name} ha giocato un {card}")
                    
                    #la rimuovo dalla mano del giocatore
                    game.player_hand[turn].remove(card)

                    #mando le carte aggiornate
                    self.send_Game(game)
                    
                    #mando le carte giocate in precedenza
                    self.send_Played_Cards(messages)
                    

                    #se la carta è uguale alla prima giocata o è la prima
                    if len(card_played) == 0 or card == card_played[0][0]:
                        
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "HAND"])
                        
                        #dico al client che puo continuare a giocare
                        conn.send("OK".encode('utf-8'))

                        print(colored(f"[GAME]carte giocate: {len(card_played)}", "cyan"))
                        print(colored(f"[GAME]carta giocata: {card}", "cyan"))
                        
                        
                    #se la carta è diversa dalla prima carta giocata
                    else:
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "HAND"])
                        
                        #termino il turno del giocatore
                        conn.send("STOP".encode('utf-8'))
                        print(colored(f"[GAME]carta giocata: {card}", "cyan"))
                        print(colored(f"[GAME] il turno del giocatore {player_name} è terminato!", "yellow"))
                        break
                    
                #1: scopre una carta dalla board
                elif move == "1":

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
                    self.send_Game(game)
                    
                    #mando le carte giocate in precedenza
                    self.send_Played_Cards(messages)

                    #se la carta è uguale alla prima giocata o è la prima
                    if len(card_played) == 0 or card == card_played[0][0]:
                        
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "BOARD", card_index])
                        #dico al client che puo continuare a giocare
                        conn.send("OK".encode('utf-8'))
                        
                        print(colored(f"[GAME]carte giocate: {len(card_played)}", "cyan"))
                        print(colored(f"[GAME]carta giocata: {card}", "cyan"))
                        
                    #se la carta è diversa dalla prima carta giocata
                    else:
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "BOARD", card_index])
                        conn.send("STOP".encode('utf-8'))
                        print(colored(f"[GAME]carta giocata: {card}", "cyan"))
                        print(colored(f"[GAME] il turno del giocatore {player_name} è terminato!", "yellow"))
                        break
             
                #2 chiedi una carta ad uno dei giocatori
                elif move == "2":
                    
                    """
                    questa sezione di codice permette al client di scegliere un giocatore
                    e quale carte vuole prendere tra alta e bassa
                    """

                    #recupero i nomi dei giocatori
                    names = self.get_player_choice(turn)
                    
                    #mando i nomi dei giocatori
                    conn.send(names[0].encode('utf-8'))
                    if conn.recv(1024).decode('utf-8') == "NEXT":
                        pass
                    
                    conn.send(names[1].encode('utf-8'))
                    if conn.recv(1024).decode('utf-8') == "DONE":
                        pass
                    
                    #elaboro i nomi presi precedentemente
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
                    self.send_Game(game)
                    
                    #mando le carte giocate in precedenza
                    self.send_Played_Cards(messages)
                
                    #se la carta è uguale alla prima giocata o è la prima
                    if len(card_played) == 0 or card == card_played[0][0]:
                        
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "PLAYER", selected_index])
                        #dico al client che puo continuare a giocare
                        conn.send("OK".encode('utf-8'))
                        
                        print(colored(f"[GAME]carte giocate: {len(card_played)}", "cyan"))
                        print(colored(f"[GAME]carta giocata: {card}", "cyan"))
                        
                    #se la carta è diversa dalla prima carta giocata
                    else:
                        #la aggiungo alle carte giocate nel turno, con il codice corrispettivo
                        card_played.append([card, "PLAYER", selected_index])
                        #termino il turno del giocatore
                        conn.send("STOP".encode('utf-8'))
                        print(colored(f"[GAME]carta giocata: {card}", "cyan"))
                        print(colored(f"[GAME] il turno del giocatore {player_name} è terminato!", "yellow"))
                        break
                                                      
            """
            In questa parte di codice controlliamo se è stato effettuato un tris, o un tris di 7, in caso contrario
            rimettiamo a posto le carte che sono state prese 
            """            
            #in caso di tris di 7
            if card_played[0][0] == 7 and card_played[1][0] == 7 and card_played[2][0] == 7:
                game.tris_counter[turn] = 3
                print(colored(f"[LOG] il giocatore {player_name} fatto un tris!", "yellow"))
                self.send_Msg(f"il giocatore {player_name} ha fatto un tris di 7!")
                time.sleep(4)
                
            #in caso di tris normale
            elif card_played[0][0] == card_played[1][0] == card_played[2][0]:
                game.tris_counter[turn] += 1
                print(colored(f"[LOG] il giocatore {player_name} fatto un tris!", "yellow"))
                self.send_Msg(f"il giocatore {player_name} ha fatto un tris!")
                
                #tolgo definitivamente le carte prese dalla board
                for card in card_played:
                    if card[1] == "BOARD":
                        game.remove_from_board(card[2])
                        game.reset_gameboard()
                time.sleep(4)
                
                #aggiorno le carte
                update = True
                
            #restituisco le carte se non c'è stato un tris
            else:
                self.send_Msg(f"il giocatore {player_name} non ha fatto un tris :(")
                time.sleep(4)
                print(colored("[LOG] rimetto a posto le carte", "yellow"))

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
                
                update = True
                        
            #cambio il turno
            if turn == 2:
                turn = 0
            else:
                turn += 1

        #assegno la vittoria
        for player, tris in zip(self.players, game.tris_counter):

            conn = player[1]
            
            conn.send("END".encode('utf-8'))

            if tris == 3:
                conn.send("VICTORY".encode('utf-8'))
            else:
                conn.send("LOSS".encode('utf-8'))
            
            if conn.recv(1024).decode('utf-8') == "DONE":
                pass

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
    
    while True:
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

        print("\nMenu:")
        print("[1] Avvia il Server")
        print("[2] Esci")
        
        choice = input(colored("-->", attrs=["bold", "blink"]))
        
        if choice == "1":
            
            server = GameServer()
            
            server.start_server()
            server.start_game()
            server.close_connection()

        elif choice == "2":
            print("Uscendo...")
            break
        else:
            print("Invalid choice. Please try again.")

