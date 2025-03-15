import random
import json
import os
from hand_evaluator import evaluate_hand, compare_hands

class PokerEngine:
    """
    Texas Hold'em Poker Game Engine for heads-up matches
    """
    def __init__(self, player1, player2, starting_stack=1000, ante=10):
        self.players = [player1, player2]
        self.starting_stack = starting_stack
        self.ante = ante
        self.stacks = {player1: starting_stack, player2: starting_stack}
        self.deck = []
        self.community_cards = []
        self.player_hands = {player1: [], player2: []}
        self.current_player_idx = 0
        self.pot = 0
        self.round_state = {}
        self.current_bet = 0
        self.game_state = {}
        self.current_round = 0
        self.predefined_community = None
        
    def initialize_round(self, predefined_cards=None):
        """Initialize a new round of poker
        
        Args:
            predefined_cards (dict): Optional dict with predefined cards to use instead of random ones
                                     Format: {'player1': [card1, card2], 'player2': [card1, card2], 
                                             'community': [card1, card2, card3, card4, card5]}
        """
        self.current_round += 1
        self.community_cards = []
        self.player_hands = {player: [] for player in self.players}
        self.pot = 0
        self.current_bet = 0
        
        # Check if players can pay the ante
        for player in self.players:
            if self.stacks[player] < self.ante:
                # Player can't pay ante, they lose
                print(f"{player} can't pay the ante and automatically loses")
                # Award all remaining chips to the opponent
                winner = self.players[1 - self.players.index(player)]
                self.stacks[winner] += self.stacks[player]
                self.stacks[player] = 0
                return winner
        
        # Collect antes
        for player in self.players:
            self.stacks[player] -= self.ante
            self.pot += self.ante
        
        if predefined_cards:
            # Use predefined cards
            self.player_hands[self.players[0]] = predefined_cards['player1']
            self.player_hands[self.players[1]] = predefined_cards['player2']
            
            # Store the predefined community cards for later use
            self.predefined_community = predefined_cards['community']
            
            # Set up a deck that will produce the predefined community cards
            # Note: We won't actually use this deck for dealing community cards,
            # but we'll keep it for backward compatibility and in case we need
            # to deal additional cards
            used_cards = predefined_cards['player1'] + predefined_cards['player2']
            remaining_community = predefined_cards['community']
            
            # Create a deck with the predefined cards first, followed by random ones
            self.deck = []
            for card in remaining_community:
                self.deck.append(card)
                
            # Add random cards for any burn cards and potential future draws
            full_deck = self._create_deck()
            for card in full_deck:
                if card not in used_cards and card not in remaining_community:
                    self.deck.append(card)
        else:
            # Deal normally with random cards
            self.deck = self._create_deck()
            self.predefined_community = None  # No predefined community cards
            
            # Deal hole cards (2 cards per player)
            for player in self.players:
                self.player_hands[player] = [self._deal_card(), self._deal_card()]
            
        # Set up round state information
        self.round_state = {
            'pot': self.pot,
            'community_cards': [],
            'current_bet': 0,
            'min_raise': self.ante * 2
        }
        
        # Initialize game state for first betting round (pre-flop)
        self._update_game_state()
        
        # Determine who starts pre-flop - alternate with each round
        self.current_player_idx = self.current_round % 2
        
        return None  # No winner yet from ante check
        
    def pregenerate_round(self, round_num):
        """
        Pre-generate a round with random cards and save to a JSON file
        
        Args:
            round_num (int): The round number to generate
            
        Returns:
            dict: The generated card data
        """
        # Create a fresh deck
        temp_deck = self._create_deck()
        
        # Deal cards for both players and community
        player1_cards = [temp_deck.pop(), temp_deck.pop()]
        player2_cards = [temp_deck.pop(), temp_deck.pop()]
        
        # Burn one card before flop
        temp_deck.pop()
        community_cards = [temp_deck.pop(), temp_deck.pop(), temp_deck.pop()]
        
        # Burn one card before turn
        temp_deck.pop()
        community_cards.append(temp_deck.pop())
        
        # Burn one card before river
        temp_deck.pop()
        community_cards.append(temp_deck.pop())
        
        # Create and save predefined cards
        card_data = {
            'round': round_num,
            'player1': player1_cards,
            'player2': player2_cards,
            'community': community_cards
        }
        
        # Ensure the poker_rounds directory exists
        os.makedirs("poker_rounds", exist_ok=True)
        
        # Save to JSON file in the poker_rounds folder
        json_path = f"poker_rounds/round_{round_num}_cards.json"
        with open(json_path, 'w') as f:
            json.dump(card_data, f, indent=2)
            
        print(f"Pre-generated cards saved to {json_path}")
        print(f"Player 1 cards: {player1_cards}")
        print(f"Player 2 cards: {player2_cards}")
        print(f"Community cards: {community_cards}")
        
        return card_data
    
    def load_predefined_cards(self, round_num):
        """
        Load predefined cards from a JSON file
        
        Args:
            round_num (int): The round number to load
            
        Returns:
            dict or None: The predefined card data if file exists, None otherwise
        """
        json_path = f"poker_rounds/round_{round_num}_cards.json"
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    card_data = json.load(f)
                return card_data
            except Exception as e:
                print(f"Error loading predefined cards: {e}")
                return None
        return None
    
    def play_round(self):
        """Play a full round of poker"""
        # Initialize round
        ante_winner = self.initialize_round()
        if ante_winner:
            return ante_winner  # Player couldn't pay ante
        
        # Pre-flop betting round
        winner = self._betting_round('preflop')
        if winner:
            return self._end_round(winner)
            
        # Deal flop (3 community cards)
        self._deal_flop()
        
        # Flop betting round
        winner = self._betting_round('flop')
        if winner:
            return self._end_round(winner)
            
        # Deal turn (1 community card)
        self._deal_turn()
        
        # Turn betting round
        winner = self._betting_round('turn')
        if winner:
            return self._end_round(winner)
            
        # Deal river (1 community card)
        self._deal_river()
        
        # River betting round
        winner = self._betting_round('river')
        if winner:
            return self._end_round(winner)
            
        # Showdown
        return self._showdown()
    
    def _betting_round(self, round_name):
        """Execute a betting round, return winner if someone folds"""
        # Reset betting state for this round
        self.current_bet = 0
        acted_players = set()
        all_players_acted = False
        
        # Pre-flop betting order is already determined during initialize_round
        # For post-flop rounds, we preserve the same starting player as pre-flop
        # (We no longer reset to position 0 for post-flop rounds)
        
        # Continue until all players have acted and bets are equal
        while not all_players_acted or any(self.round_state.get(f"player{i}_bet", 0) != self.current_bet for i in range(2) if self.stacks[self.players[i]] > 0):
            current_player = self.players[self.current_player_idx]
            
            # Get player action based on game state
            action = current_player.get_action(self._get_player_view(current_player))
            
            # Process the action
            folded = self._process_action(current_player, action)
            if folded:
                # If player folded, other player wins
                return self.players[1 - self.current_player_idx]
                
            # Mark this player as having acted
            acted_players.add(current_player)
            
            # Check if all players have acted
            all_players_acted = len(acted_players) == len(self.players)
            
            # Move to next player
            self.current_player_idx = (self.current_player_idx + 1) % 2
            
            # Update game state after action
            self._update_game_state()
            
        return None  # No winner yet
        
    def _process_action(self, player, action):
        """Process a player's action"""
        action_type = action['action']
        player_idx = self.players.index(player)
        opponent_idx = 1 - player_idx
        opponent = self.players[opponent_idx]
        
        if action_type == 'fold':
            return True  # Player folded
            
        elif action_type == 'check':
            # Can only check if there's no bet to call
            if self.current_bet > self.round_state.get(f'player{player_idx}_bet', 0):
                # Invalid check, treat as fold
                return True
                
        elif action_type == 'call':
            amount_to_call = self.current_bet - self.round_state.get(f'player{player_idx}_bet', 0)
            # All-in if not enough chips
            amount_to_call = min(amount_to_call, self.stacks[player])
            # Ensure amount is an integer
            amount_to_call = int(amount_to_call)
            self.stacks[player] -= amount_to_call
            self.pot += amount_to_call
            self.round_state[f'player{player_idx}_bet'] = self.round_state.get(f'player{player_idx}_bet', 0) + amount_to_call
            
        elif action_type == 'bet' or action_type == 'raise':
            bet_amount = action['amount']
            # Ensure bet amount is an integer
            bet_amount = int(bet_amount)
            
            # If bet amount is below min_raise, treat as a check
            current_player_bet = self.round_state.get(f'player{player_idx}_bet', 0)
            if bet_amount < self.round_state['min_raise']:
                return self._process_action(player, {'action': 'check'})
            
            # Validate bet amount
            opponent_stack = self.stacks[opponent]
            min_amount = self.current_bet - current_player_bet + self.round_state['min_raise']
            
            # Cap the bet amount at what the opponent can call (current_player_bet + opponent_stack)
            max_bet = current_player_bet + opponent_stack
            bet_amount = min(bet_amount, max_bet)
            
            # If player doesn't have enough for minimum raise, they can go all-in
            if bet_amount > self.stacks[player]:
                bet_amount = int(self.stacks[player])  # All-in
                
            # If bet doesn't meet minimum, treat as call or all-in
            if bet_amount < min_amount:
                if self.current_bet > 0:
                    return self._process_action(player, {'action': 'call'})
                else:
                    # If there's no current bet and amount is less than min_raise, treat as check
                    return self._process_action(player, {'action': 'check'})
            else:
                # Valid raise/bet
                amount_to_add = bet_amount - current_player_bet
                self.stacks[player] -= amount_to_add
                self.pot += amount_to_add
                self.round_state[f'player{player_idx}_bet'] = bet_amount
                self.current_bet = bet_amount
                self.round_state['min_raise'] = bet_amount - self.current_bet
                
        return False  # Player didn't fold
    
    def _deal_flop(self):
        """Deal the flop (3 community cards)"""
        if self.predefined_community:
            # Use predefined community cards for the flop
            # No need to burn a card
            self.community_cards = self.predefined_community[:3]
        else:
            # Deal normally
            self._deal_card()  # Burn card
            self.community_cards.append(self._deal_card())
            self.community_cards.append(self._deal_card())
            self.community_cards.append(self._deal_card())
            
        self.round_state['community_cards'] = self.community_cards.copy()
        self._update_game_state()
        
    def _deal_turn(self):
        """Deal the turn (1 community card)"""
        if self.predefined_community:
            # Use predefined community cards for the turn
            # No need to burn a card
            self.community_cards = self.predefined_community[:4]
        else:
            # Deal normally
            self._deal_card()  # Burn card
            self.community_cards.append(self._deal_card())
            
        self.round_state['community_cards'] = self.community_cards.copy()
        self._update_game_state()
        
    def _deal_river(self):
        """Deal the river (1 community card)"""
        if self.predefined_community:
            # Use predefined community cards for the river
            # No need to burn a card
            self.community_cards = self.predefined_community[:5]
        else:
            # Deal normally
            self._deal_card()  # Burn card
            self.community_cards.append(self._deal_card())
            
        self.round_state['community_cards'] = self.community_cards.copy()
        self._update_game_state()
    
    def _showdown(self):
        """Determine winner at showdown"""
        player1 = self.players[0]
        player2 = self.players[1]
        
        hand1 = self.player_hands[player1] + self.community_cards
        hand2 = self.player_hands[player2] + self.community_cards
        
        best_hand1 = evaluate_hand(hand1)
        best_hand2 = evaluate_hand(hand2)
        
        result = compare_hands(best_hand1, best_hand2)
        
        if result > 0:
            winner = player1
        elif result < 0:
            winner = player2
        else:
            # Split pot
            self.stacks[player1] += self.pot // 2
            self.stacks[player2] += self.pot // 2
            return None
            
        return self._end_round(winner)
    
    def _end_round(self, winner):
        """End the round and award pot to winner"""
        self.stacks[winner] += self.pot
        return winner
    
    def _create_deck(self):
        """Create a shuffled deck of cards"""
        suits = ['h', 'd', 'c', 's']  # hearts, diamonds, clubs, spades
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        deck = [rank + suit for suit in suits for rank in ranks]
        random.shuffle(deck)
        return deck
    
    def _deal_card(self):
        """Deal a single card from the deck"""
        if not self.deck:
            raise Exception("Deck is empty")
        return self.deck.pop()
    
    def _get_player_view(self, player):
        """Return the game state from a specific player's perspective"""
        player_idx = self.players.index(player)
        opponent_idx = 1 - player_idx
        
        return {
            'player_idx': player_idx,
            'hand': self.player_hands[player],
            'community_cards': self.community_cards,
            'pot': self.pot,
            'current_bet': self.current_bet,
            'my_stack': self.stacks[player],
            'opponent_stack': self.stacks[self.players[opponent_idx]],
            'my_bet': self.round_state.get(f'player{player_idx}_bet', 0),
            'opponent_bet': self.round_state.get(f'player{opponent_idx}_bet', 0),
            'min_raise': self.round_state['min_raise'],
            'ante': self.ante
        }
    
    def _update_game_state(self):
        """Update the current game state"""
        self.game_state = {
            'round': self.current_round,
            'pot': self.pot,
            'community_cards': self.community_cards.copy(),
            'current_bet': self.current_bet,
            'player1_stack': self.stacks[self.players[0]],
            'player2_stack': self.stacks[self.players[1]],
            'player1_bet': self.round_state.get('player0_bet', 0),
            'player2_bet': self.round_state.get('player1_bet', 0)
        } 

if __name__ == "__main__":
    # Simple test to verify that the predefined cards functionality works
    import os
    
    class TestPlayer:
        def __init__(self, name):
            self.name = name
        
        def __str__(self):
            return self.name
            
        def get_action(self, game_state):
            # Just fold for testing
            return {"action": "fold"}
    
    # Create a test engine
    player1 = TestPlayer("Player1")
    player2 = TestPlayer("Player2")
    engine = PokerEngine(player1, player2)
    
    # Ensure the directory exists
    os.makedirs("poker_rounds", exist_ok=True)
    
    # Create a test round file
    test_round = 1
    test_data = {
        "round": test_round,
        "player1": ["Ah", "Kh"],  # Royal flush potential
        "player2": ["Qc", "Jc"],  # Straight flush potential
        "community": ["Th", "Jh", "Qh", "Kc", "Ac"]  # Player 1 gets royal flush
    }
    
    with open(f"poker_rounds/round_{test_round}_cards.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print("Created test predefined cards file")
    
    # Load the predefined cards
    predefined = engine.load_predefined_cards(test_round)
    print(f"Loaded predefined cards: {predefined}")
    
    # Initialize round with predefined cards
    engine.initialize_round(predefined)
    
    # Verify player hands
    print(f"Player 1 hand: {engine.player_hands[player1]}")
    print(f"Player 2 hand: {engine.player_hands[player2]}")
    
    # Deal flop and check community cards
    engine._deal_flop()
    print(f"Community after flop: {engine.community_cards}")
    
    # Deal turn and check community cards
    engine._deal_turn()
    print(f"Community after turn: {engine.community_cards}")
    
    # Deal river and check community cards
    engine._deal_river()
    print(f"Community after river: {engine.community_cards}")
    
    print("Test complete!") 