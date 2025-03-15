#!/usr/bin/env python3
"""
Play Poker Against a Bot
This script allows a human player to compete against a poker bot
"""

from human_strategy import HumanPlayer
from example_strategy_1 import ConservativeBot
from example_strategy_2 import AggressiveBot
from poker_visualizer import run_visual_match
import random

def main():
    """Run a game where a human plays against a bot"""
    print("="*60)
    print("Welcome to Heads-Up Poker!")
    print("="*60)
    print("\nYou'll be playing against one of our poker bots.")
    
    # Get player name
    player_name = input("\nEnter your name: ").strip()
    if not player_name:
        player_name = "Human"
    
    # Create human player
    human_player = HumanPlayer(player_name)
    
    # Choose opponent
    print("\nChoose your opponent:")
    print("1. ConservaBot (plays conservative)")
    print("2. AggroBot (plays aggressive)")
    
    opponent_choice = ""
    while opponent_choice not in ["1", "2"]:
        opponent_choice = input("Enter 1 or 2: ").strip()
    
    if opponent_choice == "1":
        bot_player = ConservativeBot("ConservaBot")
        print(f"\n{player_name} vs ConservaBot")
    else:
        bot_player = AggressiveBot("AggroBot")
        print(f"\n{player_name} vs AggroBot")
    
    # Set game parameters
    print("\nGame Setup:")
    
    # Number of hands
    num_hands = 5
    try:
        hands_input = input("Number of hands to play (default 5): ").strip()
        if hands_input:
            num_hands = int(hands_input)
    except ValueError:
        print("Invalid number, using default (5)")
    
    # Animation speed
    animation_speed = 1.0
    try:
        speed_input = input("Animation speed (0.5-2.0, default 1.0): ").strip()
        if speed_input:
            animation_speed = float(speed_input)
    except ValueError:
        print("Invalid number, using default (1.0)")
    
    # Fullscreen option
    fullscreen = False
    fs_choice = input("Play in fullscreen? (y/n, default n): ").strip().lower()
    if fs_choice == 'y':
        fullscreen = True
        
    # Debug mode option
    debug = False
    debug_choice = input("Enable debug mode? This will allow editing the pre-generated hands (y/n, default n): ").strip().lower()
    if debug_choice == 'y':
        debug = True
    
    # Starting game message
    print("\nStarting game...")
    if debug:
        print("Debug mode enabled. For each hand, cards will be pre-generated and saved to poker_rounds/round_X_cards.json")
        print("You can edit this file before the hand starts to test specific scenarios.")
    print("When it's your turn, input your action in the command line.")
    print("Available actions will be displayed.")
    
    # Randomly decide if the human or bot goes first
    toggle_players = random.choice([True, False])
    if toggle_players:
        print(f"The bot ({bot_player}) will act first in the hand.")
    else:
        print(f"You ({player_name}) will act first in the hand.")
        
    input("Press Enter to begin...")
    
    # Run the match
    winner = run_visual_match(
        human_player, 
        bot_player, 
        hands=num_hands, 
        delay=animation_speed,
        fullscreen=fullscreen,
        debug=debug,
        toggle_players=toggle_players
    )
    
    # Show final result
    if winner == human_player:
        print(f"\nCongratulations {player_name}! You won the match against {bot_player}!")
    elif winner:
        print(f"\n{bot_player} won the match. Better luck next time, {player_name}!")
    else:
        print(f"\nThe match ended in a tie between {player_name} and {bot_player}.")

if __name__ == "__main__":
    main() 