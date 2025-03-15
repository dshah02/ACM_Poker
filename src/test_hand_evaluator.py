#!/usr/bin/env python
"""
Test script for the hand evaluator module
"""

from hand_evaluator import (
    evaluate_hand, 
    preflop_percentile, 
    preflop_rank_description,
    calculate_monte_carlo_strength
)
from utils import hand_type_str

def test_evaluate_hand():
    """Test the evaluate_hand function"""
    # Test a royal flush
    royal_flush = ['Ah', 'Kh', 'Qh', 'Jh', 'Th']
    result = evaluate_hand(royal_flush)
    print(f"Royal Flush: {result}")
    print(f"Hand type: {hand_type_str(result)}")
    
    # Test a full house
    full_house = ['Ah', 'Ad', 'As', 'Kh', 'Kd']
    result = evaluate_hand(full_house)
    print(f"Full House: {result}")
    print(f"Hand type: {hand_type_str(result)}")
    
    # Test with more than 5 cards (should find the best 5-card hand)
    seven_cards = ['Ah', 'Kh', 'Qh', 'Jh', 'Th', '2d', '3c']
    result = evaluate_hand(seven_cards)
    print(f"7 cards (should find royal flush): {result}")
    print(f"Hand type: {hand_type_str(result)}")

def test_preflop_percentile():
    """Test the preflop_percentile function"""
    # Test some common starting hands
    hands = [
        ['Ah', 'Ad'],  # AA
        ['Ah', 'Kh'],  # AKs
        ['Ah', 'Kd'],  # AKo
        ['2h', '7d'],  # 72o (one of the worst hands)
    ]
    
    for hand in hands:
        percentile = preflop_percentile(hand)
        desc = preflop_rank_description(hand)
        print(f"Hand: {hand} - Percentile: {percentile:.2f} - Description: {desc[0]} ({desc[1]})")

def test_monte_carlo():
    """Test the Monte Carlo simulation function"""
    # Player has pocket aces
    player_hand = ['Ah', 'Ad']
    
    # Empty community cards (preflop)
    community_cards = []
    strength = calculate_monte_carlo_strength(player_hand, community_cards, num_simulations=10)
    print(f"Preflop AA strength: {strength:.2f}")
    
    # Add a flop
    community_cards = ['Kh', 'Qh', '2d']
    strength = calculate_monte_carlo_strength(player_hand, community_cards, num_simulations=10)
    print(f"Flop AA strength with {community_cards}: {strength:.2f}")

if __name__ == "__main__":
    print("\n=== Testing evaluate_hand ===")
    test_evaluate_hand()
    
    print("\n=== Testing preflop_percentile ===")
    test_preflop_percentile()
    
    print("\n=== Testing Monte Carlo simulation ===")
    test_monte_carlo() 