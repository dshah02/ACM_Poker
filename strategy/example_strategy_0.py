"""
Basic Bot Strategy for Poker Competition
This bot makes simple decisions based on hand strength and pot odds with no bluffing
"""

from hand_evaluator import calculate_monte_carlo_strength

class BasicBot:
    """
    A very basic poker bot that makes straightforward decisions based on
    hand strength compared to pot odds, with no bluffing or round-specific adjustments.
    """
    def __init__(self, name="BasicBot"):
        self.name = name
        # Same thresholds for all rounds
        self.hand_strength_thresholds = {
            'fold': 0.3,  # Fold if below this threshold
            'call': 0.5,  # Call if above this but below raise threshold
            'raise': 0.8   # Raise if above this threshold
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
        min_raise = game_state['min_raise']
        
        # Calculate hand strength using Monte Carlo simulation
        hand_strength = calculate_monte_carlo_strength(hand, community_cards)

        # Calculate pot odds
        amount_to_call = current_bet - my_bet
        pot_odds = amount_to_call / (pot + amount_to_call) if amount_to_call > 0 else 0
        
        # If we can check (no current bet)
        if current_bet == 0 or current_bet == my_bet:
            if hand_strength >= self.hand_strength_thresholds['raise']:
                # Strong hand, raise
                raise_amount = min(my_stack, max(min_raise, pot * 0.5))
                return {'action': 'bet', 'amount': raise_amount}
            else:
                # Not strong enough to bet, check
                return {'action': 'check'}
                
        # There is a bet to call
        else:
            # If hand strength justifies a call based on pot odds
            if hand_strength > pot_odds:
                # If hand is strong enough to raise
                if hand_strength >= self.hand_strength_thresholds['raise']:
                    # Simple raise sizing based on hand strength
                    raise_amount = min(my_stack, current_bet + min_raise)
                    return {'action': 'raise', 'amount': raise_amount}
                elif hand_strength >= self.hand_strength_thresholds['call']:
                    # Just call
                    return {'action': 'call'}
                else:
                    # Hand strength > pot odds but below call threshold - make a careful call
                    if amount_to_call <= 0.1 * my_stack:
                        return {'action': 'call'}
                    else:
                        return {'action': 'fold'}
            else:
                # Hand strength not good enough compared to pot odds, fold
                return {'action': 'fold'} 