"""
Poker Tournament Manager
Run heads-up matches between poker bots
"""

import time
import random
from .poker_engine import PokerEngine
from strategy.example_strategy_0 import BasicBot
from strategy.example_strategy_1 import ConservativeBot
from strategy.example_strategy_2 import AggressiveBot
from src.utils import hand_type_str

class PokerTournament:
    """
    Tournament manager for poker bot competitions
    """
    def __init__(self, starting_stack=1000, ante=10, verbose=True):
        self.starting_stack = starting_stack
        self.ante = ante
        self.verbose = verbose
        self.results = {}
        self.toggle_first_player = False  # Track which player should go first
        
    def run_match(self, player1, player2, num_hands=100):
        """
        Run a match between two players for a specified number of hands
        
        Args:
            player1: First player bot
            player2: Second player bot
            num_hands (int): Number of hands to play
            
        Returns:
            dict: Match results
        """
        # Toggle which player goes first (alternates between matches)
        if self.toggle_first_player:
            # Swap players to alternate positions
            engine = PokerEngine(player2, player1, self.starting_stack, self.ante)
            # For results tracking, we still refer to the original players
            match_p1, match_p2 = player2, player1
        else:
            engine = PokerEngine(player1, player2, self.starting_stack, self.ante)
            match_p1, match_p2 = player1, player2
            
        # Toggle for next match
        self.toggle_first_player = not self.toggle_first_player
        
        initial_stacks = {
            player1: engine.stacks[match_p1],
            player2: engine.stacks[match_p2]
        }
        
        hands_played = 0
        hands_won = {player1: 0, player2: 0}
        
        if self.verbose:
            first_to_act = match_p1
            second_to_act = match_p2
            print(f"\n=== Starting match: {player1} vs {player2} ===")
            print(f"Position order: {first_to_act} acts first, {second_to_act} acts second")
            print(f"Starting stacks: {self.starting_stack} chips")
            print(f"Ante: {self.ante} chips")
            print(f"Number of hands: {num_hands}")
            
        # Play hands until one player is out of chips or max hands reached
        while (hands_played < num_hands and 
               engine.stacks[match_p1] > 0 and 
               engine.stacks[match_p2] > 0):
            
            if self.verbose:
                print(f"\n--- Hand #{hands_played + 1} ---")
                print(f"Stacks: {player1}: {engine.stacks[match_p1]}, {player2}: {engine.stacks[match_p2]}")
                
            winner = engine.play_round()
            
            if winner:
                # Map the winner back to the original player parameter
                original_winner = player1 if winner == match_p1 else player2
                hands_won[original_winner] = hands_won.get(original_winner, 0) + 1
                
                if self.verbose:
                    print(f"Winner: {original_winner}")
            else:
                if self.verbose:
                    print("Split pot")
                    
            hands_played += 1
            
            # Add a small delay between hands for readability if verbose
            if self.verbose:
                time.sleep(0.5)
                
        # Record final results
        final_stacks = {
            player1: engine.stacks[match_p1],
            player2: engine.stacks[match_p2]
        }
        
        profit = {
            player1: final_stacks[player1] - initial_stacks[player1],
            player2: final_stacks[player2] - initial_stacks[player2]
        }
        
        results = {
            'hands_played': hands_played,
            'hands_won': hands_won,
            'initial_stacks': initial_stacks,
            'final_stacks': final_stacks,
            'profit': profit
        }
        
        if self.verbose:
            print("\n=== Match complete ===")
            print(f"Hands played: {hands_played}")
            print(f"Hands won: {player1}: {hands_won[player1]}, {player2}: {hands_won[player2]}")
            print(f"Final stacks: {player1}: {final_stacks[player1]}, {player2}: {final_stacks[player2]}")
            print(f"Profit: {player1}: {profit[player1]}, {player2}: {profit[player2]}")
            
        return results
    
    def run_visual_match(self, player1, player2, num_hands=5, delay=1.0, fullscreen=False):
        """
        Run a visualized match between two players using pygame
        
        Args:
            player1: First player bot
            player2: Second player bot
            num_hands (int): Number of hands to play
            delay (float): Delay between actions in seconds
            fullscreen (bool): Whether to run in fullscreen mode
            
        Returns:
            dict: Match results
        """
        # Import here to avoid circular imports
        from poker_visualizer import run_visual_match
        
        if self.verbose:
            print(f"\n=== Starting visual match: {player1} vs {player2} ===")
            print(f"Starting stacks: {self.starting_stack} chips")
            print(f"Ante: {self.ante} chips")
            print(f"Number of hands: {num_hands}")
            
        winner = run_visual_match(player1, player2, hands=num_hands, delay=delay, fullscreen=fullscreen)
        
        # Since the visualizer handles the entire match, we just return a basic result
        # Note: In a real implementation, you might want to extract more detailed stats from the visualizer
        if winner:
            return {
                'winner': winner,
                'visualization': True
            }
        else:
            return {
                'winner': None,
                'visualization': True
            }
        
    def run_tournament(self, players, num_matches=10, hands_per_match=100, visualize_finals=False):
        """
        Run a round-robin tournament between all players
        
        Args:
            players (list): List of player bots
            num_matches (int): Number of matches between each pair
            hands_per_match (int): Number of hands per match
            visualize_finals (bool): Whether to visualize the final match
            
        Returns:
            dict: Tournament results
        """
        tournament_results = {}
        
        # Initialize results dictionary
        for player in players:
            tournament_results[player] = {
                'matches_played': 0,
                'matches_won': 0,
                'hands_played': 0,
                'hands_won': 0,
                'total_profit': 0
            }
            
        # Run matches between all pairs of players
        for i, player1 in enumerate(players):
            for j, player2 in enumerate(players):
                if i >= j:  # Skip playing against self or duplicate matches
                    continue
                    
                for match in range(num_matches):
                    if self.verbose:
                        print(f"\n=== Tournament match {match+1}/{num_matches}: {player1} vs {player2} ===")
                        
                    # Alternate who goes first
                    if match % 2 == 0:
                        match_results = self.run_match(player1, player2, hands_per_match)
                    else:
                        match_results = self.run_match(player2, player1, hands_per_match)
                        
                    # Update tournament results
                    p1_hands_won = match_results['hands_won'].get(player1, 0)
                    p2_hands_won = match_results['hands_won'].get(player2, 0)
                    
                    # Determine match winner based on profit
                    if match_results['profit'][player1] > match_results['profit'][player2]:
                        match_winner = player1
                    elif match_results['profit'][player2] > match_results['profit'][player1]:
                        match_winner = player2
                    else:
                        match_winner = None
                        
                    # Update player1 stats
                    tournament_results[player1]['matches_played'] += 1
                    tournament_results[player1]['hands_played'] += match_results['hands_played']
                    tournament_results[player1]['hands_won'] += p1_hands_won
                    tournament_results[player1]['total_profit'] += match_results['profit'][player1]
                    if match_winner == player1:
                        tournament_results[player1]['matches_won'] += 1
                        
                    # Update player2 stats
                    tournament_results[player2]['matches_played'] += 1
                    tournament_results[player2]['hands_played'] += match_results['hands_played']
                    tournament_results[player2]['hands_won'] += p2_hands_won
                    tournament_results[player2]['total_profit'] += match_results['profit'][player2]
                    if match_winner == player2:
                        tournament_results[player2]['matches_won'] += 1
                        
        # Calculate final statistics
        for player in players:
            stats = tournament_results[player]
            stats['hand_win_rate'] = stats['hands_won'] / stats['hands_played'] if stats['hands_played'] > 0 else 0
            stats['match_win_rate'] = stats['matches_won'] / stats['matches_played'] if stats['matches_played'] > 0 else 0
            stats['avg_profit_per_hand'] = stats['total_profit'] / stats['hands_played'] if stats['hands_played'] > 0 else 0
            
        # Display final tournament results
        if self.verbose:
            self._print_tournament_results(tournament_results)
            
        # Run a visual final match if requested
        if visualize_finals and len(players) >= 2:
            # Sort players by total profit to determine finalists
            sorted_players = sorted(tournament_results.keys(), 
                                   key=lambda p: tournament_results[p]['total_profit'], 
                                   reverse=True)
            
            finalist1 = sorted_players[0]
            finalist2 = sorted_players[1]
            
            if self.verbose:
                print("\n=== TOURNAMENT FINALS ===")
                print(f"Finalists: {finalist1} vs {finalist2}")
                print("Press Enter to start the finals...")
                input()
                
            # Run the final match with visualization
            visual_hands = min(10, hands_per_match)  # Limit visual hands for practicality
            self.run_visual_match(finalist1, finalist2, visual_hands, delay=0.5)
            
        return tournament_results
        
    def _print_tournament_results(self, results):
        """Print formatted tournament results"""
        print("\n" + "="*50)
        print("TOURNAMENT RESULTS")
        print("="*50)
        
        # Sort players by total profit
        sorted_players = sorted(results.keys(), key=lambda p: results[p]['total_profit'], reverse=True)
        
        for i, player in enumerate(sorted_players):
            stats = results[player]
            print(f"\n{i+1}. {player}")
            print(f"   Matches: {stats['matches_won']}/{stats['matches_played']} ({stats['match_win_rate']:.2%})")
            print(f"   Hands: {stats['hands_won']}/{stats['hands_played']} ({stats['hand_win_rate']:.2%})")
            print(f"   Total profit: {stats['total_profit']} chips")
            print(f"   Avg. profit per hand: {stats['avg_profit_per_hand']:.2f} chips")
            
        print("\n" + "="*50)
        
def run_detailed_hand(player1, player2, verbose=True):
    """Run a single hand with detailed output for debugging/demonstration"""
    engine = PokerEngine(player1, player2, 1000, 10)
    
    # Initialize round
    engine.initialize_round()
    
    if verbose:
        print(f"\n=== Detailed hand: {player1} vs {player2} ===")
        print(f"Ante: {engine.ante} chips")
        print(f"Stacks: {player1}: {engine.stacks[player1]}, {player2}: {engine.stacks[player2]}")
        print(f"\nHole cards:")
        print(f"{player1}: {engine.player_hands[player1]}")
        print(f"{player2}: {engine.player_hands[player2]}")
        
    # Pre-flop betting round
    if verbose:
        print("\n--- Pre-flop betting ---")
    winner = engine._betting_round('preflop')
    if winner:
        if verbose:
            print(f"{winner} wins {engine.pot} chips (opponent folded)")
        return engine._end_round(winner)
        
    # Deal flop
    engine._deal_flop()
    if verbose:
        print(f"\n--- Flop: {engine.community_cards} ---")
        
    # Flop betting round
    winner = engine._betting_round('flop')
    if winner:
        if verbose:
            print(f"{winner} wins {engine.pot} chips (opponent folded)")
        return engine._end_round(winner)
        
    # Deal turn
    engine._deal_turn()
    if verbose:
        print(f"\n--- Turn: {engine.community_cards} ---")
        
    # Turn betting round
    winner = engine._betting_round('turn')
    if winner:
        if verbose:
            print(f"{winner} wins {engine.pot} chips (opponent folded)")
        return engine._end_round(winner)
        
    # Deal river
    engine._deal_river()
    if verbose:
        print(f"\n--- River: {engine.community_cards} ---")
        
    # River betting round
    winner = engine._betting_round('river')
    if winner:
        if verbose:
            print(f"{winner} wins {engine.pot} chips (opponent folded)")
        return engine._end_round(winner)
        
    # Showdown
    player1_cards = engine.player_hands[player1] + engine.community_cards
    player2_cards = engine.player_hands[player2] + engine.community_cards
    
    if verbose:
        print("\n--- Showdown ---")
        player1_hand = engine._hand_evaluator.evaluate_hand(player1_cards)
        player2_hand = engine._hand_evaluator.evaluate_hand(player2_cards)
        print(f"{player1}: {hand_type_str(player1_hand)}")
        print(f"{player2}: {hand_type_str(player2_hand)}")
        
    winner = engine._showdown()
    
    if verbose:
        if winner:
            print(f"{winner} wins {engine.pot} chips")
        else:
            print(f"Split pot: {engine.pot // 2} chips each")
            
    return engine._end_round(winner)

def run_visual_demo(delay=0.5, fullscreen=False):
    """Run a visual demo match between example bots"""
    from poker_visualizer import run_visual_match
    
    print("Starting a visual poker match demonstration...")
    
    # Create example bots
    bot1 = ConservativeBot("Conserve")
    bot2 = AggressiveBot("AggroBot")
    
    # Run a visual match
    winner = run_visual_match(bot1, bot2, hands=5, delay=delay, fullscreen=fullscreen)
    
    print(f"\nDemo complete. Winner: {winner if winner else 'Tie'}")
    return winner

def run_visual_tournament(bots, matches_per_pair=1, hands_per_match=5, delay=0.5, fullscreen=False):
    """Run a tournament with visualization for the finals"""
    from poker_visualizer import run_visual_tournament
    
    print("Starting a poker tournament with visual finals...")
    
    # Run the tournament with visual finals
    results, winner = run_visual_tournament(
        bots, 
        matches_per_pair=matches_per_pair,
        hands_per_match=hands_per_match,
        delay=delay,
        fullscreen=fullscreen
    )
    
    print(f"\nTournament complete. Champion: {winner if winner else 'Tie'}")
    return results, winner

if __name__ == "__main__":
    # Create sample bots
    bot0 = BasicBot("SimpleBot")
    bot1 = ConservativeBot("Conserv")
    bot2 = AggressiveBot("AggroBot")
    
    # Run a detailed hand
    run_detailed_hand(bot0, bot1)
    
    # Run matches
    tournament = PokerTournament()
    tournament.run_match(bot0, bot1, num_hands=10)
    tournament.run_match(bot0, bot2, num_hands=10)
    
    # Run a small tournament
    tournament = PokerTournament()
    tournament.run_tournament([bot0, bot1, bot2], num_matches=2, hands_per_match=10)
    
    # Option 4: Run a visual demo match (commented out since pygame is not available)
    # run_visual_demo(delay=0.5)
    
    # Option 5: Run a tournament with visual finals (commented out since pygame is not available)
    # run_visual_tournament([bot0, bot1, bot2], matches_per_pair=1, hands_per_match=5, delay=0.5) 