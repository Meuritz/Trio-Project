import random

class Trio:
    #inizializzo le varibili e preparo il gioco
    def __init__(self, players):
        
        self.deck = []

        self.board = []                      #board effettiva
        self.gameboard = self.hidden_board() #board che viene stampata
        
        self.player_hand = []           #this 3 list rely on the fact that every position corresponds to a player
        self.player = players           # ex index1, will be the hand of the player whit index 1, and the tris that
        
        self.tris_counter = [0, 0, 0]          #counter for tris that have been done

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
    
    #per ordinare le carte di un giocatore
    def sort_hand(self, player):
        self.player_hand[player].sort()

    #funzione per stampare le carte di un giocatore
    def print_cards(self, player):
        return str(self.player_hand[player])

    #funzione per ottenere le carte della board (sono le carte effettive)
    def get_board(self):
        return self.board
    
    #funzione per ottenere le carte dalla gameboard (carte viste dai giocatori)
    def get_gameboard(self):
        return str(self.gameboard)
    
    #funzione per ottenere una carta dalla board
    def get_from_board(self, x):
        return self.board[x]
    
    #funzione per aggiungere una determinata carta alla board
    def add_board(self, value, x):
        self.board[x] = value

    #funzione per rimuove una determinata carta dalla board
    def remove_board(self, x):
        self.board[x] = ""
    
    #funzione per avere una board di carte coperte
    def hidden_board(self):
        
        hidden_board = []
        
        #faccio in modo di stampare spazi vuoti se una carta è stata rimossa
        for card in self.board:
            
            if not card:
                hidden_board.append(" ")
            else:
                hidden_board.append("X")
        
        return hidden_board
    
    #per ricoprire le carte
    def reset_gameboard(self):
        self.gameboard = self.hidden_board()
    
    #funzione per scoprire una carta sulla board
    def draw_from_board(self, x):
        self.gameboard[x] = self.get_from_board(x)