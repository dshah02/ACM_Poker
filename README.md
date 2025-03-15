# ACM Poker Bot Competition

A Texas Hold'em poker bot competition framework for heads-up matches. This system allows you to create, test, and compete poker bots against each other.

## Overview

This framework provides:

1. A poker game engine that handles all the rules of Texas Hold'em
2. A hand evaluation system to determine winning hands
3. Example bot strategies to demonstrate the API
4. A tournament manager to run matches and competitions
5. A visual interface using Pygame to display poker matches

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Pygame (for visualization features)

### Installation 

Install the required packages:

```bash
pip install pygame tqdm
```

### Running the Demo

To run a demonstration of the poker system, simply execute:

```bash
python game.py
```

This will run a visual demonstration match between the example bots.

You can also modify the main block in `poker_tournament.py` to run other types of demonstrations:

```python
# Option 1: Run a detailed hand for debugging
run_detailed_hand(bot1, bot2)

# Option 2: Run a match
tournament = PokerTournament()
tournament.run_match(bot1, bot2, num_hands=10)

# Option 3: Run a tournament
tournament = PokerTournament()
tournament.run_tournament([bot1, bot2], num_matches=2, hands_per_match=10)

# Option 4: Run a visual demo match
run_visual_demo(delay=0.5)

# Option 5: Run a tournament with visual finals
run_visual_tournament([bot1, bot2], matches_per_pair=1, hands_per_match=5, delay=0.5)
```

## System Components

### Poker Engine (`poker_engine.py`)

The core game engine that implements Texas Hold'em rules:
- Manages game state
- Deals cards
- Processes player actions
- Handles betting rounds
- Determines winners

### Hand Evaluator (`hand_evaluator.py`)

Provides functionality to evaluate poker hands:
- Identifies hand types (pair, flush, etc.)
- Evaluates the best 5-card hand from 7 cards
- Compares hands to determine the winner
- Calculates preflop hand strength
- Provides percentile rankings for preflop hands

### Example Strategies

Two example bot strategies are provided:

1. **Conservative Bot** (`example_strategy_1.py`): A cautious bot that plays based on hand strength and folds weaker hands
2. **Aggressive Bot** (`example_strategy_2.py`): A more aggressive bot that bluffs frequently and plays more hands

### Tournament Manager (`poker_tournament.py`)

Manages matches and tournaments:
- Runs individual matches
- Conducts round-robin tournaments
- Tracks and reports results
- Can run visual matches with Pygame

### Visualization (`poker_visualizer.py`)

A Pygame-based visualization system that:
- Displays cards, chips, and the poker table
- Shows player actions and betting in real-time
- Dramatizes important moments like showdowns
- Displays hand strength and percentile rankings
- Provides a UI for tournament finals

## Creating Your Own Bot

To create your own poker bot:

1. Create a new Python class with a `get_action` method that takes a game state dictionary and returns an action
2. The bot must implement the following methods:
   - `__init__(self, name)`: Constructor that accepts a name parameter
   - `__str__(self)`: Return the bot's name
   - `get_action(self, game_state)`: Return the bot's action based on the current game state

### Bot Interface

Your bot must implement the `get_action` method with this signature:

```python
def get_action(self, game_state):
    """
    Args:
        game_state (dict): The current state of the game from the player's perspective
            
    Returns:
        dict: Action to take
    """
    # Your strategy logic here
    # Must return a dictionary with an 'action' key and possibly an 'amount' key
```

### Game State

The game state provided to your bot includes:

- `player_idx`: Your position (0 or 1)
- `hand`: Your hole cards (e.g., ['Ah', 'Kd'])
- `community_cards`: Shared cards on the board
- `pot`: Total pot size
- `current_bet`: Current bet to call
- `my_stack`: Your remaining chips
- `opponent_stack`: Opponent's remaining chips
- `my_bet`: Amount you've already bet in this round
- `opponent_bet`: Amount opponent has bet in this round
- `min_raise`: Minimum raise amount
- `ante`: Ante amount

### Valid Actions

Your bot must return one of these actions:

- `{'action': 'fold'}`: Give up your hand
- `{'action': 'check'}`: Pass the action (only when there's no bet to call)
- `{'action': 'call'}`: Match the current bet
- `{'action': 'bet', 'amount': X}`: Place a bet of amount X (when there's no existing bet)
- `{'action': 'raise', 'amount': X}`: Raise to a total of X (when there's an existing bet)

## Example Bot Template

```python
class MyPokerBot:
    def __init__(self, name="MyPokerBot"):
        self.name = name
        
    def __str__(self):
        return self.name
        
    def get_action(self, game_state):
        # Extract information from game state
        hand = game_state['hand']
        community_cards = game_state['community_cards']
        pot = game_state['pot']
        current_bet = game_state['current_bet']
        my_stack = game_state['my_stack']
        
        # Implement your strategy here
        # This is a very simple example that just calls any bet
        if current_bet == 0:
            return {'action': 'check'}
        else:
            return {'action': 'call'}
```

## Running Your Own Tournament

To run a tournament with your own bots:

```python
from poker_tournament import PokerTournament
from my_bot import MyPokerBot
from example_strategy_1 import ConservativeBot

# Create bot instances
my_bot = MyPokerBot("MyAwesomeBot")
opponent = ConservativeBot("ConservativeBot")

# Create tournament manager
tournament = PokerTournament(starting_stack=1000, ante=10)

# Run a match
tournament.run_match(my_bot, opponent, num_hands=100)

# Run a tournament with multiple bots
bots = [my_bot, opponent, AnotherBot("AnotherBot")]
tournament.run_tournament(bots, num_matches=5, hands_per_match=50)

# Run a tournament with visualized finals
tournament.run_tournament(bots, num_matches=5, hands_per_match=50, visualize_finals=True)
```

### Running Visual Matches

For a more engaging experience, you can run matches with visual display:

```python
from poker_tournament import run_visual_match, run_visual_tournament
from my_bot import MyPokerBot
from example_strategy_1 import ConservativeBot

# Create bot instances
my_bot = MyPokerBot("MyAwesomeBot")
opponent = ConservativeBot("ConservativeBot")

# Run a single visual match
run_visual_match(my_bot, opponent, hands=5, delay=0.5)

# Run a tournament with visualization for the finals
run_visual_tournament([my_bot, opponent], matches_per_pair=2, hands_per_match=10, delay=0.5)
```

## Visualization Controls

When running a visualization:
- Press any key to advance through the stages of the match
- Press ESC to quit
- Watch as cards are dealt, bets are made, and hands are evaluated
- Hand percentiles and rankings are displayed to help understand the quality of hands

## Hand Evaluation Features

The `hand_evaluator.py` module provides useful functions for evaluating poker hands:

```python
from hand_evaluator import calculate_preflop_strength, preflop_percentile, preflop_rank_description

# Get the preflop strength of a hand (0.0 - 1.0)
strength = calculate_preflop_strength(['Ah', 'Kh'], style='balanced')

# Get the percentile of a preflop hand (0.0 - 1.0)
percentile = preflop_percentile(['Ah', 'Kh'])

# Get a description of a preflop hand
rank, description = preflop_rank_description(['Ah', 'Kh'])
print(f"{rank} - {description}")  # Example: "Premium hand - Suited Ace-King"
```
