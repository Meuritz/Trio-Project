import random

class Trio:
    #inizializzo le varibili e preparo il gioco
    def __init__(self ):
        
        self.deck = []
        self.player_hand = []
        self.board = []
        #self.player = players

    
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
    def print_cards(self):
        
        pass


x = Trio()
x.prepare_game()
print(x.player_hand)
print(x.board)
