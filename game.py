#!/usr/bin/env python3
"""
Poker Game Launcher
This script provides simple ways to run poker games and tournaments
"""

import sys
import os
import time
import tqdm
import random


from src.poker_engine import PokerEngine
from src.poker_visualizer import run_visual_match
from src.poker_tournament import PokerTournament
from src.utils import *
from hand_evaluator import preflop_rank_description, evaluate_hand, calculate_head_to_head_equity, compare_hands
from strategy.example_strategy_1 import ConservativeBot
from strategy.example_strategy_2 import AggressiveBot
from strategy.human_strategy import HumanPlayer


def run_visual_game(player1_bot, player2_bot, hands=5, delay=1.0, fullscreen=False, debug=False, alternate_positions=True):
    """
    Run a visual poker game between two bots
    
    Args:
        player1_bot: First player bot
        player2_bot: Second player bot
        hands (int): Number of hands to play
        delay (float): Delay between actions in seconds
        fullscreen (bool): Whether to run in fullscreen mode
        debug (bool): Whether to allow editing the pre-generated hands JSON
        alternate_positions (bool): Whether to alternate which player goes first between matches
        
    Returns:
        The winner of the match
    """
    print(f"Starting visual game: {player1_bot} vs {player2_bot}")
    print(f"Playing {hands} hands with {delay}s animation delay")
    
    # Make sure the poker_rounds directory exists
    os.makedirs("poker_rounds", exist_ok=True)
    
    # If alternating positions, decide randomly who starts first
    toggle_players = False
    if alternate_positions:
        toggle_players = random.choice([True, False])
        if toggle_players:
            print(f"Positions swapped: {player2_bot} will act first")
    
    # Run the visual match
    winner = run_visual_match(
        player1_bot, 
        player2_bot, 
        hands=hands, 
        delay=delay, 
        fullscreen=fullscreen,
        debug=debug,
        toggle_players=toggle_players
    )
    
    print(f"\nGame complete! Winner: {winner}")
    return winner


def run_tournaments(player1_bot, player2_bot, num_matches=100, hands_per_match=10, verbose=False, alternate_positions=True):
    """
    Run multiple matches between two bots without visual feedback
    
    Args:
        player1_bot: First player bot
        player2_bot: Second player bot
        num_matches (int): Number of matches to run
        hands_per_match (int): Number of hands per match
        verbose (bool): Whether to print detailed results
        alternate_positions (bool): Whether to alternate which player goes first between matches
        
    Returns:
        Dictionary with match statistics
    """
    print(f"Running {num_matches} matches: {player1_bot} vs {player2_bot}")
    print(f"Each match consists of {hands_per_match} hands")
    start_time = time.time()
    
    tournament = PokerTournament(verbose=verbose)
    
    # If not alternating positions, reset toggle to keep player1 first
        
    # Track results
    player1_wins = 0
    player2_wins = 0
    ties = 0
    player1_total_profit = 0
    player2_total_profit = 0
    
    # Run the matches
    for i in tqdm.tqdm(range(num_matches)):
                    
        # Run a single match between the two bots
        match_results = tournament.run_match(player1_bot, player2_bot, hands_per_match)
        
        # Determine the winner based on profit
        p1_profit = match_results['profit'][player1_bot]
        p2_profit = match_results['profit'][player2_bot]
        
        player1_total_profit += p1_profit
        player2_total_profit += p2_profit
        
        if p1_profit > p2_profit:
            player1_wins += 1
        elif p2_profit > p1_profit:
            player2_wins += 1
        else:
            ties += 1
    
    # Calculate statistics
    win_rate_p1 = player1_wins / num_matches
    win_rate_p2 = player2_wins / num_matches
    tie_rate = ties / num_matches
    avg_profit_p1 = player1_total_profit / num_matches
    avg_profit_p2 = player2_total_profit / num_matches
    
    # Prepare and print results
    stats = {
        'player1_name': str(player1_bot),
        'player2_name': str(player2_bot),
        'player1_wins': player1_wins,
        'player2_wins': player2_wins,
        'ties': ties,
        'player1_win_rate': win_rate_p1,
        'player2_win_rate': win_rate_p2,
        'player1_avg_profit': avg_profit_p1,
        'player2_avg_profit': avg_profit_p2,
        'matches_played': num_matches
    }
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*50)
    print(f"Match Results (completed in {elapsed_time:.2f} seconds):")
    print("="*50)
    print(f"Matches played: {num_matches}")
    print(f"{player1_bot} wins: {player1_wins} ({win_rate_p1:.2%})")
    print(f"{player2_bot} wins: {player2_wins} ({win_rate_p2:.2%})")
    print(f"Ties: {ties} ({tie_rate:.2%})")
    print(f"{player1_bot} average profit: {avg_profit_p1:.2f}")
    print(f"{player2_bot} average profit: {avg_profit_p2:.2f}")
    print("="*50)
    
    return stats


# Example 1: Run a visual game between two bots
if __name__ == "__main__":
    # Create example bots
    bot1 = ConservativeBot("Conserv")
    bot2 = AggressiveBot("AggroBot")
    human_bot = HumanPlayer("human")
    
    # Run a visual game
    print("=== Example 1: Running a visual game ===")
    run_visual_game(
        human_bot,              # First player bot
        bot2,                   # Second player bot
        hands=5,                # Number of hands to play
        delay=1.0,              # Animation delay in seconds
        fullscreen=False,       # Run in fullscreen mode?
        debug=True,             # Allow editing pre-generated hands?
        alternate_positions=True # Whether to randomly assign first player
    )
    
    # Example 2: Run multiple tournaments without visualization
    # print("\n\n=== Example 2: Running multiple games ===")
    # print("(Uncomment the code below to run this example)")
    
    
    # run_tournaments(
    #     bot1,                   # First player bot
    #     bot2,                   # Second player bot
    #     num_matches=10,         # Number of matches to play
    #     hands_per_match=5,      # Hands per match
    #     verbose=False,          # Print detailed results?
    #     alternate_positions=True # Whether to alternate who goes first
    # )
    
    # Example 3: Run a visual game with fixed positions (no alternating)
    # print("\n\n=== Example 3: Running a visual game with fixed positions ===")
    # print("(Uncomment the code below to run this example)")
    
    
    # run_visual_game(
    #     bot1,                   # First player bot (will always act first)
    #     bot2,                   # Second player bot (will always act second)
    #     hands=5,                # Number of hands to play
    #     delay=1.0,              # Animation delay in seconds
    #     alternate_positions=False # Keep player positions fixed
    # )
    