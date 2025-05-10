import random
from enum import Enum
from typing import List, Tuple, Dict, Optional


class Suit(Enum):
    HEARTS = 0
    DIAMONDS = 1
    CLUBS = 2
    SPADES = 3
    
    def __str__(self) -> str:
        suit_symbols = {
            Suit.HEARTS: "♥",
            Suit.DIAMONDS: "♦",
            Suit.CLUBS: "♣",
            Suit.SPADES: "♠"
        }
        return suit_symbols[self]


class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    
    def __str__(self) -> str:
        rank_symbols = {
            Rank.TWO: "2",
            Rank.THREE: "3",
            Rank.FOUR: "4",
            Rank.FIVE: "5",
            Rank.SIX: "6",
            Rank.SEVEN: "7",
            Rank.EIGHT: "8",
            Rank.NINE: "9",
            Rank.TEN: "10",
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
            Rank.ACE: "A"
        }
        return rank_symbols[self]
    
class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"
    
    def __repr__(self) -> str:
        return f"Card({self.rank}, {self.suit})"
    

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self) -> None:
        self.cards = []
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(rank, suit))
    
    def shuffle(self) -> None:
        random.shuffle(self.cards)
    
    def draw(self) -> Card:
        return self.cards.pop()
    
    def draw_multiple(self, count: int) -> List[Card]:
        cards = []
        for _ in range(count):
            cards.append(self.draw())
        return cards
    
    def __len__(self) -> int:
        return len(self.cards)
    
    def print_cards(self) -> None:
        for card in self.cards:
            print(card)
    
    @staticmethod
    def create_deck_without_cards(excluded_cards: List[Card]) -> 'Deck':
        deck = Deck()
        deck.cards = [card for card in deck.cards if card not in excluded_cards]
        return deck
    

class HandRank(Enum):
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9

class HandEvaluator:
    @staticmethod
    def get_rank_counts(cards: List[Card]) -> Dict[Rank, int]:
        rank_counts = {}
        for card in cards:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = 0
            rank_counts[card.rank] += 1
        return rank_counts
    
    @staticmethod
    def get_suit_counts(cards: List[Card]) -> Dict[Suit, int]:
        suit_counts = {}
        for card in cards:
            if card.suit not in suit_counts:
                suit_counts[card.suit] = 0
            suit_counts[card.suit] += 1
        return suit_counts
    
    @staticmethod
    def has_flush(cards: List[Card]) -> Tuple[bool, Optional[Suit]]:
        suit_counts = HandEvaluator.get_suit_counts(cards)
        for suit, count in suit_counts.items():
            if count >= 5:
                return True, suit
        return False, None
    
    @staticmethod
    def has_straight(ranks: List[Rank]) -> Tuple[bool, Optional[Rank]]:
        unique_ranks = sorted(set(ranks), key=lambda r: r.value)
        
        if len(unique_ranks) < 5: 
            return False, None
    
        # ace low 
        if (Rank.ACE in unique_ranks and
            Rank.TWO in unique_ranks and
            Rank.THREE in unique_ranks and
            Rank.FOUR in unique_ranks and
            Rank.FIVE in unique_ranks):
            return True, Rank.FIVE
        
        # other straights
        straight_high_card = None
        consecutive_count = 1
        
        for i in range(1, len(unique_ranks)):
            if unique_ranks[i].value == unique_ranks[i-1].value + 1:
                consecutive_count += 1
                if consecutive_count >= 5:
                    straight_high_card = unique_ranks[i]
            elif unique_ranks[i].value > unique_ranks[i-1].value + 1:
                consecutive_count = 1
        
        return straight_high_card is not None, straight_high_card
    
    @staticmethod
    def evaluate_hand(player_cards: List[Card], community_cards: List[Card]) -> Tuple[HandRank, List]:
        all_cards = player_cards + community_cards
        
        # check for flush
        has_flush, flush_suit = HandEvaluator.has_flush(all_cards)
        
        all_ranks = [card.rank for card in all_cards]
        
        # check for straight
        has_straight, straight_high_card = HandEvaluator.has_straight(all_ranks)
        
        # check for straight flush and royal flush
        if has_flush and has_straight:
            flush_cards = [card for card in all_cards if card.suit == flush_suit]
            flush_ranks = [card.rank for card in flush_cards]
            has_straight_flush, straight_flush_high_card = HandEvaluator.has_straight(flush_ranks)
            
            if has_straight_flush:
                if straight_flush_high_card == Rank.ACE:
                    return HandRank.ROYAL_FLUSH, [straight_flush_high_card]
                return HandRank.STRAIGHT_FLUSH, [straight_flush_high_card]
        
        # count rank occurrences for pairs
        rank_counts = HandEvaluator.get_rank_counts(all_cards)
        
        # check for four of a kind
        for rank, count in rank_counts.items():
            if count == 4:
                kickers = sorted([r for r in rank_counts if r != rank], 
                                key=lambda r: r.value, reverse=True)
                return HandRank.FOUR_OF_A_KIND, [rank] + kickers[:1]
        
        # check for full house
        three_of_a_kind = None
        pairs = []
        
        for rank, count in rank_counts.items():
            if count == 3:
                if three_of_a_kind is None or rank.value > three_of_a_kind.value:
                    if three_of_a_kind is not None:
                        pairs.append(three_of_a_kind)
                    three_of_a_kind = rank
            elif count == 2:
                pairs.append(rank)
        
        if three_of_a_kind is not None and pairs:
            # sort pairs for tie-breaking
            pairs.sort(key=lambda r: r.value, reverse=True)
            return HandRank.FULL_HOUSE, [three_of_a_kind, pairs[0]]
        
        # check for flush
        if has_flush:
            flush_cards = [card for card in all_cards if card.suit == flush_suit]
            flush_cards.sort(key=lambda card: card.rank.value, reverse=True)
            return HandRank.FLUSH, [card.rank for card in flush_cards[:5]]
        
        # check for straight
        if has_straight:
            return HandRank.STRAIGHT, [straight_high_card]
        
        # check for three of a kind
        if three_of_a_kind is not None:
            kickers = sorted([r for r in rank_counts if r != three_of_a_kind], 
                            key=lambda r: r.value, reverse=True)
            return HandRank.THREE_OF_A_KIND, [three_of_a_kind] + kickers[:2]
        
        # check for two pair
        if len(pairs) >= 2:
            # sort pairs for tie-breaking
            pairs.sort(key=lambda r: r.value, reverse=True)
            kickers = sorted([r for r in rank_counts if r not in pairs[:2]], 
                            key=lambda r: r.value, reverse=True)
            return HandRank.TWO_PAIR, pairs[:2] + kickers[:1]
        
        # check for one pair
        if pairs:
            kickers = sorted([r for r in rank_counts if r != pairs[0]], 
                            key=lambda r: r.value, reverse=True)
            return HandRank.PAIR, [pairs[0]] + kickers[:3]
        
        # high card
        high_cards = sorted(all_ranks, key=lambda r: r.value, reverse=True)
        return HandRank.HIGH_CARD, high_cards[:5]
    
    @staticmethod
    def compare_hands(player_cards1: List[Card], player_cards2: List[Card], 
                     community_cards: List[Card]) -> int:

        rank1, tiebreakers1 = HandEvaluator.evaluate_hand(player_cards1, community_cards)
        rank2, tiebreakers2 = HandEvaluator.evaluate_hand(player_cards2, community_cards)
        
        # compare hand ranks
        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return 2
        
        # compare tie-breakers
        for tb1, tb2 in zip(tiebreakers1, tiebreakers2):
            if tb1.value > tb2.value:
                return 1
            elif tb1.value < tb2.value:
                return 2
        
        # Push
        return 0
