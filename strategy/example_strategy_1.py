"""
Conservative Bot Strategy for Poker Competition
This bot plays carefully based on hand strength and position
"""

from hand_evaluator import calculate_monte_carlo_strength

class ConservativeBot:
    """
    A conservative poker bot that makes decisions based on hand strength,
    position, and pot odds.
    """
    def __init__(self, name="ConsBot"):
        self.name = name
        self.hand_strength_thresholds = {
            'preflop': {
                'fold': 0.2,
                'call': 0.4,
                'raise': 0.7
            },
            'flop': {
                'fold': 0.3,
                'call': 0.5,
                'raise': 0.7
            },
            'turn': {
                'fold': 0.4,
                'call': 0.6,
                'raise': 0.8
            },
            'river': {
                'fold': 0.5,
                'call': 0.7,
                'raise': 0.85
            }
        }
        
        # Conservative bot percentile thresholds for preflop play
        self.preflop_percentile_thresholds = {
            'fold': 0.3,    # Fold bottom 70% of hands
            'call': 0.6,    # Call with top 40% of hands
            'raise': 0.85   # Raise with top 15% of hands
        }
        
    def __str__(self):
        return self.name
        
    def get_action(self, game_state):
        """
        Determine action based on current game state
        
        Args:
            game_state (dict): The current state of the game from the player's perspective
            
        Returns:
            dict: Action to take
        """
        # Extract relevant information from game state
        hand = game_state['hand']
        community_cards = game_state['community_cards']
        pot = game_state['pot']
        current_bet = game_state['current_bet']
        my_stack = game_state['my_stack']
        my_bet = game_state['my_bet']
        opponent_bet = game_state['opponent_bet']
        min_raise = game_state['min_raise']
        
        # Determine game round based on number of community cards
        if len(community_cards) == 0:
            round_name = 'preflop'
        elif len(community_cards) == 3:
            round_name = 'flop'
        elif len(community_cards) == 4:
            round_name = 'turn'
        else:
            round_name = 'river'
            
        # Calculate hand strength and percentile
        hand_strength  = calculate_monte_carlo_strength(hand, community_cards)

        # Calculate pot odds
        amount_to_call = current_bet - my_bet
        pot_odds = amount_to_call / (pot + amount_to_call) if amount_to_call > 0 else 0
        
        # Determine action thresholds for this round
        thresholds = self.hand_strength_thresholds[round_name]
        
        # If we can check (no current bet)
        if current_bet == 0 or current_bet == my_bet:
            if hand_strength >= thresholds['raise']:
                # Strong hand, raise
                raise_amount = min(min(my_stack, pot), min_raise * 3)
                # Ensure bet is an integer
                raise_amount = int(raise_amount)
                return {'action': 'bet', 'amount': raise_amount}
            else:
                # Weak or medium hand, check
                return {'action': 'check'}
                
        # There is a bet to call
        else:
            # If hand strength justifies a call based on pot odds
            if hand_strength > pot_odds and hand_strength >= thresholds['call']:
                # If hand is strong enough to raise
                if hand_strength >= thresholds['raise']:
                    # Calculate raise amount based on hand strength and pot size
                    raise_size_factor = min(3, 1 + hand_strength)
                    raise_amount = min(my_stack, current_bet + min_raise * raise_size_factor)
                    # Ensure bet is an integer
                    raise_amount = int(raise_amount)
                    return {'action': 'raise', 'amount': raise_amount}
                else:
                    # Just call
                    return {'action': 'call'}
            elif hand_strength >= thresholds['fold']:
                # Borderline hand, call if cheap
                if amount_to_call <= 0.1 * my_stack:
                    return {'action': 'call'}
                else:
                    return {'action': 'fold'}
            else:
                # Weak hand, fold
                return {'action': 'fold'}
        