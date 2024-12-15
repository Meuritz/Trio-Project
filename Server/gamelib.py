import random

class Trio:
    #inizializzo le varibili e preparo il gioco
    def __init__(self, players):
        
        self.deck = []

        self.board = []#board 

        self.gameboard = self.hidden_board() #"fake" board

        self.player_name = players

        self.player_hand = []#carte in mano ad i giocatori
        
        self.tris_counter = [0, 0, 0]#contatore dei tris

    #preparo il gioco
    def prepare_game(self):
        
        #creo il mazzo e lo mischio
        for x in range(13):
            for y in range(3):
                if (x != 0):
                    self.deck.append(x)
        random.shuffle(self.deck)

        #metto le carte nelle mani dei giocatori e le sorto
        for x in range(3):
            temp = []
            for y in range(9):
                temp.append(self.deck.pop())
            self.player_hand.append(temp)
            self.player_hand[x].sort()


        #metto le carte rimaste nella board
        for x in self.deck:
            self.board.append(x)
        #inizializzo la gameboard con carte coperte
        self.gameboard = self.hidden_board()
    
    #ordina le carte di un giocatore
    def sort_hand(self, player):
        self.player_hand[player].sort()

    #restituisce le carte di un giocatore
    def print_cards(self, player):
        return str(self.player_hand[player])
    
    #funzione per aggiungere una carta nella mano di un giocatore
    def add_card_player(self, card, index):
        self.player_hand[index].append(card)
        self.sort_hand(index)
    
    #prende la carta più alta dalla mano di un giocatore
    def get_max_card_player(self, player_index):
        return max(self.player_hand[player_index])
    
    #prende la carta più bassa dalla mano di un giocatore
    def get_min_card_player(self, player_index):
        return min(self.player_hand[player_index])

    #funzione per creare una board di carte coperte("fake" board)
    def hidden_board(self):
        
        hidden_board = []
        
        #faccio in modo di stampare spazi vuoti se una carta è stata rimossa
        for card in self.board:
            
            if not card:
                hidden_board.append(" ")
            else:
                hidden_board.append("X")
        
        return hidden_board

    #funzione per ottenere le carte dalla "fake" board
    def get_gameboard(self):
        return str(self.gameboard)
    
    #funzione per ottenere una carta dalla board
    def get_from_board(self, x):
        return self.board[x]
    
    #funzione per aggiungere una determinata carta alla board
    def add_board(self, value, x):
        self.board[x] = value

    #funzione per rimuove una determinata carta dalla board
    def remove_from_board(self, x):
        self.board[x] = ""
    
    #funzione per scoprire una carta dalla "fake" board
    def draw_from_board(self, x):
        self.gameboard[x] = self.get_from_board(x)

    #per ricoprire le carte
    def reset_gameboard(self):
        self.gameboard = self.hidden_board()

    #prende i punteggi dei giocatori
    def get_Points(self):
        
        points_scored = ""

        for i in range(3):
            points_scored += f"{self.player_name[i]}:  {self.tris_counter[i]} | "

        return points_scored
    
