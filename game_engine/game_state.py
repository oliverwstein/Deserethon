# game_engine/game_state.py
import os
import glob # For finding all character YAML files
from .character import Character # Assuming character.py is in the same directory

class GameState:
    def __init__(self):
        # --- Core Game Data ---
        self.characters: dict[str, Character] = {} # Stores Character objects, keyed by char_id
        self.player_character_id: str | None = None

        # --- UI/Interaction State (to be managed by GameLogic) ---
        self.log_messages: list[str] = []
        self.current_prompt: dict = { # Info for the UI about what input is expected
            "type": "message", # e.g., message, main_command, choice, text_input
            "text": "Initializing...",
            "options": []
        }
        self.is_game_over: bool = False
        self.game_over_message: str = ""

        # --- Loading Status ---
        self.initial_load_complete: bool = False
        self.loading_errors: list[str] = []


    def add_log(self, message: str):
        """Adds a message to the game log."""
        self.log_messages.append(message)
        # Optional: limit log size if it grows too large
        # self.log_messages = self.log_messages[-20:]

    def clear_log(self):
        """Clears all messages from the game log."""
        self.log_messages.clear()

    def load_all_characters_from_files(self, characters_dir_path: str) -> bool:
        """
        Loads all character definitions from .yaml files in the specified directory.
        Populates self.characters and self.player_character_id.
        Returns True if successful, False otherwise (and populates self.loading_errors).
        """
        self.clear_log() # Clear previous logs before loading
        self.characters.clear()
        self.loading_errors.clear()
        self.player_character_id = None
        self.initial_load_complete = False

        self.add_log(f"Starting character load from: {characters_dir_path}")

        if not os.path.isdir(characters_dir_path):
            error_msg = f"ERROR: Characters directory not found: {characters_dir_path}"
            self.add_log(error_msg)
            self.loading_errors.append(error_msg)
            return False

        # Find all .yaml or .yml files in the directory
        yaml_files = glob.glob(os.path.join(characters_dir_path, "*.yaml"))
        yaml_files.extend(glob.glob(os.path.join(characters_dir_path, "*.yml")))

        if not yaml_files:
            error_msg = f"WARN: No character YAML files found in {characters_dir_path}."
            self.add_log(error_msg)
            # Potentially not a fatal error, could be an empty game or different setup
            # For now, let's treat it as non-fatal but mark load as not fully complete if desired
            # Or, if characters are essential, return False here
            # self.loading_errors.append(error_msg) # If considered an error
            # return False


        loaded_chars_count = 0
        for file_path in yaml_files:
            try:
                self.add_log(f"  Loading character from: {os.path.basename(file_path)}")
                char_obj = Character.load_from_yaml_file(file_path)
                
                if char_obj.id in self.characters:
                    error_msg = (f"ERROR: Duplicate character ID '{char_obj.id}' "
                                 f"found in {os.path.basename(file_path)}. Skipping.")
                    self.add_log(error_msg)
                    self.loading_errors.append(error_msg)
                    continue

                self.characters[char_obj.id] = char_obj
                if char_obj.is_player:
                    if self.player_character_id is not None:
                        error_msg = (f"ERROR: Multiple player characters defined! "
                                     f"Old: {self.player_character_id}, New: {char_obj.id}. Using last one.")
                        self.add_log(error_msg)
                        self.loading_errors.append(error_msg) # Log as warning/error
                    self.player_character_id = char_obj.id
                loaded_chars_count += 1
            except Exception as e: # Catch errors from Character.load_from_yaml_file or others
                error_msg = f"ERROR: Failed to load character from {os.path.basename(file_path)}: {e}"
                self.add_log(error_msg)
                self.loading_errors.append(error_msg)
        
        if self.player_character_id is None and self.characters:
            # Only an error if characters were loaded but no player
            error_msg = "ERROR: No player character (is_player: true) defined among loaded characters."
            self.add_log(error_msg)
            self.loading_errors.append(error_msg)

        if not self.loading_errors:
            self.add_log(f"Successfully loaded {loaded_chars_count} characters.")
            # Now, link relationships
            self._link_character_relationships()
            self.initial_load_complete = True # Mark loading as complete if no critical errors
            return True
        else:
            self.add_log(f"Character loading finished with {len(self.loading_errors)} errors/warnings.")
            # Decide if any error makes the load incomplete. For now, any error makes it so.
            # We might refine this to distinguish warnings from fatal errors.
            return False


    def _link_character_relationships(self):
        """
        Iterates through all loaded characters and populates their
        direct object relationship attributes (spouse_obj, children_objs, etc.)
        based on the IDs stored in their relationships_data.
        This should be called only AFTER all characters are loaded into self.characters.
        """
        self.add_log("Linking character relationships...")
        if not self.characters:
            self.add_log("  No characters to link.")
            return

        for char_id, character in self.characters.items():
            # Link Spouse
            spouse_id = character.get_spouse_id() # Helper method from Character class
            if spouse_id:
                character.spouse_obj = self.get_character(spouse_id)
                if not character.spouse_obj:
                    self.add_log(f"  WARN: Spouse ID '{spouse_id}' for character '{char_id}' not found.")
                    self.loading_errors.append(f"Linking Warn: Spouse ID '{spouse_id}' for '{char_id}' not found.")


            # Link Parents
            parent_ids = character.get_parent_ids()
            if parent_ids:
                character.parent_objs = []
                for p_id in parent_ids:
                    parent_obj = self.get_character(p_id)
                    if parent_obj:
                        character.parent_objs.append(parent_obj)
                    else:
                        self.add_log(f"  WARN: Parent ID '{p_id}' for character '{char_id}' not found.")
                        self.loading_errors.append(f"Linking Warn: Parent ID '{p_id}' for '{char_id}' not found.")


            # Link Children
            children_ids = character.get_children_ids()
            if children_ids:
                character.children_objs = []
                for c_id in children_ids:
                    child_obj = self.get_character(c_id)
                    if child_obj:
                        character.children_objs.append(child_obj)
                    else:
                        self.add_log(f"  WARN: Child ID '{c_id}' for character '{char_id}' not found.")
                        self.loading_errors.append(f"Linking Warn: Child ID '{c_id}' for '{char_id}' not found.")


            # Link Siblings
            sibling_ids = character.get_sibling_ids()
            if sibling_ids:
                character.sibling_objs = []
                for s_id in sibling_ids:
                    sibling_obj = self.get_character(s_id)
                    if sibling_obj:
                        character.sibling_objs.append(sibling_obj)
                    else:
                        self.add_log(f"  WARN: Sibling ID '{s_id}' for character '{char_id}' not found.")
                        self.loading_errors.append(f"Linking Warn: Sibling ID '{s_id}' for '{char_id}' not found.")

        self.add_log("Character relationship linking complete.")


    def get_character(self, char_id: str) -> Character | None:
        """Retrieves a character by their ID."""
        return self.characters.get(char_id)

    def get_all_characters(self) -> list[Character]:
        """Returns a list of all character objects."""
        return list(self.characters.values())

    def get_player_character(self) -> Character | None:
        """Returns the player Character object, or None if not set."""
        if self.player_character_id:
            return self.get_character(self.player_character_id)
        return None