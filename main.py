# main.py
import os
from game_engine.game_runner import GameRunner
from interface.cli_runner import CLIHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    game_runner = GameRunner(BASE_DIR)
    client = CLIHandler(game_runner)
    client.run()

if __name__ == "__main__":
    # Ensure your game_engine package can be found.
    # Requires game_engine/__init__.py
    # Run `python main.py` from the project root.
    main()