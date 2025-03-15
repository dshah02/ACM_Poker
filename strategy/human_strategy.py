"""
Human Player Strategy for Poker
Allows a human to input decisions via the command line
"""

class HumanPlayer:
    """Human player strategy that requests input for each decision"""
    
    def __init__(self, name="Human"):
        """Initialize with a name for the player"""
        self.name = name
    
    def get_action(self, player_view):
        """
        Get an action from human input
        
        Args:
            player_view (dict): Current game state from player's perspective
            
        Returns:
            dict: Action to take
        """
        # Display current game state
        self._display_game_state(player_view)
        
        # Get valid input from user
        while True:
            print("\nAvailable actions:")
            
            # Show possible actions based on the game state
            actions = ["fold"]
            
            if player_view['current_bet'] <= player_view['my_bet']:
                actions.append("check")
            else:
                actions.append("call")
                
            if player_view['my_stack'] > 0:
                actions.append("bet")
                actions.append("raise")
            
            action_str = "/".join(actions)
            prompt = f"Enter your action ({action_str}): "
            user_input = input(prompt).strip().lower()
            
            # Handle simple actions (fold, check, call)
            if user_input == "fold" and "fold" in actions:
                return {"action": "fold"}
                
            elif user_input == "check" and "check" in actions:
                return {"action": "check"}
                
            elif user_input == "call" and "call" in actions:
                return {"action": "call"}
            
            # Handle bet action
            elif user_input.startswith("bet") and "bet" in actions:
                try:
                    # Extract amount from input
                    parts = user_input.split()
                    if len(parts) == 2:
                        amount = int(parts[1])
                        if amount > 0 and amount <= player_view['my_stack']:
                            return {"action": "bet", "amount": amount}
                except ValueError:
                    pass
                print("Invalid bet. Format: 'bet AMOUNT' where AMOUNT is a positive integer <= your stack")
                
            # Handle raise action
            elif user_input.startswith("raise") and "raise" in actions:
                try:
                    # Extract amount from input
                    parts = user_input.split()
                    if len(parts) == 2:
                        amount = int(parts[1])
                        if amount > 0 and amount <= player_view['my_stack']:
                            return {"action": "raise", "amount": amount}
                except ValueError:
                    pass
                print("Invalid raise. Format: 'raise AMOUNT' where AMOUNT is a positive integer <= your stack")
                
            else:
                print(f"Invalid action. Please enter one of: {action_str}")
                print("For bet/raise, use format: 'bet AMOUNT' or 'raise AMOUNT'")
    
    def _display_game_state(self, player_view):
        """Display the current game state in a human-readable format"""
        print("\n" + "="*50)
        print(f"YOUR TURN ({self.name})")
        print("="*50)
        
        # Display hole cards
        print(f"Your hand: {player_view['hand']}")
        
        # Display community cards if any
        if player_view['community_cards']:
            print(f"Community cards: {player_view['community_cards']}")
        else:
            print("Community cards: None (Pre-flop)")
        
        # Display pot and betting information
        print(f"\nPot: {player_view['pot']}")
        print(f"Your stack: {player_view['my_stack']}")
        print(f"Opponent stack: {player_view['opponent_stack']}")
        
        # Display current bet status
        print(f"Current bet: {player_view['current_bet']}")
        print(f"Your current bet: {player_view['my_bet']}")
        print(f"Opponent current bet: {player_view['opponent_bet']}")
        
        # Calculate amount to call
        to_call = player_view['current_bet'] - player_view['my_bet']
        if to_call > 0:
            print(f"Amount to call: {to_call}")
        
        # Display minimum raise if relevant
        if player_view['min_raise'] > 0:
            min_raise_total = player_view['current_bet'] + player_view['min_raise']
            print(f"Minimum raise: {player_view['min_raise']} (total: {min_raise_total})")
    
    def __str__(self):
        return self.name 