"""
Poker Tournament Visualizer with Pygame
Creates a visual representation of poker hands for the tournament finals
"""

import pygame
import os
import time
import random
from .poker_engine import PokerEngine
from hand_evaluator import preflop_rank_description, evaluate_hand, calculate_head_to_head_equity
from .utils import hand_type_str, compare_hands

# Initialize pygame
pygame.init()
pygame.font.init()

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GRAY = (128, 128, 128)
GOLD = (212, 175, 55)

# Card dimensions
CARD_WIDTH = 80
CARD_HEIGHT = 120

# Chip size
CHIP_RADIUS = 15

# Paths to resources
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CARD_BACK_IMAGE = None  # Will be loaded in load_resources

# Card suits and colors
SUITS = {
    'h': ('hearts', RED),
    'd': ('diamonds', RED),
    's': ('spades', BLACK),
    'c': ('clubs', BLACK)
}

class PokerVisualizer:
    """Visualizer for poker tournaments using pygame"""
    
    def __init__(self, fullscreen=False):
        """Initialize the pygame visualizer"""
        flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption("ACM Poker Bot Tournament")
        
        # Set up fonts
        self.large_font = pygame.font.SysFont('Arial', 36)
        self.medium_font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Load card images
        self.card_images = {}
        self.card_back = None
        self.chip_image = None
        self.load_resources()
        
        # Animation settings
        self.animation_speed = 0.5  # seconds per action
        self.running = True
        
        # Game state
        self.engine = None
        self.player1 = None
        self.player2 = None
        self.round_state = {}
        self.last_action = None
        self.pot_display = 0
        self.winner = None
        
        # Cache for equity calculations
        self.equity_cache = {}
        self.player1_equity = 0.5
        self.player2_equity = 0.5
        
    def load_resources(self):
        """Load card images and other resources"""
        # Create simple card representations with pygame
        # In a real implementation, you might load actual card images
        for rank in "23456789TJQKA":
            for suit, (suit_name, color) in SUITS.items():
                # Create a card surface
                card_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                card_surf.fill(WHITE)
                
                # Add border
                pygame.draw.rect(card_surf, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)
                
                # Add rank and suit
                # Convert 'T', 'J', 'Q', 'K', 'A' to their full names for clarity
                display_rank = rank
                if rank == 'T':
                    display_rank = '10'
                elif rank == 'J':
                    display_rank = 'J'
                elif rank == 'Q':
                    display_rank = 'Q'
                elif rank == 'K':
                    display_rank = 'K'
                elif rank == 'A':
                    display_rank = 'A'
                
                rank_text = self.medium_font.render(display_rank, True, color)
                card_surf.blit(rank_text, (5, 5))
                
                # Add suit symbol
                suit_symbol = {
                    'hearts': '♥',
                    'diamonds': '♦',
                    'clubs': '♣',
                    'spades': '♠'
                }[suit_name]
                
                suit_text = self.medium_font.render(suit_symbol, True, color)
                card_surf.blit(suit_text, (5, 30))
                
                # Store card image
                self.card_images[f"{rank}{suit}"] = card_surf
        
        # Create card back
        card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        card_back.fill(BLUE)
        pygame.draw.rect(card_back, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)
        for i in range(0, CARD_WIDTH, 10):
            pygame.draw.line(card_back, BLACK, (i, 0), (i, CARD_HEIGHT), 1)
        for i in range(0, CARD_HEIGHT, 10):
            pygame.draw.line(card_back, BLACK, (0, i), (CARD_WIDTH, i), 1)
        
        self.card_back = card_back
        
        # Create chip image
        chip = pygame.Surface((CHIP_RADIUS * 2, CHIP_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(chip, RED, (CHIP_RADIUS, CHIP_RADIUS), CHIP_RADIUS)
        pygame.draw.circle(chip, WHITE, (CHIP_RADIUS, CHIP_RADIUS), CHIP_RADIUS - 2, 2)
        self.chip_image = chip
        
    def setup_match(self, player1, player2, starting_stack=1000, ante=10):
        """Set up a new match between two players"""
        self.player1 = player1
        self.player2 = player2
        self.engine = PokerEngine(player1, player2, starting_stack, ante)
        self.round_state = {}
        self.last_action = None
        self.pot_display = 0
        self.winner = None
        
    def run_match(self, num_hands=10, delay=1.0, debug=False):
        """Run a full match with visualization"""
        hands_played = 0
        hands_won = {self.player1: 0, self.player2: 0}
        
        # Display match info
        self.clear_screen()
        self.draw_text(f"Starting match: {self.player1} vs {self.player2}", SCREEN_WIDTH // 2, 100, self.large_font, centered=True)
        self.draw_text(f"Starting stacks: {self.engine.starting_stack} chips", SCREEN_WIDTH // 2, 150, self.medium_font, centered=True)
        self.draw_text(f"Ante: {self.engine.ante} chips", SCREEN_WIDTH // 2, 180, self.medium_font, centered=True)
        self.draw_text(f"Press any key to start...", SCREEN_WIDTH // 2, 400, self.medium_font, centered=True)
        pygame.display.flip()
        
        # Wait for key press
        self.wait_for_key()
        
        # Play hands
        while (hands_played < num_hands and
               self.engine.stacks[self.player1] > 0 and
               self.engine.stacks[self.player2] > 0):
               
            # Pre-generate cards for upcoming hand
            next_round_num = self.engine.current_round + 1
            self.engine.pregenerate_round(next_round_num)
            
            # Display hand number
            self.clear_screen()
            self.draw_text(f"Hand #{hands_played + 1}", SCREEN_WIDTH // 2, 80, self.large_font, centered=True)
            self.draw_text(f"Stacks: {self.player1}: {self.engine.stacks[self.player1]}, {self.player2}: {self.engine.stacks[self.player2]}", 
                          SCREEN_WIDTH // 2, 130, self.medium_font, centered=True)
            
            # Only show JSON editing info in debug mode
            if debug:
                self.draw_text(f"Cards pre-generated and saved to poker_rounds/round_{next_round_num}_cards.json", 
                              SCREEN_WIDTH // 2, 180, self.medium_font, centered=True)
                self.draw_text(f"Edit that file now if you want to modify the upcoming hand", 
                              SCREEN_WIDTH // 2, 210, self.medium_font, centered=True)
                self.draw_text(f"Press any key when ready to continue with this hand...", 
                              SCREEN_WIDTH // 2, 240, self.medium_font, centered=True)
            else:
                self.draw_text(f"Press any key to continue with this hand...", 
                              SCREEN_WIDTH // 2, 180, self.medium_font, centered=True)
            
            pygame.display.flip()
            
            # Wait for key press (giving time to edit the JSON if desired)
            self.wait_for_key()
            self.wait_with_events(delay)
            
            # Run a hand with visualization
            winner = self.run_visual_hand()
            
            if winner:
                hands_won[winner] = hands_won.get(winner, 0) + 1
                
            hands_played += 1
            
            # Display result
            self.clear_screen()
            if winner:
                self.draw_text(f"Winner: {winner}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, self.large_font, centered=True)
            else:
                self.draw_text("Split pot", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, self.large_font, centered=True)
                
            self.draw_text(f"Press any key to continue...", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, self.medium_font, centered=True)
            pygame.display.flip()
            
            # Wait for key press
            self.wait_for_key()
            
        # Display final results
        self.clear_screen()
        self.draw_text("Match Results", SCREEN_WIDTH // 2, 100, self.large_font, centered=True)
        self.draw_text(f"Hands played: {hands_played}", SCREEN_WIDTH // 2, 170, self.medium_font, centered=True)
        self.draw_text(f"Hands won: {self.player1}: {hands_won[self.player1]}, {self.player2}: {hands_won[self.player2]}", 
                      SCREEN_WIDTH // 2, 210, self.medium_font, centered=True)
        self.draw_text(f"Final stacks: {self.player1}: {self.engine.stacks[self.player1]}, {self.player2}: {self.engine.stacks[self.player2]}", 
                      SCREEN_WIDTH // 2, 250, self.medium_font, centered=True)
        
        # Determine match winner
        if self.engine.stacks[self.player1] > self.engine.stacks[self.player2]:
            match_winner = self.player1
        elif self.engine.stacks[self.player2] > self.engine.stacks[self.player1]:
            match_winner = self.player2
        else:
            match_winner = None
            
        if match_winner:
            self.draw_text(f"Match winner: {match_winner}", SCREEN_WIDTH // 2, 320, self.large_font, centered=True, color=GOLD)
        else:
            self.draw_text("Match tied", SCREEN_WIDTH // 2, 320, self.large_font, centered=True)
            
        self.draw_text(f"Press any key to exit...", SCREEN_WIDTH // 2, 400, self.medium_font, centered=True)
        pygame.display.flip()
        
        # Wait for key press
        self.wait_for_key()
        
        return match_winner
    
    def run_visual_hand(self):
        """Run a single hand with visualization"""
        # Check for predefined cards - load right before using to capture any edits
        next_round_num = self.engine.current_round + 1
        predefined_cards = self.engine.load_predefined_cards(next_round_num)
        
        if predefined_cards:
            print(f"Loaded predefined cards from poker_rounds/round_{next_round_num}_cards.json")
            print(f"Using cards: Player 1: {predefined_cards['player1']}, Player 2: {predefined_cards['player2']}")
            print(f"Community cards will be: {predefined_cards['community']}")
        
        # Initialize round with predefined cards if available
        ante_winner = self.engine.initialize_round(predefined_cards)
        self.pot_display = self.engine.pot
        
        # Print debug information
        print("\n" + "="*80)
        print(f"HAND #{self.engine.current_round} - STARTING")
        print("="*80)
        print(f"Player 1 ({self.player1}): Stack = {self.engine.stacks[self.player1]}")
        print(f"Player 2 ({self.player2}): Stack = {self.engine.stacks[self.player2]}")
        print(f"Ante: {self.engine.ante}")
        
        # Print the cards that will be used (for debugging)
        print(f"Player 1 cards: {self.engine.player_hands[self.player1]}")
        print(f"Player 2 cards: {self.engine.player_hands[self.player2]}")
        if predefined_cards:
            print(f"Community cards (will be): {predefined_cards['community']}")
            print("Using predefined cards from JSON file")
        
        # Check if a player couldn't pay the ante
        if ante_winner:
            print(f"\nWINNER (can't pay ante): {ante_winner}")
            print(f"Final stacks - {self.player1}: {self.engine.stacks[self.player1]}, {self.player2}: {self.engine.stacks[self.player2]}")
            
            # Display on screen
            self.clear_screen()
            self.draw_table()
            self.draw_player_stacks()
            self.draw_text(f"{self.player1 if self.player1 != ante_winner else self.player2} can't pay ante!", 
                          SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, 
                          self.medium_font, centered=True, color=RED)
            self.draw_text(f"Winner: {ante_winner}", 
                          SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 
                          self.large_font, centered=True, color=GOLD)
            # Make sure everything is drawn before pausing
            pygame.display.flip()
            self.wait_with_events(self.animation_speed * 3)
            
            self.winner = ante_winner
            return ante_winner
            
        print(f"Starting Pot: {self.engine.pot}")
        
        # Print hole cards
        print("\nHole Cards:")
        p1_hand = self.engine.player_hands[self.player1]
        p2_hand = self.engine.player_hands[self.player2]
        
        # Get preflop hand descriptions
        p1_desc = preflop_rank_description(p1_hand)
        p2_desc = preflop_rank_description(p2_hand)
        
        print(f"{self.player1}: {p1_hand} - {p1_desc[0]} ({p1_desc[1]})")
        print(f"{self.player2}: {p2_hand} - {p2_desc[0]} ({p2_desc[1]})")
        
        # Display player hands initially with cards face down
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=False)
        self.draw_pot()
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed)
        
        # Now reveal the hole cards
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_pot()
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed * 2)
        
        # Pre-flop betting round
        print("\nPRE-FLOP BETTING:")
        winner = self._visual_preflop_betting()
        
        # Print betting results
        print(f"  Pot after pre-flop: {self.engine.pot}")
        print(f"  Player stacks - {self.player1}: {self.engine.stacks[self.player1]}, {self.player2}: {self.engine.stacks[self.player2]}")
        
        # If someone folded, end the hand (pot already transferred in _visual_betting_round)
        if winner:
            print(f"\nWINNER (by fold): {winner}")
            self.winner = winner
            return winner
            
        # Deal flop
        print("\nFLOP:")
        self._visual_flop()
        
        # Print flop cards
        print(f"  Flop: {self.engine.community_cards}")
        
        # Flop betting round
        print("\nFLOP BETTING:")
        winner = self._visual_flop_betting()
        
        # Print betting results
        print(f"  Pot after flop: {self.engine.pot}")
        print(f"  Player stacks - {self.player1}: {self.engine.stacks[self.player1]}, {self.player2}: {self.engine.stacks[self.player2]}")
        
        # If someone folded, end the hand (pot already transferred in _visual_betting_round)
        if winner:
            print(f"\nWINNER (by fold): {winner}")
            self.winner = winner
            return winner
            
        # Deal turn
        print("\nTURN:")
        self._visual_turn()
        
        # Print turn card
        print(f"  Turn: {self.engine.community_cards[3]}")
        print(f"  Board: {self.engine.community_cards}")
        
        # Turn betting round
        print("\nTURN BETTING:")
        winner = self._visual_turn_betting()
        
        # Print betting results
        print(f"  Pot after turn: {self.engine.pot}")
        print(f"  Player stacks - {self.player1}: {self.engine.stacks[self.player1]}, {self.player2}: {self.engine.stacks[self.player2]}")
        
        # If someone folded, end the hand (pot already transferred in _visual_betting_round)
        if winner:
            print(f"\nWINNER (by fold): {winner}")
            self.winner = winner
            return winner
            
        # Deal river
        print("\nRIVER:")
        self._visual_river()
        
        # Print river card
        print(f"  River: {self.engine.community_cards[4]}")
        print(f"  Final board: {self.engine.community_cards}")
        
        # River betting round
        print("\nRIVER BETTING:")
        winner = self._visual_river_betting()
        
        # Print betting results
        print(f"  Final pot: {self.engine.pot}")
        print(f"  Player stacks - {self.player1}: {self.engine.stacks[self.player1]}, {self.player2}: {self.engine.stacks[self.player2]}")
        
        # If someone folded, end the hand (pot already transferred in _visual_betting_round)
        if winner:
            print(f"\nWINNER (by fold): {winner}")
            self.winner = winner
            return winner
            
        # Showdown
        print("\nSHOWDOWN:")
        winner = self._visual_showdown()
        
        self.winner = winner
        return winner
    
    def _visual_preflop_betting(self):
        """Execute preflop betting with visualization"""
        # Display the round
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_pot()
        self.draw_text("Pre-Flop Betting", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed)
        
        # Execute the betting round
        winner = self._visual_betting_round('preflop')
        
        return winner
        
    def _visual_flop(self):
        """Deal and display the flop"""
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_pot()
        self.draw_text("Dealing Flop", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed)
        
        # Deal flop (3 cards)
        self.engine._deal_flop()
        
        # Update display with flop cards
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_community_cards()
        self.draw_pot()
        self.draw_text("Flop Dealt", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed * 2)
        
    def _visual_flop_betting(self):
        """Execute flop betting with visualization"""
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_community_cards()
        self.draw_pot()
        self.draw_text("Flop Betting", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed)
        
        # Execute the betting round
        winner = self._visual_betting_round('flop')
        
        return winner
        
    def _visual_turn(self):
        """Deal and display the turn card"""
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_community_cards()
        self.draw_pot()
        self.draw_text("Dealing Turn", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed)
        
        # Deal turn (1 card)
        self.engine._deal_turn()
        
        # Update display with turn card
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_community_cards()
        self.draw_pot()
        self.draw_text("Turn Dealt", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed * 2)
        
    def _visual_turn_betting(self):
        """Execute turn betting with visualization"""
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_community_cards()
        self.draw_pot()
        self.draw_text("Turn Betting", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed)
        
        # Execute the betting round
        winner = self._visual_betting_round('turn')
        
        return winner
        
    def _visual_river(self):
        """Deal and display the river card"""
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_community_cards()
        self.draw_pot()
        self.draw_text("Dealing River", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed)
        
        # Deal river (1 card)
        self.engine._deal_river()
        
        # Update display with river card
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_community_cards()
        self.draw_pot()
        self.draw_text("River Dealt", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed * 2)
        
    def _visual_river_betting(self):
        """Execute river betting with visualization"""
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_community_cards()
        self.draw_pot()
        self.draw_text("River Betting", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed)
        
        # Execute the betting round
        winner = self._visual_betting_round('river')
        
        return winner
        
    def _visual_showdown(self):
        """Execute showdown with visualization"""
        # Clear screen and draw current state
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_community_cards()
        self.draw_pot()
        self.draw_text("Showdown", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        # Make sure everything is drawn before pausing
        pygame.display.flip()
        self.wait_with_events(self.animation_speed * 2)
        
        # Evaluate hands
        player1 = self.engine.players[0]
        player2 = self.engine.players[1]
        
        hand1 = self.engine.player_hands[player1] + self.engine.community_cards
        hand2 = self.engine.player_hands[player2] + self.engine.community_cards
        
        best_hand1 = evaluate_hand(hand1)
        best_hand2 = evaluate_hand(hand2)
        
        # Display best hands
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_community_cards()
        self.draw_pot()
        self.draw_text("Showdown", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        
        # Show best hands - Fix access to hand type which is a dict key 'type', not an index
        self.draw_text(f"{player1}: {hand_type_str(best_hand1)}", 250, SCREEN_HEIGHT - 220, self.medium_font, color=WHITE)
        self.draw_text(f"{player2}: {hand_type_str(best_hand2)}", SCREEN_WIDTH - 250, 80, self.medium_font, color=WHITE)
        pygame.display.flip()
        self.wait_with_events(self.animation_speed * 2)
        
        # Compare hands and determine winner
        result = compare_hands(best_hand1, best_hand2)
        
        if result > 0:
            winner = player1
            self.draw_text(f"{player1} WINS!", SCREEN_WIDTH // 2, 160, self.large_font, centered=True, color=GOLD)
            # Show pot transfer
            prev_pot = self.pot_display
            self.draw_text(f"Pot: {prev_pot} → transferred to {winner}", SCREEN_WIDTH // 2, 210, self.medium_font, centered=True, color=GOLD)
            pygame.display.flip()
            self.wait_with_events(self.animation_speed * 2)
            
            # Transfer pot and update display
            self.engine._end_round(winner)
            self.pot_display = 0
        elif result < 0:
            winner = player2
            self.draw_text(f"{player2} WINS!", SCREEN_WIDTH // 2, 160, self.large_font, centered=True, color=GOLD)
            # Show pot transfer
            prev_pot = self.pot_display
            self.draw_text(f"Pot: {prev_pot} → transferred to {winner}", SCREEN_WIDTH // 2, 210, self.medium_font, centered=True, color=GOLD)
            pygame.display.flip()
            self.wait_with_events(self.animation_speed * 2)
            
            # Transfer pot and update display
            self.engine._end_round(winner)
            self.pot_display = 0
        else:
            # Split pot
            self.draw_text("SPLIT POT", SCREEN_WIDTH // 2, 160, self.large_font, centered=True, color=GOLD)
            prev_pot = self.pot_display
            split_amount = prev_pot // 2
            
            # Show pot splitting animation
            self.draw_text(f"Pot: {prev_pot} → split equally ({split_amount} each)", SCREEN_WIDTH // 2, 210, self.medium_font, centered=True, color=GOLD)
            pygame.display.flip()
            self.wait_with_events(self.animation_speed * 2)
            
            # Actually split the pot
            self.engine.stacks[player1] += split_amount
            self.engine.stacks[player2] += split_amount
            # Handle odd chip if pot is odd
            if prev_pot % 2 == 1:
                # Give the odd chip to the player in position (player 0)
                self.engine.stacks[player1] += 1
                self.draw_text(f"Odd chip goes to {player1}", SCREEN_WIDTH // 2, 250, self.small_font, centered=True, color=GOLD)
            
            self.pot_display = 0
            pygame.display.flip()
            self.wait_with_events(self.animation_speed * 2)
            return None
            
        # Final display with updated stacks
        self.clear_screen()
        self.draw_table()
        self.draw_player_stacks()
        self.draw_player_hands(show_cards=True)
        self.draw_community_cards()
        self.draw_pot()
        self.draw_text("Showdown Complete", SCREEN_WIDTH // 2, 80, self.large_font, centered=True, color=GOLD)
        if result > 0:
            self.draw_text(f"{player1} WINS!", SCREEN_WIDTH // 2, 160, self.large_font, centered=True, color=GOLD)
        elif result < 0:
            self.draw_text(f"{player2} WINS!", SCREEN_WIDTH // 2, 160, self.large_font, centered=True, color=GOLD)
        else:
            self.draw_text("SPLIT POT", SCREEN_WIDTH // 2, 160, self.large_font, centered=True, color=GOLD)
        pygame.display.flip()
        self.wait_with_events(self.animation_speed * 2)
        
        return player1 if result > 0 else player2 if result < 0 else None
    
    def _visual_betting_round(self, round_name):
        """Execute a betting round with visualization"""
        # Reset betting state for this round
        acted_players = set()
        all_players_acted = False
        
        # Reset current bet at the start of the round
        current_bet_at_start = self.engine.current_bet
        
        # Reset betting state for this round
        self.engine.current_bet = 0
        
        # Clear player bets from previous round
        if round_name != 'preflop':
            # Don't reset current_player_idx - preserve the same starting player as pre-flop
            # Reset player bets - this is the fix for bets carrying over between rounds
            self.engine.round_state['player0_bet'] = 0
            self.engine.round_state['player1_bet'] = 0
            
        # Continue until all players have acted and bets are equal
        while not all_players_acted or any(self.engine.round_state.get(f"player{i}_bet", 0) != self.engine.current_bet 
                                          for i in range(2) if self.engine.stacks[self.engine.players[i]] > 0):
                                          
            current_player = self.engine.players[self.engine.current_player_idx]
            
            # Debug - print current state
            print(f"  Current player: {current_player}")
            print(f"  Current bets - Player 1: {self.engine.round_state.get('player0_bet', 0)}, Player 2: {self.engine.round_state.get('player1_bet', 0)}")
            print(f"  Current pot: {self.engine.pot}")
            
            # Update display to show current player
            self.clear_screen()
            self.draw_table()
            self.draw_player_stacks()
            self.draw_player_hands(show_cards=True)
            self.draw_community_cards()
            self.draw_pot()
            
            # Highlight current player
            player_position = (100, 600) if current_player == self.player1 else (SCREEN_WIDTH - 100, 600)
            pygame.draw.circle(self.screen, BLUE, player_position, 50, 5)
            
            # Show current bet to call
            player_idx = self.engine.players.index(current_player)
            current_player_bet = self.engine.round_state.get(f'player{player_idx}_bet', 0)
            amount_to_call = self.engine.current_bet - current_player_bet
            
            # Debug - print what needs to be called
            print(f"  Current bet: {self.engine.current_bet}, Player already bet: {current_player_bet}")
            print(f"  Amount to call: {amount_to_call}")
            
            if amount_to_call > 0:
                self.draw_text(f"To call: {amount_to_call}", SCREEN_WIDTH // 2, 130, self.medium_font, centered=True)
            
            self.draw_text(f"{current_player}'s turn...", SCREEN_WIDTH // 2, 90, self.medium_font, centered=True)
            
            # Make sure everything is drawn before pausing
            pygame.display.flip()
            
            # Slight pause for drama
            self.wait_with_events(self.animation_speed)
            
            # Get player action
            player_view = self.engine._get_player_view(current_player)
            print(f"  Player view: {player_view}")
            
            action = current_player.get_action(player_view)
            
            # Debug - print the action taken
            print(f"  Action taken: {action}")
            
            # Display the action
            action_text = f"{action['action'].upper()}"
            if action['action'] in ['bet', 'raise']:
                # Show "CHECK" for bets or raises with 0 amount
                if 'amount' in action and action['amount'] == 0:
                    action_text = "CHECK"
                elif 'amount' in action and action['amount'] < self.engine.round_state.get('min_raise', 0):
                    action_text = "CHECK"
                elif 'amount' in action:
                    action_text += f" {action['amount']}"
            
            # Display action with larger text and more prominent color
            self.last_action = f"{current_player}: {action_text}"
            
            # Update the screen with the action
            self.clear_screen()
            self.draw_table()
            self.draw_player_stacks()
            self.draw_player_hands(show_cards=True)
            self.draw_community_cards()
            self.draw_pot()
            self.draw_text(self.last_action, SCREEN_WIDTH // 2, 160, self.large_font, centered=True, color=GOLD)
            
            # Make sure everything is drawn before pausing
            pygame.display.flip()
            
            # Process the action
            folded = self.engine._process_action(current_player, action)
            self.pot_display = self.engine.pot
            
            # Debug - print the result of the action
            print(f"  After action - Folded: {folded}, Pot: {self.engine.pot}")
            print(f"  New bets - Player 1: {self.engine.round_state.get('player0_bet', 0)}, Player 2: {self.engine.round_state.get('player1_bet', 0)}")
            print(f"  Player stacks - {self.player1}: {self.engine.stacks[self.player1]}, {self.player2}: {self.engine.stacks[self.player2]}")
            
            # Update display to show action result
            self.clear_screen()
            self.draw_table()
            self.draw_player_stacks()
            self.draw_player_hands(show_cards=True)
            self.draw_community_cards()
            self.draw_pot()
            
            if self.last_action:
                self.draw_text(self.last_action, SCREEN_WIDTH // 2, 160, self.large_font, centered=True, color=GOLD)
            
            # Make sure everything is drawn before pausing
            pygame.display.flip()
            
            # Pause to show the action
            self.wait_with_events(self.animation_speed * 1.5)
            
            if folded:
                # If player folded, other player wins
                winner = self.engine.players[1 - self.engine.current_player_idx]
                
                # Transfer pot to winner visually
                prev_pot = self.pot_display
                prev_winner_stack = self.engine.stacks[winner]
                
                # Call engine's _end_round to transfer pot to winner
                self.engine._end_round(winner)
                
                # Update pot display
                self.pot_display = 0
                
                # Show pot transfer animation
                self.clear_screen()
                self.draw_table()
                self.draw_player_stacks()  # Will now show updated stack with pot added
                self.draw_player_hands(show_cards=True)
                self.draw_community_cards()
                self.draw_pot()  # Will show empty pot
                
                # Show fold and pot transfer messages
                self.draw_text(f"{current_player} FOLDED", SCREEN_WIDTH // 2, 160, self.large_font, centered=True, color=RED)
                self.draw_text(f"Pot: {prev_pot} → transferred to {winner}", SCREEN_WIDTH // 2, 210, self.medium_font, centered=True, color=GOLD)
                
                # Make sure everything is drawn before pausing
                pygame.display.flip()
                self.wait_with_events(self.animation_speed * 2)
                
                return winner
                
            # Mark this player as having acted
            acted_players.add(current_player)
            
            # Check if all players have acted
            all_players_acted = len(acted_players) == len(self.engine.players)
            
            # Check if we should break out of infinite checking loop
            # If both players have acted and we're back to the same bet as at the start (or both are checking)
            if all_players_acted and (
                  # Either the current bet is the same as at the start of the round
                  self.engine.current_bet == current_bet_at_start or
                  # Or both players are effectively checking (bet 0 or checking directly)
                  (action['action'] in ['check', 'bet', 'raise'] and
                   ('amount' not in action or action['amount'] == 0 or 
                    action['amount'] < self.engine.round_state.get('min_raise', 0)))):
                # If we've gone through the full betting cycle and have reached a stable state, exit
                if action['action'] == 'check' or (
                    action['action'] in ['bet', 'raise'] and 
                    ('amount' not in action or action['amount'] == 0 or 
                     action['amount'] < self.engine.round_state.get('min_raise', 0))):
                    if all(p in acted_players for p in self.engine.players):
                        break
            
            # Move to next player
            self.engine.current_player_idx = (self.engine.current_player_idx + 1) % 2
            
            # Update game state after action
            self.engine._update_game_state()
            
        return None  # No winner yet
    
    def clear_screen(self):
        """Clear the screen"""
        self.screen.fill(BLACK)
        
    def draw_table(self):
        """Draw the poker table"""
        # Draw table background
        table_rect = pygame.Rect(50, 150, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 300)
        pygame.draw.ellipse(self.screen, GREEN, table_rect)
        pygame.draw.ellipse(self.screen, BLACK, table_rect, 3)
        
        # Draw table border
        border_rect = pygame.Rect(40, 140, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 280)
        pygame.draw.ellipse(self.screen, GRAY, border_rect, 5)
        
    def draw_player_hands(self, show_cards=True):
        """Draw the player's hole cards"""
        # Player 1 (bottom)
        x = 150
        y = SCREEN_HEIGHT - 150
        if show_cards:
            for card in self.engine.player_hands[self.player1]:
                self.draw_card(card, x, y)
                x += CARD_WIDTH + 10
                
            # Draw hand percentile
            if len(self.engine.player_hands[self.player1]) == 2 and not self.engine.community_cards:
                hand_info = preflop_rank_description(self.engine.player_hands[self.player1])
                self.draw_text(f"{hand_info[0]} - {hand_info[1]}", 250, y + CARD_HEIGHT + 10, self.small_font)
            
            # Draw win probability after the flop
            elif len(self.engine.community_cards) >= 3:
                # Calculate head-to-head equity only if it's not cached or cards have changed
                p1_hand = self.engine.player_hands[self.player1]
                p2_hand = self.engine.player_hands[self.player2]
                community = self.engine.community_cards
                
                # Create a cache key from the current cards
                cache_key = (
                    tuple(sorted(p1_hand)), 
                    tuple(sorted(p2_hand)), 
                    tuple(sorted(community))
                )
                
                # Only recalculate if not in cache
                if cache_key not in self.equity_cache:
                    print("Calculating new equity...")
                    self.player1_equity, self.player2_equity = calculate_head_to_head_equity(
                        p1_hand,
                        p2_hand,
                        community,
                        num_simulations=200
                    )
                    # Cache the result
                    self.equity_cache[cache_key] = (self.player1_equity, self.player2_equity)
                else:
                    # Use cached value
                    self.player1_equity, self.player2_equity = self.equity_cache[cache_key]
                
                self.draw_text(f"Win prob: {self.player1_equity:.1%}", 250, y + CARD_HEIGHT + 10, self.small_font, color=RED)
        else:
            for _ in range(2):
                self.screen.blit(self.card_back, (x, y))
                x += CARD_WIDTH + 10
                
        # Player 2 (top)
        x = SCREEN_WIDTH - 150 - (CARD_WIDTH + 10) * 2
        y = 150
        if show_cards:
            for card in self.engine.player_hands[self.player2]:
                self.draw_card(card, x, y)
                x += CARD_WIDTH + 10
                
            # Draw hand percentile
            if len(self.engine.player_hands[self.player2]) == 2 and not self.engine.community_cards:
                hand_info = preflop_rank_description(self.engine.player_hands[self.player2])
                self.draw_text(f"{hand_info[0]} - {hand_info[1]}", SCREEN_WIDTH - 250, y + CARD_HEIGHT + 10, self.small_font)
            
            # Draw win probability after the flop
            elif len(self.engine.community_cards) >= 3:
                # We already calculated this in the player 1 section, so we just use player2_equity
                self.draw_text(f"Win prob: {self.player2_equity:.1%}", SCREEN_WIDTH - 250, y + CARD_HEIGHT + 10, self.small_font, color=RED)
        else:
            for _ in range(2):
                self.screen.blit(self.card_back, (x, y))
                x += CARD_WIDTH + 10
                
        # Draw player names
        self.draw_text(str(self.player1), 250, SCREEN_HEIGHT - 190, self.medium_font)
        self.draw_text(str(self.player2), SCREEN_WIDTH - 250, 110, self.medium_font)
        
    def draw_community_cards(self):
        """Draw the community cards"""
        if not self.engine.community_cards:
            return
            
        x = (SCREEN_WIDTH - (CARD_WIDTH + 10) * min(5, len(self.engine.community_cards)) + 10) // 2
        y = (SCREEN_HEIGHT - CARD_HEIGHT) // 2
        
        for card in self.engine.community_cards:
            self.draw_card(card, x, y)
            x += CARD_WIDTH + 10
            
    def draw_card(self, card, x, y):
        """Draw a single card"""
        if card in self.card_images:
            self.screen.blit(self.card_images[card], (x, y))
        else:
            # Fallback if image not found
            card_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            card_surf.fill(WHITE)
            pygame.draw.rect(card_surf, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)
            self.screen.blit(card_surf, (x, y))
            
            # Draw card text
            card_text = self.small_font.render(card, True, BLACK)
            self.screen.blit(card_text, (x + 5, y + 5))
    
    def draw_player_stacks(self):
        """Draw the player's chip stacks"""
        # Player 1 stack - push more to the left
        self.draw_chips(80, SCREEN_HEIGHT - 170, self.engine.stacks[self.player1])
        self.draw_text(f"{self.engine.stacks[self.player1]}", 80, SCREEN_HEIGHT - 120, self.medium_font)
        
        # Player 2 stack - push more to the right
        self.draw_chips(SCREEN_WIDTH - 80, 170, self.engine.stacks[self.player2])
        self.draw_text(f"{self.engine.stacks[self.player2]}", SCREEN_WIDTH - 80, 220, self.medium_font)
        
        # Player bets - adjust positions for better visibility
        player1_bet = self.engine.round_state.get('player0_bet', 0)
        player2_bet = self.engine.round_state.get('player1_bet', 0)
        
        if player1_bet > 0:
            # Push player 1 bet display more to the left and up
            self.draw_chips(80, SCREEN_HEIGHT - 280, player1_bet)
            self.draw_text(f"Bet: {player1_bet}", 80, SCREEN_HEIGHT - 250, self.small_font, color=RED)
            
        if player2_bet > 0:
            # Push player 2 bet display more to the right and down
            self.draw_chips(SCREEN_WIDTH - 80, 280, player2_bet)
            self.draw_text(f"Bet: {player2_bet}", SCREEN_WIDTH - 80, 310, self.small_font, color=RED)
    
    def draw_chips(self, x, y, amount):
        """Draw a stack of chips representing an amount"""
        if amount <= 0:
            return
        
        # Convert amount to integer to avoid TypeError
        amount = int(amount)
            
        # Draw a simplified representation of chips
        chip_count = min(5, amount // 100 + 1)
        for i in range(chip_count):
            self.screen.blit(self.chip_image, (x - CHIP_RADIUS, y - CHIP_RADIUS - i * 5))
    
    def draw_pot(self):
        """Draw the pot"""
        pot_x = SCREEN_WIDTH // 2
        # Raise pot position significantly higher (from -100 to -150)
        pot_y = SCREEN_HEIGHT // 2 - 150
        
        if self.pot_display > 0:
            self.draw_chips(pot_x, pot_y, self.pot_display)
            # Make pot text larger and colorful
            self.draw_text(f"Pot: {self.pot_display}", pot_x, pot_y + 40, self.medium_font, centered=True, color=GOLD)
    
    def draw_text(self, text, x, y, font, color=WHITE, centered=False):
        """Draw text on the screen"""
        text_surface = font.render(text, True, color)
        if centered:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect()
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)
    
    def wait_for_key(self):
        """Wait for a key press"""
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    waiting = False
                    
    def check_events(self):
        """Check pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def wait_with_events(self, duration):
        """Wait for a specified duration while still checking for events"""
        start_time = time.time()
        while time.time() - start_time < duration and self.running:
            self.check_events()
            pygame.time.wait(10)  # Short sleep to avoid CPU hogging

    def quit(self):
        """Quit pygame"""
        pygame.quit()


def run_visual_match(player1, player2, hands=5, delay=1.0, fullscreen=False, debug=False, toggle_players=False):
    """
    Run a match with pygame visualization
    
    Args:
        player1: First player bot
        player2: Second player bot
        hands (int): Number of hands to play
        delay (float): Delay between actions in seconds
        fullscreen (bool): Whether to run in fullscreen mode
        debug (bool): Whether to show debug info and allow JSON editing
        toggle_players (bool): If True, swap player positions (player2 acts first)
        
    Returns:
        The winner of the match
    """
    # If toggle_players is True, swap the players
    if toggle_players:
        player1, player2 = player2, player1
        
    visualizer = PokerVisualizer(fullscreen=fullscreen)
    visualizer.setup_match(player1, player2)
    visualizer.animation_speed = delay
    
    # Add position indicator for clearer UI
    if toggle_players:
        print(f"Player positions: {player1} acts first (originally player2)")
    else:
        print(f"Player positions: {player1} acts first (originally player1)")
    
    try:
        winner = visualizer.run_match(num_hands=hands, delay=delay, debug=debug)
        return winner
    finally:
        visualizer.quit()


def run_visual_tournament(players, matches_per_pair=1, hands_per_match=5, delay=0.5, fullscreen=False, debug=False):
    """
    Run a tournament with visualization for the final match
    
    Args:
        players (list): List of player bots
        matches_per_pair (int): Number of matches between each pair
        hands_per_match (int): Number of hands per match
        delay (float): Delay between actions in seconds
        fullscreen (bool): Whether to run in fullscreen mode
        debug (bool): Whether to show debug info and allow JSON editing
        
    Returns:
        The tournament results
    """
    # Run preliminary matches without visualization
    from poker_tournament import PokerTournament
    tournament = PokerTournament(verbose=True)
    results = tournament.run_tournament(players, matches_per_pair, hands_per_match)
    
    # Get the top two players for the final
    sorted_players = sorted(results.keys(), key=lambda p: results[p]['total_profit'], reverse=True)
    
    if len(sorted_players) >= 2:
        print("\n=== TOURNAMENT FINALS ===")
        finalist1 = sorted_players[0]
        finalist2 = sorted_players[1]
        
        print(f"Finalists: {finalist1} vs {finalist2}")
        print("Press Enter to start the finals...")
        input()
        
        # Run the final match with visualization
        winner = run_visual_match(finalist1, finalist2, hands=hands_per_match, delay=delay, fullscreen=fullscreen, debug=debug)
        
        # Update results to include final
        if winner:
            results[winner]['total_profit'] += 1000  # Bonus points for winning the final
            
        return results, winner
    else:
        return results, sorted_players[0] if sorted_players else None


if __name__ == "__main__":
    print("This module should not be run directly.")
    print("Use game.py to run poker games and tournaments.") 