import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from the file
from src.poker_engine import PokerEngine

class TestPlayer:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def get_action(self, game_state):
        # Always check/call to ensure all betting rounds are played
        if game_state.get('can_check', False):
            return {'action': 'check'}
        else:
            return {'action': 'call'}

def test_alternating_starts():
    p1 = TestPlayer('Player 1')
    p2 = TestPlayer('Player 2')
    engine = PokerEngine(p1, p2)
    
    print("\nTesting alternating starts and consistent first actor within a hand:")
    
    # Test Round 1
    print("\n=== ROUND 1 ===")
    preflop_player = engine.players[engine.current_player_idx]
    print(f"Pre-flop starting player: {preflop_player}")
    
    # Capture the starting player index for each betting round
    round1_starting_players = []
    
    # Store the original _betting_round method
    original_betting_round = engine._betting_round
    
    # Override the _betting_round method to track the starting player
    def wrapped_betting_round(round_name):
        round1_starting_players.append((round_name, engine.players[engine.current_player_idx]))
        return original_betting_round(round_name)
    
    # Replace the method
    engine._betting_round = wrapped_betting_round
    
    # Play round 1
    engine.play_round()
    
    # Print the starting player for each betting round in round 1
    for round_name, player in round1_starting_players:
        print(f"{round_name.capitalize()} starting player: {player}")
    
    # Test Round 2
    print("\n=== ROUND 2 ===")
    preflop_player = engine.players[engine.current_player_idx]
    print(f"Pre-flop starting player: {preflop_player}")
    
    # Capture the starting player index for each betting round
    round2_starting_players = []
    
    # Override the _betting_round method again for round 2
    def wrapped_betting_round2(round_name):
        round2_starting_players.append((round_name, engine.players[engine.current_player_idx]))
        return original_betting_round(round_name)
    
    # Replace the method
    engine._betting_round = wrapped_betting_round2
    
    # Play round 2
    engine.play_round()
    
    # Print the starting player for each betting round in round 2
    for round_name, player in round2_starting_players:
        print(f"{round_name.capitalize()} starting player: {player}")
    
    # Check that the pre-flop player alternated between rounds
    assert round1_starting_players[0][1] != round2_starting_players[0][1], "Pre-flop players should alternate between rounds"
    
    # Check that all betting rounds in round 1 had the same starting player
    assert all(player == round1_starting_players[0][1] for _, player in round1_starting_players), "All betting rounds in round 1 should have the same starting player"
    
    # Check that all betting rounds in round 2 had the same starting player
    assert all(player == round2_starting_players[0][1] for _, player in round2_starting_players), "All betting rounds in round 2 should have the same starting player"
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    test_alternating_starts() 