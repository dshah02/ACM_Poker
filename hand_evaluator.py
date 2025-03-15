"""
Hand evaluator for Texas Hold'em Poker
This module provides main functions to evaluate poker hands
"""

from itertools import combinations
import random
from src.utils import (
    evaluate_5card_hand, 
    get_hand_value, 
    compare_hands,
    PREFLOP_HAND_RANKINGS,
    get_canonical_preflop_hand
)

def evaluate_hand(cards):
    """
    Evaluates the best 5-card hand from a list of cards
    
    Args:
        cards (list): List of cards in the format 'rank+suit' (e.g., 'As', 'Th', '2c')
        
    Returns:
        dict: Hand evaluation with type and relevant card ranks
    """
    # Find all possible 5-card combinations
    best_hand = None
    best_hand_value = -1
    
    # If we have exactly 5 cards, no need for combinations
    if len(cards) == 5:
        return evaluate_5card_hand(cards)
    
    # Otherwise, find the best 5-card hand from all possible combinations
    for hand in combinations(cards, 5):
        hand_eval = evaluate_5card_hand(hand)
        hand_value = get_hand_value(hand_eval)
        
        if hand_value > best_hand_value:
            best_hand_value = hand_value
            best_hand = hand_eval
            
    return best_hand

def preflop_percentile(hand):
    """
    Calculate the percentile of a preflop hand based on conventional rankings
    
    Args:
        hand (list): Two-card hand (e.g., ['Ah', 'Kd'])
        
    Returns:
        float: Percentile from 0.0 (worst) to 1.0 (best)
    """
    canonical_hand = get_canonical_preflop_hand(hand)
    
    try:
        # Find position in ranking (0-indexed)
        rank_position = PREFLOP_HAND_RANKINGS.index(canonical_hand)
        
        # Convert to percentile (invert so higher is better)
        # 169 possible starting hands, so position 0 is best (100th percentile)
        percentile = 1.0 - (rank_position / (len(PREFLOP_HAND_RANKINGS) - 1))
        
        return percentile
    except ValueError:
        # If hand not found in rankings (shouldn't happen with valid hands)
        return 0.0

def preflop_rank_description(hand):
    """
    Get a descriptive label for a preflop hand based on its ranking
    
    Args:
        hand (list): Two-card hand (e.g., ['Ah', 'Kd'])
        
    Returns:
        tuple: (hand_name, rank_description, percentile)
    """
    percentile = preflop_percentile(hand)
    canonical_hand = get_canonical_preflop_hand(hand)
    
    # Descriptive labels based on percentile
    if percentile >= 0.95:
        description = "(Top 5%)"
    elif percentile >= 0.85:
        description = "(Top 15%)"
    elif percentile >= 0.70:
        description = "(Top 30%)"
    elif percentile >= 0.50:
        description = "(Top 50%)"
    elif percentile >= 0.30:
        description = "(Top 70%)"
    elif percentile >= 0.15:
        description = "(Bottom 30%)"
    elif percentile >= 0.05:
        description = "(Bottom 15%)"
    else:
        description = "(Bottom 5%)"
        
    return (canonical_hand, description, percentile)

def calculate_monte_carlo_strength(player_hand, community_cards, num_simulations=100, samples_per_opponent=5):
    """
    Calculate hand strength using Monte Carlo simulation.
    First samples possible opponent hands, then for each opponent hand,
    samples possible community card completions.
    
    Args:
        player_hand (list): Player's hole cards (e.g., ['Ah', 'Kd'])
        community_cards (list): Community cards on the board (can be empty for preflop)
        num_simulations (int): Number of random simulations to run
        samples_per_opponent (int): Number of board completions to sample per opponent hand
        
    Returns:
        float: Monte Carlo hand strength as a value between 0.0 and 1.0
    """
    if not player_hand:
        return 0.0
        
    # If preflop, just use the preflop percentile for efficiency
    if not community_cards:
        return preflop_percentile(player_hand)
    
    # Create a deck excluding the player's hand and community cards
    ranks = list("23456789TJQKA")
    suits = list("hdcs")
    deck = [r + s for r in ranks for s in suits]
    
    # Remove known cards from the deck
    for card in player_hand + community_cards:
        if card in deck:
            deck.remove(card)
    
    # Number of opponent hands to sample
    num_opponent_samples = num_simulations
    
    # Number of board completions per opponent hand
    num_board_samples_per_opponent = samples_per_opponent
    
    total_trials = 0
    wins = 0
    ties = 0
    
    # Sample different opponent hands
    for _ in range(num_opponent_samples):
        # Generate a random opponent hand from remaining deck
        opponent_hand = random.sample(deck, 2)
        
        # Remove opponent cards from the deck temporarily
        opponent_deck = deck.copy()
        for card in opponent_hand:
            opponent_deck.remove(card)
        
        # Determine how many more community cards we need
        remaining_cards_needed = 5 - len(community_cards)
        
        # Sample different board completions for this opponent hand
        for _ in range(num_board_samples_per_opponent):
            # Sample remaining community cards
            if remaining_cards_needed > 0:
                remaining_community = random.sample(opponent_deck, remaining_cards_needed)
                full_community = community_cards + remaining_community
            else:
                full_community = community_cards
            
            # Evaluate both hands
            player_cards = player_hand + full_community
            opponent_cards = opponent_hand + full_community
            
            player_hand_eval = evaluate_hand(player_cards)
            opponent_hand_eval = evaluate_hand(opponent_cards)
            
            # Compare hands
            result = compare_hands(player_hand_eval, opponent_hand_eval)
            
            if result > 0:
                wins += 1
            elif result == 0:
                ties += 0.5  # Count ties as half a win
                
            total_trials += 1
    
    # Calculate win percentage
    if total_trials == 0:
        return 0.5  # Default if no trials were run
        
    return (wins + ties) / total_trials


def calculate_head_to_head_equity(player1_hand, player2_hand, community_cards, num_simulations=100):
    """
    Calculate win probability for both players in a head-to-head matchup using Monte Carlo simulation.
    This is more efficient than calling calculate_monte_carlo_strength twice, as it reuses the same
    community card completions for both players.
    
    Args:
        player1_hand (list): Player 1's hole cards (e.g., ['Ah', 'Kd'])
        player2_hand (list): Player 2's hole cards (e.g., ['Qh', 'Qd'])
        community_cards (list): Community cards on the board (can be empty for preflop)
        num_simulations (int): Number of random simulations to run
        
    Returns:
        tuple: (player1_equity, player2_equity) as values between 0.0 and 1.0
    """
    import random
    
    if not player1_hand or not player2_hand:
        return (0.5, 0.5)  # Default if invalid hands
    
    # Create a deck excluding both players' hands and community cards
    ranks = list("23456789TJQKA")
    suits = list("hdcs")
    deck = [r + s for r in ranks for s in suits]
    
    # Remove known cards from the deck
    for card in player1_hand + player2_hand + community_cards:
        if card in deck:
            deck.remove(card)
    
    total_trials = 0
    player1_wins = 0
    player2_wins = 0
    ties = 0
    
    # Determine how many more community cards we need
    remaining_cards_needed = 5 - len(community_cards)
    
    # Run simulations
    for _ in range(num_simulations):
        # Sample remaining community cards
        if remaining_cards_needed > 0:
            remaining_community = random.sample(deck, remaining_cards_needed)
            full_community = community_cards + remaining_community
        else:
            full_community = community_cards
        
        # Evaluate both hands
        player1_cards = player1_hand + full_community
        player2_cards = player2_hand + full_community
        
        player1_hand_eval = evaluate_hand(player1_cards)
        player2_hand_eval = evaluate_hand(player2_cards)
        
        # Compare hands
        result = compare_hands(player1_hand_eval, player2_hand_eval)
        
        if result > 0:
            player1_wins += 1
        elif result < 0:
            player2_wins += 1
        else:
            ties += 1
            
        total_trials += 1
    
    # Calculate win percentages
    if total_trials == 0:
        return (0.5, 0.5)  # Default if no trials were run
        
    # Count ties as half a win for each player
    player1_equity = (player1_wins + ties * 0.5) / total_trials
    player2_equity = (player2_wins + ties * 0.5) / total_trials
    
    return (player1_equity, player2_equity) 