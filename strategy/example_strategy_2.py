"""
Aggressive Bot Strategy for Poker Competition
This bot plays aggressively, frequently bluffing and playing more hands
"""

import random
from hand_evaluator import calculate_monte_carlo_strength


class AggressiveBot:
    """
    An aggressive poker bot that plays more hands, bluffs frequently
    and applies pressure with bets and raises
    """
    def __init__(self, name="AggressiveBot"):
        self.name = name
        self.hand_strength_thresholds = {
            'preflop': {
                'fold': 0.1,  # Lower fold threshold = plays more hands
                'call': 0.25,
                'raise': 0.4  # Lower raise threshold = raises more often
            },
            'flop': {
                'fold': 0.15,
                'call': 0.3,
                'raise': 0.5
            },
            'turn': {
                'fold': 0.2,
                'call': 0.4,
                'raise': 0.6
            },
            'river': {
                'fold': 0.3,
                'call': 0.5,
                'raise': 0.7
            }
        }
        
        # Aggressive bot percentile thresholds for preflop play (plays more hands)
        self.preflop_percentile_thresholds = {
            'fold': 0.15,    # Only fold bottom 15% of hands
            'call': 0.4,     # Call with top 85% of hands
            'raise': 0.7     # Raise with top 30% of hands
        }
        
        # Bluffing frequencies for each round
        self.bluff_frequency = {
            'preflop': 0.2,
            'flop': 0.3,
            'turn': 0.25,
            'river': 0.2
        }
        # Track hands played for dynamic adjustment
        self.hands_played = 0
        self.hands_won = 0
        self.opponent_fold_frequency = 0.5  # Initial assumption
        
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
            
        # Calculate hand strength using Monte Carlo simulation
        hand_strength = calculate_monte_carlo_strength(hand, community_cards)
        
        # Decide if we should bluff in this situation
        should_bluff = self._should_bluff(round_name, pot, hand_strength)
        
        # If we should bluff, temporarily boost hand strength
        if should_bluff:
            hand_strength = max(hand_strength, self.hand_strength_thresholds[round_name]['raise'] + 0.1)
        
        # Calculate pot odds
        amount_to_call = current_bet - my_bet
        pot_odds = amount_to_call / (pot + amount_to_call) if amount_to_call > 0 else 0
        
        # Determine action thresholds for this round
        thresholds = self.hand_strength_thresholds[round_name]
        
        # If we can check (no current bet)
        if current_bet == 0 or current_bet == my_bet:
            if hand_strength >= thresholds['raise'] or should_bluff:
                # Strong hand or bluffing, raise aggressively
                # Size bet based on pot and stack
                bet_size_factor = random.uniform(0.6, 1.0)  # Varied bet sizes
                bet_amount = min(my_stack, max(min_raise, pot * bet_size_factor))
                # Ensure bet is an integer
                bet_amount = int(bet_amount)
                return {'action': 'bet', 'amount': bet_amount}
            elif hand_strength >= thresholds['call']:
                # Medium strength, sometimes bet
                if random.random() < 0.4:  # 40% of the time
                    small_bet = min(my_stack, pot * 0.3)
                    # Ensure bet is an integer
                    small_bet = int(small_bet)
                    return {'action': 'bet', 'amount': small_bet}
                else:
                    return {'action': 'check'}
            else:
                # Weak hand, usually check
                return {'action': 'check'}
                
        # There is a bet to call
        else:
            # Calculate relative pot size compared to stack
            relative_pot_size = pot / my_stack if my_stack > 0 else float('inf')
            
            if hand_strength >= thresholds['raise'] or should_bluff:
                # Strong hand or bluffing, raise often
                raise_size_factor = random.uniform(2.0, 3.0)  # More aggressive raises
                raise_amount = min(my_stack, current_bet + min_raise * raise_size_factor)
                
                # If nearly all-in anyway, just go all-in
                if raise_amount > 0.8 * my_stack:
                    raise_amount = my_stack
                
                # Ensure bet is an integer
                raise_amount = int(raise_amount)
                return {'action': 'raise', 'amount': raise_amount}
            elif hand_strength >= thresholds['call']:
                # Medium hand, call or occasionally re-raise as a semi-bluff
                if random.random() < 0.3:  # 30% semi-bluff raise
                    raise_amount = min(my_stack, current_bet + min_raise * 1.5)
                    # Ensure bet is an integer
                    raise_amount = int(raise_amount)
                    return {'action': 'raise', 'amount': raise_amount}
                else:
                    return {'action': 'call'}
            elif hand_strength >= thresholds['fold']:
                # Borderline hand, call if reasonable
                if amount_to_call <= 0.2 * my_stack or pot_odds > hand_strength * 0.7:
                    return {'action': 'call'}
                else:
                    return {'action': 'fold'}
            else:
                # Weak hand, but occasionally call as a bluff
                if random.random() < 0.15 and amount_to_call <= 0.15 * my_stack:
                    return {'action': 'call'}
                else:
                    return {'action': 'fold'}
    
    def _should_bluff(self, round_name, pot, hand_strength):
        """
        Decide whether to bluff in the current situation
        
        Args:
            round_name (str): Current betting round
            pot (int): Current pot size
            hand_strength (float): Current hand strength
            
        Returns:
            bool: True if should bluff, False otherwise
        """
        # Base bluff frequency for this round
        base_frequency = self.bluff_frequency[round_name]
        
        # Adjust based on opponent's fold tendencies
        adjusted_frequency = base_frequency * (0.5 + self.opponent_fold_frequency)
        
        # Reduce bluffing with strong hands (already betting for value)
        if hand_strength > 0.6:
            adjusted_frequency *= 0.2
        
        # Increase bluffing with very weak hands
        elif hand_strength < 0.3:
            adjusted_frequency *= 1.5
            
        # Random decision based on adjusted frequency
        return random.random() < adjusted_frequency
    
    def update_opponent_model(self, opponent_folded, pot_size, last_bet_size):
        """
        Update the model of opponent tendencies
        
        Args:
            opponent_folded (bool): Whether opponent folded to our bet
            pot_size (int): Size of the pot
            last_bet_size (int): Size of our last bet
        """
        # Update fold frequency
        bet_to_pot_ratio = last_bet_size / pot_size if pot_size > 0 else 1
        
        # Larger weight for more significant bets
        weight = min(0.1, bet_to_pot_ratio * 0.2)
        
        if opponent_folded:
            # Opponent folded, increase our estimate of their fold frequency
            self.opponent_fold_frequency = (1 - weight) * self.opponent_fold_frequency + weight
        else:
            # Opponent called/raised, decrease our estimate of their fold frequency
            self.opponent_fold_frequency = (1 - weight) * self.opponent_fold_frequency 