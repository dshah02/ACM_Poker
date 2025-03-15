"""
Utility functions for poker hand evaluation
This module provides helper functions and constants for poker hand evaluation
"""

from collections import Counter

# Card ranks and their values
RANKS = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
    'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
}

# Hand ranks
HAND_RANKS = {
    'high_card': 1,
    'pair': 2,
    'two_pair': 3,
    'three_kind': 4,
    'straight': 5,
    'flush': 6,
    'full_house': 7,
    'four_kind': 8,
    'straight_flush': 9
}

# Preflop hand rankings (169 distinct starting hands)
# List is ordered from strongest to weakest based on conventional poker strategy
# Format: pairs are listed as 'AA', suited hands as 'AKs', offsuit hands as 'AKo'
PREFLOP_HAND_RANKINGS = [
    # Top tier hands (1-10)
    'AA', 'KK', 'QQ', 'JJ', 'AKs', 'TT', 'AQs', 'AKo', 'AJs', 'KQs',
    # Strong hands (11-20)
    'ATs', 'AQo', '99', 'KJs', 'AJo', 'KTs', '88', 'QJs', 'A9s', 'KQo',
    # Above average hands (21-30)
    'ATo', 'KJo', '77', 'QTs', 'A8s', 'K9s', 'QJo', 'A7s', 'A5s', 'KTo',
    # Playable hands (31-40)
    'A6s', '66', 'A4s', 'QTo', 'A3s', 'K8s', 'Q9s', 'A2s', 'K7s', '55',
    # Middle tier hands (41-50)
    'JTs', 'A9o', 'K6s', 'K5s', 'Q8s', 'J9s', 'K4s', 'A8o', 'K3s', '44',
    # Below average but still playable (51-60)
    'K2s', 'A7o', 'Q7s', 'J8s', 'T9s', 'K9o', 'A6o', 'Q6s', 'Q5s', 'A5o',
    # Marginal hands (61-70)
    'T8s', 'A4o', 'J9o', 'Q4s', 'J7s', 'Q3s', 'A3o', '33', 'K8o', 'Q2s',
    # Weak but still occasionally playable (71-80)
    'Q9o', 'T7s', 'A2o', 'J6s', '98s', 'J5s', 'K7o', 'J4s', 'T9o', 'J3s',
    # Very weak hands (81-90)
    'J2s', 'K6o', 'T6s', '97s', 'Q8o', 'K5o', 'T5s', '87s', 'K4o', 'T4s',
    # Poor hands (91-100)
    '96s', 'K3o', 'T3s', 'J8o', 'T2s', 'K2o', '86s', '76s', 'Q7o', '22',
    # Very poor hands (101-110)
    '95s', 'Q6o', 'J7o', '85s', '65s', 'T8o', 'Q5o', '75s', '94s', 'Q4o',
    # Trash hands begin (111-120)
    '54s', 'Q3o', '84s', 'J6o', 'T7o', 'Q2o', '64s', '74s', 'J5o', '98o',
    # Very trash hands (121-130)
    '93s', '53s', 'J4o', '43s', '92s', '63s', '97o', 'J3o', '83s', 'J2o',
    # Extremely weak hands (131-140)
    '73s', '82s', 'T6o', '52s', '87o', 'T5o', '62s', '42s', '96o', 'T4o',
    # Bottom tier hands (141-150)
    '32s', '76o', 'T3o', '86o', 'T2o', '95o', '65o', '85o', '75o', '94o',
    # Worst hands (151-169)
    '54o', '84o', '74o', '64o', '93o', '53o', '43o', '92o', '63o', '73o',
    '83o', '52o', '82o', '62o', '42o', '32o', '72o'
]

def evaluate_5card_hand(cards):
    """Evaluate a specific 5-card hand"""
    assert len(cards) == 5, "Must provide exactly 5 cards"
    
    # Extract ranks and suits
    ranks = [card[0] for card in cards]
    suits = [card[1] for card in cards]
    
    # Count ranks and suits
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)
    
    # Check for flush
    is_flush = max(suit_counts.values()) == 5
    
    # Check for straight
    rank_values = sorted([RANKS[rank] for rank in ranks])
    
    # Special case: A-5 straight (Ace is low)
    if set(rank_values) == {2, 3, 4, 5, 14}:
        is_straight = True
        # Adjust ace to low
        rank_values = [1, 2, 3, 4, 5]
    else:
        is_straight = (len(set(rank_values)) == 5 and 
                      max(rank_values) - min(rank_values) == 4)
    
    # Identify hand type
    if is_straight and is_flush:
        return {'type': 'straight_flush', 'ranks': rank_values}
    
    if 4 in rank_counts.values():
        four_kind_rank = [rank for rank, count in rank_counts.items() if count == 4][0]
        kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
        return {'type': 'four_kind', 'ranks': [RANKS[four_kind_rank], RANKS[kicker]]}
    
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        three_kind_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
        pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
        return {'type': 'full_house', 'ranks': [RANKS[three_kind_rank], RANKS[pair_rank]]}
    
    if is_flush:
        return {'type': 'flush', 'ranks': sorted([RANKS[rank] for rank in ranks], reverse=True)}
    
    if is_straight:
        return {'type': 'straight', 'ranks': rank_values}
    
    if 3 in rank_counts.values():
        three_kind_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
        kickers = [RANKS[rank] for rank, count in rank_counts.items() if count == 1]
        kickers.sort(reverse=True)
        return {'type': 'three_kind', 'ranks': [RANKS[three_kind_rank]] + kickers}
    
    if list(rank_counts.values()).count(2) == 2:
        pairs = [RANKS[rank] for rank, count in rank_counts.items() if count == 2]
        pairs.sort(reverse=True)
        kicker = [RANKS[rank] for rank, count in rank_counts.items() if count == 1][0]
        return {'type': 'two_pair', 'ranks': pairs + [kicker]}
    
    if 2 in rank_counts.values():
        pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
        kickers = [RANKS[rank] for rank, count in rank_counts.items() if count == 1]
        kickers.sort(reverse=True)
        return {'type': 'pair', 'ranks': [RANKS[pair_rank]] + kickers}
    
    # High card
    return {'type': 'high_card', 'ranks': sorted([RANKS[rank] for rank in ranks], reverse=True)}

def get_hand_value(hand_eval):
    """
    Convert a hand evaluation to a numeric value for comparison
    
    Args:
        hand_eval (dict): Hand evaluation from evaluate_hand
        
    Returns:
        int: Numeric value of the hand for comparison
    """
    # Base value from hand type
    base_value = HAND_RANKS[hand_eval['type']] * 10**10
    
    # Add value of specific ranks
    # We multiply by decreasing powers of 10 to ensure proper ordering
    rank_values = 0
    for i, rank in enumerate(hand_eval['ranks']):
        rank_values += rank * 10**(8 - i*2)
        
    return base_value + rank_values

def compare_hands(hand1_eval, hand2_eval):
    """
    Compare two poker hands
    
    Args:
        hand1_eval (dict): First hand evaluation from evaluate_hand
        hand2_eval (dict): Second hand evaluation from evaluate_hand
        
    Returns:
        int: 1 if hand1 wins, -1 if hand2 wins, 0 if tie
    """
    hand1_value = get_hand_value(hand1_eval)
    hand2_value = get_hand_value(hand2_eval)
    
    if hand1_value > hand2_value:
        return 1
    elif hand1_value < hand2_value:
        return -1
    else:
        return 0

def hand_type_str(hand_eval):
    """
    Convert a hand evaluation to a human-readable string
    
    Args:
        hand_eval (dict): Hand evaluation from evaluate_hand
        
    Returns:
        str: Human-readable description of the hand
    """
    hand_type = hand_eval['type']
    
    if hand_type == 'straight_flush':
        if 14 in hand_eval['ranks']:
            return "Royal Flush"
        return "Straight Flush"
    elif hand_type == 'four_kind':
        return f"Four of a Kind"
    elif hand_type == 'full_house':
        return f"Full House"
    elif hand_type == 'flush':
        return f"Flush"
    elif hand_type == 'straight':
        return f"Straight"
    elif hand_type == 'three_kind':
        return f"Three of a Kind"
    elif hand_type == 'two_pair':
        return f"Two Pair"
    elif hand_type == 'pair':
        return f"Pair"
    else:
        return f"High Card"

def extract_card_values(hand):
    """
    Extract the rank values and suit information from hole cards
    
    Args:
        hand (list): Two-card hand (e.g., ['Ah', 'Kd'])
        
    Returns:
        tuple: (rank_values, is_pair, is_suited)
    """
    # Extract ranks and suits
    ranks = [card[0] for card in hand]
    suits = [card[1] for card in hand]
    
    # Calculate rank values
    rank_values = sorted([RANKS[rank] for rank in ranks], reverse=True)
    
    # Check if pair or suited
    is_pair = rank_values[0] == rank_values[1]
    is_suited = suits[0] == suits[1]
    
    return (rank_values, is_pair, is_suited)

def calculate_preflop_strength(hand, style='balanced'):
    """
    Calculate the pre-flop hand strength based on hole cards
    
    Args:
        hand (list): Two-card hand (e.g., ['Ah', 'Kd'])
        style (str): Playing style - 'conservative', 'aggressive', or 'balanced'
        
    Returns:
        float: Hand strength as a value between 0 and 1
    """
    if style == 'conservative':
        return _conservative_preflop_strength(hand)
    elif style == 'aggressive':
        return _aggressive_preflop_strength(hand)
    else:  # balanced
        conservative = _conservative_preflop_strength(hand)
        aggressive = _aggressive_preflop_strength(hand)
        return (conservative + aggressive) / 2.0

def _conservative_preflop_strength(hand):
    """Conservative pre-flop hand strength calculation"""
    rank_values, is_pair, is_suited = extract_card_values(hand)
    
    # Base strength
    strength = 0.0
    
    # Strong pairs
    if is_pair:
        if rank_values[0] >= 10:  # TT, JJ, QQ, KK, AA
            strength = 0.8 + 0.04 * (rank_values[0] - 10)  # 0.8 for TT up to 0.96 for AA
        else:
            strength = 0.4 + 0.04 * (rank_values[0] - 2)  # 0.4 for 22 up to 0.76 for 99
    
    # Strong non-pairs
    else:
        # Both cards are high (10 or higher)
        high_cards = sum(1 for rank in rank_values if rank >= 10)
        
        if high_cards == 2:  # Both cards are high
            strength = 0.6 + 0.02 * (rank_values[0] + rank_values[1] - 20)
            if is_suited:
                strength += 0.1
        elif high_cards == 1:  # One high card
            strength = 0.3 + 0.02 * rank_values[0]
            if is_suited:
                strength += 0.05
            # Connected cards bonus (less than 4 gap)
            if rank_values[0] - rank_values[1] < 4:
                strength += 0.05
        else:  # No high cards
            strength = 0.1
            if is_suited:
                strength += 0.05
            # Connected cards bonus
            if rank_values[0] - rank_values[1] <= 1:
                strength += 0.1
            elif rank_values[0] - rank_values[1] <= 3:
                strength += 0.05
    
    return min(1.0, max(0.0, strength))

def _aggressive_preflop_strength(hand):
    """Aggressive pre-flop hand strength calculation (plays more hands)"""
    rank_values, is_pair, is_suited = extract_card_values(hand)
    
    # Base strength - slightly higher base values than conservative
    strength = 0.1  # Even the worst hand gets some play
    
    # Pairs
    if is_pair:
        if rank_values[0] >= 10:  # TT, JJ, QQ, KK, AA
            strength = 0.85 + 0.03 * (rank_values[0] - 10)  # 0.85 for TT up to 0.97 for AA
        else:
            strength = 0.5 + 0.035 * (rank_values[0] - 2)  # 0.5 for 22 up to 0.78 for 99
    
    # Non-pairs
    else:
        # Both cards are high (10 or higher)
        high_cards = sum(1 for rank in rank_values if rank >= 10)
        
        if high_cards == 2:  # Both cards are high
            strength = 0.65 + 0.02 * (rank_values[0] + rank_values[1] - 20)
            if is_suited:
                strength += 0.1
        elif high_cards == 1:  # One high card
            strength = 0.4 + 0.03 * rank_values[0]
            if is_suited:
                strength += 0.1
            # Connected cards bonus (less than 5 gap - more generous)
            if rank_values[0] - rank_values[1] < 5:
                strength += 0.05
        else:  # No high cards
            strength = 0.2
            if is_suited:
                strength += 0.1
            # Connected cards bonus - more generous
            if rank_values[0] - rank_values[1] <= 2:
                strength += 0.15
            elif rank_values[0] - rank_values[1] <= 4:
                strength += 0.05
    
    return min(1.0, max(0.0, strength))

def calculate_draw_potential(hand, community_cards, round_name):
    """
    Calculate potential for draws based on the current hand and community cards
    
    Args:
        hand (list): Player's hole cards
        community_cards (list): Community cards on the board
        round_name (str): Current betting round
        
    Returns:
        float: Draw potential as a value between 0 and 1
    """
    # If we're at the river, there's no draw potential
    if round_name == 'river' or len(community_cards) >= 5:
        return 0.0
    
    # Extract suits and ranks
    all_cards = hand + community_cards
    suits = [card[1] for card in all_cards]
    ranks = [RANKS[card[0]] for card in all_cards]
    
    # Count suits for flush draw
    suit_counts = Counter(suits)
    flush_potential = 0.0
    
    # Check for flush draw (4 cards of same suit with more cards to come)
    if max(suit_counts.values()) == 4:
        # On the flop, we'll see 1 more card on turn and 1 on river
        if round_name == 'flop':
            flush_potential = 0.35  # Approx. probability of hitting by the river
        # On the turn, we'll only see 1 more card
        elif round_name == 'turn':
            flush_potential = 0.196  # Approx. probability of hitting on the river
    
    # Check for open-ended straight draw
    ranks = sorted(ranks)
    straight_potential = 0.0
    
    # Check for open-ended straight draws (need 1 card on either end)
    for i in range(len(ranks) - 3):
        # Check for four connected cards
        if ranks[i+3] - ranks[i] == 3:
            # On the flop, we'll see 2 more cards
            if round_name == 'flop':
                straight_potential = 0.31  # Approx. probability of hitting by the river
            # On the turn, we'll only see 1 more card
            elif round_name == 'turn':
                straight_potential = 0.174  # Approx. probability of hitting on the river
            break
    
    # Return the maximum draw potential
    return max(flush_potential, straight_potential)

def get_canonical_preflop_hand(hand):
    """
    Convert a hand to its canonical form for preflop ranking lookup
    
    Args:
        hand (list): Two-card hand (e.g., ['Ah', 'Kd'])
        
    Returns:
        str: Canonical form (e.g., 'AKo' for Ace-King offsuit, 'AKs' for Ace-King suited)
    """
    # Extract ranks and suits
    ranks = [card[0] for card in hand]
    suits = [card[1] for card in hand]
    
    # Get rank values
    rank_values = []
    for rank in ranks:
        if rank == 'A':
            rank_values.append((14, 'A'))
        elif rank == 'K':
            rank_values.append((13, 'K'))
        elif rank == 'Q':
            rank_values.append((12, 'Q'))
        elif rank == 'J':
            rank_values.append((11, 'J'))
        elif rank == 'T':
            rank_values.append((10, 'T'))
        else:
            rank_values.append((int(rank), rank))
    
    # Sort by rank value (descending)
    rank_values.sort(reverse=True)
    
    # Check if pair
    if rank_values[0][0] == rank_values[1][0]:
        return f"{rank_values[0][1]}{rank_values[1][1]}"
    
    # Check if suited
    is_suited = suits[0] == suits[1]
    suffix = 's' if is_suited else 'o'
    
    # Return in canonical form: higher rank first, then lower rank, then 's' or 'o'
    return f"{rank_values[0][1]}{rank_values[1][1]}{suffix}"

