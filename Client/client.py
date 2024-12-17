import socket
from os import system, name
from termcolor import colored
import time

class client:

    #apre il socket, ed invia un messaggio
    def __init__(self, host, port):
        
        # Creo un socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connettiamo il client al server
        self.client_socket.connect((host, port))
        print(f"Connesso al server: {host}:{port}")

        # prendo in input l'username e lo mando al server
        self.username = input("inserisci il tuo username\n -->")
        self.client_socket.send(self.username.encode('utf-8'))

        # ricevo un messaggio dal server
        msg = self.client_socket.recv(1024).decode('utf-8')
        print(msg)

        #varibile punteggio giocatore
        self.points = 0
    
    #per ricevere dal server e stampare la carte in mano e la board
    def recv_Game(self):
        
        clear()
        
        #nome e punteggio giocatori
        print(colored("Tris effettuati:", "green"))
        points = self.client_socket.recv(1024).decode('utf-8')
        print(points)

        #chiedo il prossimo pacchetto
        self.client_socket.send("NEXT".encode('utf-8'))

        print(colored("======================================================================","cyan" ,attrs=["blink", "bold"]))
        
        #ricevo e stampo la board
        print("Carte nella board:")
        board = self.client_socket.recv(1024).decode('utf-8')
        print(board)
        
        #chiedo il prossimo pacchetto
        self.client_socket.send("NEXT".encode('utf-8'))

        #ricevo e stampo le carte in mano
        print("Carte in Mano:")
        hand = self.client_socket.recv(1024).decode('utf-8')
        print(hand)
        print(colored("======================================================================","cyan" ,attrs=["blink", "bold"]))
        self.client_socket.send("DONE".encode('utf-8'))

    #per ricevere e stampare messaggi dal server 
    def recv_Played_Cards(self):
        
        while True:
            
            message = self.client_socket.recv(1024).decode('utf-8')
            
            if message == "MESSAGE":
                message = self.client_socket.recv(1024).decode('utf-8')
                print(message)
                self.client_socket.send("READY".encode('utf-8'))
            
            elif message == "DONE":
                self.client_socket.send("DONE".encode('utf-8'))
                break

        print(colored("======================================================================","cyan" ,attrs=["blink", "bold"]))

    #funzione per ricevere e stampare un singolo messaggio
    def recv_Msg(self):
        
        message = self.client_socket.recv(1024).decode('utf-8')
        print(message)

    #il gioco vero e proprio (loop)
    def client_loop(self):

        #loop del gioco
        while True:
            
            message = self.client_socket.recv(1024).decode('utf-8')
            print(f"[LOG]: {message}")
            
            # se ricevo update aggiorno le carte 
            if message == "UPDATE":
                self.recv_Game()
            
            # stampo i messaggi se ce ne sono
            if message == "UPDATE_MSG":
                self.recv_Played_Cards()
            
            #serve per inviare dei messaggi singoli
            if message == "MSG":
                self.recv_Msg()

            #termina la partita
            if message == "END":
                
                result = self.client_socket.recv(1024).decode('utf-8')

                if result == "VICTORY":
                    clear()
                    print(colored(r"""
        .##.....##.####.########.########..#######..########..####....###...
        .##.....##..##.....##.......##....##.....##.##.....##..##....##.##..
        .##.....##..##.....##.......##....##.....##.##.....##..##...##...##.
        .##.....##..##.....##.......##....##.....##.########...##..##.....##
        ..##...##...##.....##.......##....##.....##.##...##....##..#########
        ...##.##....##.....##.......##....##.....##.##....##...##..##.....##
        ....###....####....##.......##.....#######..##.....##.####.##.....##
        """, "green", attrs=["blink"]))
                    self.client_socket.send("DONE".encode('utf-8'))
                    time.sleep(5)
                    #chiudo la connessione
                    self.client_socket.close()
                    break
                else:
                    clear()
                    print(colored(r"""
    ..######...######...#######..##....##.########.####.########.########....###...
    .##....##.##....##.##.....##.###...##.##........##.....##.......##......##.##..
    .##.......##.......##.....##.####..##.##........##.....##.......##.....##...##.
    ..######..##.......##.....##.##.##.##.######....##.....##.......##....##.....##
    .......##.##.......##.....##.##..####.##........##.....##.......##....#########
    .##....##.##....##.##.....##.##...###.##........##.....##.......##....##.....##
    ..######...######...#######..##....##.##.......####....##.......##....##.....##
    """, "red", attrs=["blink"]))
                    self.client_socket.send("DONE".encode('utf-8'))
                    time.sleep(5)
                    #chiudo la connessiones
                    self.client_socket.close()
                    break

            # loop per giocare, quando il giocatore è di turno
            elif message == "PLAY":
                print(f"{self.username} è il tuo turno!")
                
                #fino a 3 
                for i in range(3):
                    
                    # il giocatore decide cosa vuole fare
                    print(colored("Fai la tua mossa!", "yellow"))
                    print(colored("0: carta da mano", "red"))
                    print(colored("1: carta dalla board", "green"))
                    print(colored("2: carta da un giocatore", "blue"))
                    move = ""
                    
                    # ciclo fino a che il giocatore non sceglie un opzione valida
                    while True:
                        move = input("-->")
                        
                        if  0 <= int(move) <= 2:
                            self.client_socket.send(move.encode('utf-8'))
                            break
                        else:
                            print("scelta non valida!")

                    # carta da mano
                    if move == "0":

                        # prendo in input la carta giocata e la mando al server
                        while True:
                            
                            card = input("Quale carta vuoi giocare? [0-8]\n -->")
                            
                            if 0 <= int(card) <= 8:
                                self.client_socket.send(card.encode("utf-8"))
                                break
                            else:
                                print("scelta non valida!")
                        
                        #ricevo gli aggiornamenti
                        if self.client_socket.recv(1024).decode('utf-8') == "UPDATE":
                            self.recv_Game()

                        # stampo le carte giocate in precendenza e l'ultima carta giocata
                        if self.client_socket.recv(1024).decode('utf-8') == "UPDATE_MSG":
                            self.recv_Played_Cards()

                        #aspetto che il server mi dica se posso continuare
                        response = self.client_socket.recv(1024).decode('utf-8')
                        print(f"[LOG] response = {response}") 

                        #se il server ci manda "STOP" torniamo nel loop principale
                        if response == "STOP":
                            break
                    
                    # carta dalla board
                    elif move == "1":
                        
                        # prendo in input la carta giocata e la mando al server
                        while True:
                            
                            card = input("Quale carta vuoi scoprire? [0-8]\n -->")
                            
                            if 0 <= int(card) <= 8:
                                self.client_socket.send(card.encode("utf-8"))
                                break
                            else:
                                print("scelta non valida!")

                        #ricevo gli aggiornamenti
                        if self.client_socket.recv(1024).decode('utf-8') == "UPDATE":
                            self.recv_Game()
                        
                        # stampo le carte giocate in precendenza e l'ultima carta giocata
                        if self.client_socket.recv(1024).decode('utf-8') == "UPDATE_MSG":
                            self.recv_Played_Cards()

                        #aspetto che il server mi dica se posso continuare
                        response = self.client_socket.recv(1024).decode('utf-8')
                        print(f"[LOG] response = {response}") 

                        if response == "STOP":
                            break
                    

                    # carta da un giocatore
                    elif move == "2":
                        
                        print("Da quale giocatore?")
                            
                        name = []
                        
                        name.append(self.client_socket.recv(1024).decode('utf-8'))
                        print(name[0])
                        self.client_socket.send("NEXT".encode("utf-8"))
                        
                        name.append(self.client_socket.recv(1024).decode('utf-8'))
                        print(name[1])
                        self.client_socket.send("DONE".encode("utf-8"))
                        
                        #ciclo fino a quando il giocatore non sceglie un opzione valida tra i giocatori
                        """aggiungere un modo per controllare le carte gia scoperte, per non farle riselezionare"""
                        while True:
                            player = input("-->")
                            
                            if  0 <= int(player) <= 1:
                                #mando il giocatore scelto al server ed esco
                                self.client_socket.send(player.encode('utf-8'))
                                break
                            else:
                                print("scelta non valida!")
                        
                        print("Carta alta o bassa? \n[0]Alta\n[1]Bassa")
                        #ciclo fino a quando il giocatore non sceglie un opzione valida tra alta/bassa
                        while True:
                            player = input("-->")
                            
                            if  0 <= int(player) <= 1:
                                #mando la scelta al server ed esco
                                self.client_socket.send(player.encode('utf-8'))
                                break
                            else:
                                print("scelta non valida!")
                        
                        #ricevo gli aggiornamenti
                        if self.client_socket.recv(1024).decode('utf-8') == "UPDATE":
                            self.recv_Game()
                        
                        # stampo le carte giocate in precendenza e l'ultima carta giocata
                        if self.client_socket.recv(1024).decode('utf-8') == "UPDATE_MSG":
                            self.recv_Played_Cards()

                        #aspetto che il server mi dica se posso continuare
                        response = self.client_socket.recv(1024).decode('utf-8')
                        print(f"[LOG] response = {response}") 

                        if response == "STOP":
                            break


# funzione di clear indipendente dal sistema in uso
def clear():

    # Windows
    if name == 'nt':
        _ = system('cls')

    # Unix(linux e mac)
    else:
        _ = system('clear')

while True:
    
    clear()

    print(colored(""" 
████████╗██████╗ ██╗ ██████╗ 
╚══██╔══╝██╔══██╗██║██╔═══██╗
   ██║   ██████╔╝██║██║   ██║                             
   ██║   ██╔══██╗██║██║   ██║
   ██║   ██║  ██║██║╚██████╔╝                                           
   ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝                                               
""","cyan", attrs=["blink"]))
    print(colored("[1] Connettiti e gioca", "green"))
    print(colored("[2] gioca in localhost", "light_magenta"))
    print(colored("[3] Esci", "light_red"))
    print(colored("Version 0.0.9 @Meuritz", "light_yellow"))
    print(colored("Seleziona un opzione:", "light_green"))
    choice = input(colored("-->", "light_blue", attrs=["blink"]))
    
    #connessione ad un server specifico
    if choice == "1":
        try:
            
            ip = input("Inserisci l'indirizzo IP del server di gioco: \n -->")
            
            game = client(str(ip), 60420)
            game.client_loop()
            
        except:
            print("Impossibile stabilire una connessione")
            time.sleep(3)
            continue
    
    #gioco in localhost
    elif choice == "2":
        try:
            game = client("localhost", 60420)
            game.client_loop()
        except:
            print("Impossibile stabilire una connessione")
            time.sleep(3)
            continue
    
    #chiude il client
    elif choice == "3":
        print("Uscendo...")
        break
    else:
        print("Scelta non valida riprova")
        time.sleep(3)
