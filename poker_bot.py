from cards import Suit, Rank, Card, Deck, HandRank


def main(): 
    deck = Deck()
    deck.shuffle()

    deck.print_cards()



if __name__ == '__main__': 
    main()