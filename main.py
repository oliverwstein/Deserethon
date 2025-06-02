# enhanced_main.py - Example integration

import os
from game_engine.game_runner import GameRunner
from interface.cli_runner import CLIRunner

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    """
    Main entry point using the enhanced CLI interface.
    """
    print("Initializing Mormon Trek Survival...")
    
    # Initialize game runner
    game_runner = GameRunner(BASE_DIR)
    
    # Use enhanced CLI instead of basic CLI
    client = CLIRunner(game_runner)
    
    # Run the game
    client.run()

if __name__ == "__main__":
    main()
