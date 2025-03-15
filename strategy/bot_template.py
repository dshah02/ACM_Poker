"""
Poker Bot Template for ACM Poker Bot Competition

This is a starter template for creating your own poker bot.
Implement the get_action method to determine what action your bot will take in each situation.
"""

class PokerBotTemplate:
    """
    Template for creating a poker bot
    """
    def __init__(self, name="MyPokerBot"):
        """
        Initialize your bot with a name and any custom attributes
        
        Args:
            name (str): The name of your bot
        """
        self.name = name
        
        # Add any custom attributes here
        # For example, you might track hands played, opponent tendencies, etc.
        
    def __str__(self):
        """Return the bot's name for display purposes"""
        return self.name
        
    def get_action(self, game_state):
        """
        Determine the action to take based on the current game state
        
        Args:
            game_state (dict): The current state of the game from your perspective
                - player_idx: Your position (0 or 1)
                - hand: Your hole cards (e.g., ['Ah', 'Kd'])
                - community_cards: Shared cards on the board
                - pot: Total pot size
                - current_bet: Current bet to call
                - my_stack: Your remaining chips
                - opponent_stack: Opponent's remaining chips
                - my_bet: Amount you've already bet in this round
                - opponent_bet: Amount opponent has bet in this round
                - min_raise: Minimum raise amount
                - ante: Ante amount
            
        Returns:
            dict: Action to take
                - {'action': 'fold'}: Give up your hand
                - {'action': 'check'}: Pass (only when there's no bet to call)
                - {'action': 'call'}: Match the current bet
                - {'action': 'bet', 'amount': X}: Place a bet (when no existing bet)
                - {'action': 'raise', 'amount': X}: Raise to a total of X
        """
        # Extract information from game state
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
            
        # TODO: Calculate hand strength
        # You can implement your own hand strength evaluation or use helper functions
            
        # IMPLEMENT YOUR STRATEGY HERE
        # This is where you'll add your poker logic
        
        # Example structure for decision making:
        if current_bet == 0 or current_bet == my_bet:
            # No bet to call, we can check or bet
            pass  # Implement your strategy for checking or betting
        else:
            # There's a bet to call
            amount_to_call = current_bet - my_bet
            
            # Calculate pot odds if needed
            pot_odds = amount_to_call / (pot + amount_to_call) if amount_to_call > 0 else 0
            
            pass  # Implement your strategy for calling, raising, or folding
        
        # For now, just fold every hand
        return {'action': 'fold'}
    
    # Add any helper methods here to make your strategy more sophisticated