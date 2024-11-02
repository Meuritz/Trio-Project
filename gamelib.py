import random

class Trio:
    #inizializzo le varibili e preparo il gioco
    def __init__(self, players):
        
        self.deck = []
        self.board = []
        self.player_hand = []           #this 3 list rely on the fact that every position corresponds to a player
        self.player = players           # ex index1, will be the hand of the player whit index 1, and the tris that
        self.tris_counter = [0 , 0, 0]          #he has done in the game
        self.buffer = []


    
    #preparo il gioco
    def prepare_game(self):
        
        #creo il mazzo e lo mischio
        for x in range(13):
            for y in range(3):
                if (x != 0):
                    self.deck.append(x)
        random.shuffle(self.deck)

        #metto le carte nelle mani dei giocatori
        for x in range(3):
            temp = []
            for y in range(9):
                temp.append(self.deck.pop())
            self.player_hand.append(temp)

        #metto le carte rimaste nella board
        for x in self.deck:
            self.board.append(x)
  
    #funzione per stampare le carte dei giocatori
    def print_cards(self, player):
        
        self.player_hand[player].sort()

        return str(self.player_hand[player])

    #funzione per ottenere le carte della board
    def get_board(self):
        return self.board

    #funzione per rimuove una determinata carta dalla board, in caso di tris
    def remove_board(self, x):
        self.board.remove(x)