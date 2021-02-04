import random



class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        D = {'6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'valet': 2, 'dama': 3, 'korol': 4, 'tuz': 11}
        self.value = D[rank]  # Присваиваем карте очки

    def __repr__(self):
        return str(self.rank) + str(self.suit)

    def to_dickt(self):
        return { 'rank': self.rank, 'suit': self.suit }


class Deck:
    def __init__(self, **kwargs):
        if kwargs:
            self.card_deck = []
            for i in kwargs.values():
                for j in i:
                    self.card_deck.append(Card(**j))
        else:
            ranks = ['6', '7', '8', '9', '10', 'valet', 'dama', 'korol', 'tuz']
            suits = ['♥', '♣', '♦', '♠']
            self.card_deck = [Card(i, j) for j in suits for i in ranks]  # создаём колоду
            random.shuffle(self.card_deck)  # Перемешиваем колоду

    def __repr__(self):
        return str(self.card_deck)

    def shuffle(self):
        random.shuffle(self.card_deck)

    def give_card(self):
        return self.card_deck.pop()

    def to_dickt(self):
        d = {}
        d['card_deck'] = [card.to_dickt() for card in self.card_deck]
        return d


class PlayersHand:
    def __init__(self, **kwargs):
        if kwargs:
            self.Hand_value = kwargs['Hand_value']
            self.Hand = []
            for i in kwargs['hand']:
                self.Hand.append(Card(**i))
        else:
            self.Hand = []
            self.Hand_value = 0

    def __repr__(self):
        return ', '.join(str(i) for i in self.Hand)

    def get_card(self, card):
        self.Hand.append(card)
        self.Hand_value += card.value
        return card

    def tuz_checking(self):
        return self.Hand[0].rank == 'tuz'

    def to_dickt(self):
        d = {}
        d['hand'] = [card.to_dickt() for card in self.Hand]
        d['Hand_value'] = self.Hand_value
        return d
