import time
import math
from cards import Suit, Rank, Card, Deck, HandRank, HandEvaluator
from typing import List

class MCTSNode:
    def __init__(self, parent=None):
        self.parent = parent
        self.wins = 0
        self.simulations = 0
        self.children = {}
        self.untried_actions = []
    
    def ucb1(self, exploration_weight=1.5):
        if self.simulations == 0:
            return float('inf')
        
        exploitation = self.wins / self.simulations
        
        if self.parent is None:
            return exploitation
        
        exploration = exploration_weight * math.sqrt(
            math.log(self.parent.simulations) / self.simulations
        )
        
        return exploitation + exploration
    
    def select_child(self):
        return max(self.children.values(), key=lambda n: n.ucb1())
    
    def expand(self, action):
        child = MCTSNode(parent=self)
        self.children[action] = child
        if action in self.untried_actions:
            self.untried_actions.remove(action)
        return child
    
    def update(self, result):
        self.simulations += 1
        self.wins += result
    
    def is_fully_expanded(self):
        return len(self.untried_actions) == 0


class PokerBot:
    def __init__(self, time_limit=9.8):
        self.time_limit = time_limit
    
    def make_decision(self, my_hole_cards: List[Card], community_cards: List[Card]) -> bool:
        # false = fold, true = stay

        start_time = time.time()
        root = MCTSNode()
        
        # run simulations 
        simulations = 0
        while time.time() - start_time < self.time_limit:
            self.run_simulation(root, my_hole_cards, community_cards)
            simulations += 1
        
        # win probability
        win_probability = root.wins / root.simulations if root.simulations > 0 else 0
        
        # stay or fold
        print(f'Win Probability: {win_probability}')
        return win_probability >= 0.5
    
    def run_simulation(self, root: MCTSNode, my_hole_cards: List[Card], 
                        community_cards: List[Card]):
        known_cards = my_hole_cards + community_cards
        remaining_deck = Deck.create_deck_without_cards(known_cards)
        remaining_deck.shuffle()
        
        # guess oponents hand
        opponent_hole_cards = remaining_deck.draw_multiple(2)
        
        # extend community cards 
        future_community = community_cards.copy()
        cards_needed = 5 - len(future_community)
        if cards_needed > 0:
            future_community.extend(remaining_deck.draw_multiple(cards_needed))
        
        # determine winner
        result = HandEvaluator.compare_hands(my_hole_cards, opponent_hole_cards, future_community)
        
        win = 1 if result == 1 else 0

        
        # selection / backpropagation
        node = root
        while node is not None:
            node.update(win)
            node = node.parent
    
    def estimate_win_probability(self, my_hole_cards: List[Card], community_cards: List[Card], 
        num_simulations: int = 100000) -> float:
        wins = 0
        
        for _ in range(num_simulations):
            known_cards = my_hole_cards + community_cards
            remaining_deck = Deck.create_deck_without_cards(known_cards)
            remaining_deck.shuffle()
            
            # guess opponent's hand
            opponent_hole_cards = remaining_deck.draw_multiple(2)
            
            # extend community cards
            future_community = community_cards.copy()
            cards_needed = 5 - len(future_community)
            if cards_needed > 0:
                future_community.extend(remaining_deck.draw_multiple(cards_needed))
            
            # determine winner
            result = HandEvaluator.compare_hands(my_hole_cards, opponent_hole_cards, future_community)
            
            if result == 1:
                wins += 1
        
        return wins / num_simulations


def play_hand():
    bot = PokerBot()
    deck = Deck()
    deck.shuffle()
    
    # hole cards
    bot_hole_cards = deck.draw_multiple(2)
    opponent_hole_cards = deck.draw_multiple(2)
    
    print("Bot's hole cards:", [str(card) for card in bot_hole_cards])
    
    # pre-flop 
    decision = bot.make_decision(bot_hole_cards, [])
    print(f"Pre-flop decision: {'STAY' if decision else 'FOLD'}")
    
    if not decision:
        print("Bot folds pre-flop. Opponent wins.")
        return
    
    # flop
    flop = deck.draw_multiple(3)
    print("Flop:", [str(card) for card in flop])
    
    # pre-turn 
    decision = bot.make_decision(bot_hole_cards, flop)
    print(f"Pre-turn decision: {'STAY' if decision else 'FOLD'}")
    
    if not decision:
        print("Bot folds after flop. Opponent wins.")
        return
    
    # turn
    turn = deck.draw()
    community_cards = flop + [turn]
    print("Turn:", str(turn))
    
    # pre-river 
    decision = bot.make_decision(bot_hole_cards, community_cards)
    print(f"Pre-river decision: {'STAY' if decision else 'FOLD'}")
    
    if not decision:
        print("Bot folds after turn. Opponent wins.")
        return
    
    # river
    river = deck.draw()
    community_cards.append(river)
    print("River:", str(river))
    
    # determine winner
    print("Opponent's hole cards:", [str(card) for card in opponent_hole_cards])
    
    bot_hand, _ = HandEvaluator.evaluate_hand(bot_hole_cards, community_cards)
    opponent_hand, _ = HandEvaluator.evaluate_hand(opponent_hole_cards, community_cards)
    
    print(f"Bot's hand: {bot_hand.name}")
    print(f"Opponent's hand: {opponent_hand.name}")
    
    result = HandEvaluator.compare_hands(bot_hole_cards, opponent_hole_cards, community_cards)
    
    if result == 1:
        print("Bot wins")
    elif result == 2:
        print("Opponent wins")
    else:
        print("It's a tie")


def main():
    play_hand()


if __name__ == '__main__':
    main()