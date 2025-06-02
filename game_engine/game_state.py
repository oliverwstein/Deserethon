# game_engine/game_state.py
# os and glob are no longer needed here for character loading
from .character import Character # Still needed for type hints and direct use
from .character_manager import CharacterManager # Import the new manager

class GameState:
    def __init__(self):
        # --- Core Game Data ---
        # These will be populated by the initialize_characters method
        self.characters: dict[str, Character] = {}
        self.player_character_id: str | None = None

        # --- UI/Interaction State (to be managed by GameRunner/Logic) ---
        self.log_messages: list[str] = [] # Game-wide log for UI

        # --- Overall Loading Status for GameState ---
        # This reflects the status of all data loading, not just characters
        self.initial_load_complete: bool = False # General flag for all critical data
        self.loading_errors: list[str] = [] # Aggregated errors from all loading processes

    def add_log(self, message: str):
        """Adds a message to the game-wide log."""
        self.log_messages.append(message)

    def clear_log(self):
        """Clears all messages from the game-wide log."""
        self.log_messages.clear()

    def initialize_characters(self, characters_dir_path: str) -> bool:
        """
        Initializes character data by using the CharacterManager.
        Populates self.characters and self.player_character_id.
        Aggregates logs and errors from the CharacterManager.

        Returns:
            bool: True if character initialization was considered successful 
                  (e.g., no critical errors from CharacterManager), False otherwise.
        """
        
        char_manager = CharacterManager()
        manager_process_completed = char_manager.load_and_link_characters(characters_dir_path)

        # Integrate logs and errors from the CharacterManager into GameState's records
        # Prefixing helps identify the source of the log/error.
        if manager_process_completed:
            self.characters = char_manager.characters
            self.player_character_id = char_manager.player_character_id
            
            # Now, GameState decides if the outcome from CharacterManager constitutes a "successful load"
            # For example, if there are any errors from CharacterManager, or if no player was found.
            if char_manager.loading_errors: # If CharacterManager reported any issues
                self.add_log("GameState: Character initialization completed with issues (see errors).")
                # Depending on severity, we might still proceed or mark as incomplete.
                # For now, let's say any error from CharManager makes character load less than perfect.
                # self.initial_load_complete = False; # Keep this for overall GameState readiness
                return False # Indicate that while manager ran, there were problems.
            
            if not self.characters: # No characters were loaded
                 self.add_log("GameState: Character initialization complete, but no characters were loaded (directory might be empty or all files failed).")
                 # This might be okay or an error depending on game design.
                 # Let's assume for now if the directory was valid and processed, it's not a GameState init failure itself.

            if self.characters and not self.player_character_id:
                self.add_log("GameState: CRITICAL - Characters loaded, but no player character designated.")
                self.loading_errors.append("GameState: No player character designated after character load.")
                return False # This is likely a fatal issue for starting the game.

            # If we reach here, character loading is considered good from GameState's perspective.
            # The overall self.initial_load_complete will be set after all data types are loaded.
            return True
        else:
            # manager_process_completed was False, meaning a critical failure within CharacterManager
            # (e.g., directory not found). Errors should already be in self.loading_errors.
            self.add_log("GameState: Critical failure during character manager execution.")
            return False

    def get_character(self, char_id: str) -> Character | None:
        """Retrieves a character by their ID from the loaded characters."""
        return self.characters.get(char_id)

    def get_all_characters(self) -> list[Character]:
        """Returns a list of all loaded character objects."""
        return list(self.characters.values())

    def get_player_character(self) -> Character | None:
        """Returns the player Character object, or None if not set or found."""
        if self.player_character_id:
            return self.get_character(self.player_character_id)
        return None