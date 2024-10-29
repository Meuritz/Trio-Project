import random

class Trio:
    def __init__(self):
        
        self.player_hand = []
        self.board = []
        self.deck = []

    def prepare_deck(self):
        for x in range(13):
            for y in range(3):
                if (x != 0):
                    self.deck.append(x)
        random.shuffle(self.deck)

    def prepare_game(self, players):
        """
        Purpose: this method sets the game up before playing
        """
        

x = Trio()

print(x.deck)

x.prepare_deck()

print(x.deck)
    # end def