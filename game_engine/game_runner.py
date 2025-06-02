import os
from game_engine.game_state import GameState



class GameRunner:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        CHARACTERS_DATA_DIR = os.path.join(self.base_dir, "data", "characters")
        game_state = GameState()
        characters_initialized_successfully = game_state.initialize_characters(CHARACTERS_DATA_DIR)
        if not characters_initialized_successfully:
            print("GameState reports character initialization FAILED or encountered significant issues.")
            for message in game_state.log_messages:
                print(message)
        else:
            print(f"Loaded {len(game_state.characters)} characters")
        
