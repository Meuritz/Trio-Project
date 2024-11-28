import socket
from os import system, name
from termcolor import colored
import time

# Ip e porta a cui connettersi
SERVER_HOST = "localhost"
SERVER_PORT = 60420


#funzione per connetersi al server di gioco
def start_client():
    
    # Creiamo un socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # connettiamo il socket al server
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connesso al server: {SERVER_HOST}:{SERVER_PORT}")
     
    # prendo in input l'username e lo mando al server
    username = input("inserisci il tuo username\n -->")
    client_socket.send(username.encode('utf-8'))

    # ricevo il messaggio di benvenuto dal server e lo stampo
    msg = client_socket.recv(1024).decode('utf-8')
    print(msg)

    return client_socket


# funzione di clear indipendente dal sistema in uso
def clear():

    # Windows
    if name == 'nt':
        _ = system('cls')

    # Unix(linux e mac)
    else:
        _ = system('clear')

#per ricevere dal server e stampare la carte in mano e la board
def update_cards(client_socket):
    
    clear()

    for _ in range(5):
        print("\n")
    print(colored("======================================================================","cyan" ,attrs=["blink", "bold"]))
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
    print(colored("======================================================================","cyan" ,attrs=["blink", "bold"]))
    client_socket.send("DONE".encode('utf-8'))

#per ricevere e stampare messaggi dal server 
def recv_message(client_socket):
    
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if message == "MESSAGE":
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
            client_socket.send("READY".encode('utf-8'))
        
        elif message == "DONE":
            #print("All messages received and printed")
            client_socket.send("DONE".encode('utf-8'))
            break
    print(colored("======================================================================","cyan" ,attrs=["blink", "bold"]))    

#funzione per ricevere e stampare un singolo messaggio
def recv_msg(client_socket):
    
    message = client_socket.recv(1024).decode('utf-8')
    print(message)      
    
#il gioco vero e proprio (loop)
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
        
        # stampo i messaggi se ce ne sono
        if message == "UPDATE_MSG":
            recv_message(client_socket)
        
        #serve per inviare dei messaggi singoli
        if message == "MSG":
            recv_msg(client_socket)

        #per chiudere il gioco lato client
        if message == "END":
            
            result = client_socket.recv(1024).decode('utf-8')

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
               client_socket.send("DONE".encode('utf-8'))
               time.sleep(5)
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
                client_socket.send("DONE".encode('utf-8'))
                time.sleep(5)
                break

        # loop per giocare, quando il giocatore è di turno
        elif message == "PLAY":
            print("è il tuo turno!")
            
            #fino a 3 
            for i in range(3):
                
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

                    # stampo le carte giocate in precendenza e l'ultima carta giocata
                    if client_socket.recv(1024).decode('utf-8') == "UPDATE_MSG":
                        recv_message(client_socket)

                    #aspetto che il server mi dica se posso continuare
                    response = client_socket.recv(1024).decode('utf-8')
                    print(f"[LOG] response = {response}") 

                    #se il server ci manda "STOP" torniamo nel loop principale
                    if response == "STOP":
                        break
                
                # carta dalla board
                elif move == "1":
                    
                    # prendo in input la carta giocata e la mando al server
                    card = input("Quale carta vuoi scoprire? [0-8]\n -->")
                    client_socket.send(card.encode("utf-8"))

                    #ricevo gli aggiornamenti
                    if client_socket.recv(1024).decode('utf-8') == "UPDATE":
                        update_cards(client_socket)
                    
                    # stampo le carte giocate in precendenza e l'ultima carta giocata
                    if client_socket.recv(1024).decode('utf-8') == "UPDATE_MSG":
                        recv_message(client_socket)

                    #aspetto che il server mi dica se posso continuare
                    response = client_socket.recv(1024).decode('utf-8')
                    print(f"[LOG] response = {response}") 

                    if response == "STOP":
                        break
                

                # carta da un giocatore
                elif move == "2":
                    
                    print("Da quale giocatore?")
                        
                    name = []
                    
                    name.append(client_socket.recv(1024).decode('utf-8'))
                    print(name[0])
                    client_socket.send("NEXT".encode("utf-8"))
                    
                    name.append(client_socket.recv(1024).decode('utf-8'))
                    print(name[1])
                    client_socket.send("DONE".encode("utf-8"))
                    
                    #ciclo fino a quando il giocatore non sceglie un opzione valida tra i giocatori
                    while True:
                        player = input("-->")
                        
                        if  0 <= int(player) <= 1:
                            #mando il giocatore scelto al server ed esco
                            client_socket.send(player.encode('utf-8'))
                            break
                        else:
                            print("scelta non valida!")
                    print("Carta alta o bassa? \n[0]Alta\n[1]Bassa")
                    #ciclo fino a quando il giocatore non sceglie un opzione valida tra alta/bassa
                    while True:
                        player = input("-->")
                        
                        if  0 <= int(player) <= 1:
                            #mando la scelta al server ed esco
                            client_socket.send(player.encode('utf-8'))
                            break
                        else:
                            print("scelta non valida!")
                    
                    #ricevo gli aggiornamenti
                    if client_socket.recv(1024).decode('utf-8') == "UPDATE":
                        update_cards(client_socket)
                    
                    # stampo le carte giocate in precendenza e l'ultima carta giocata
                    if client_socket.recv(1024).decode('utf-8') == "UPDATE_MSG":
                        recv_message(client_socket)

                    #aspetto che il server mi dica se posso continuare
                    response = client_socket.recv(1024).decode('utf-8')
                    print(f"[LOG] response = {response}") 

                    if response == "STOP":
                        break
                    
                                       
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
    print(colored("[1] Connettiti e gioca", "light_magenta"))
    print(colored("[2] Esci", "light_red"))
    print(colored("Version 0.0.1 @Meuritz", "light_yellow"))
    print(colored("Seleziona un opzione:", "light_green"))
    choice = input(colored("-->", "light_blue", attrs=["blink"]))
    
    if choice == "1":
        client_loop()
    elif choice == "2":
        print("Uscendo...")
        break
    else:
        print("Scelta non valida riprova")
        time.sleep(3)
