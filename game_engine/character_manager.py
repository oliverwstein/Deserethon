# game_engine/character_manager.py
import os
import glob
from .character import Character # Assuming character.py is in the same game_engine directory

class CharacterManager:
    def __init__(self):
        """
        Manages the loading, validation, and linking of a collection of Character objects.
        """
        self.characters: dict[str, Character] = {}
        self.player_character_id: str | None = None
        
        # These lists store messages specific to the loading process managed by this class.
        # GameState or another orchestrator can choose to retrieve and integrate these.
        self.loading_log: list[str] = []
        self.loading_errors: list[str] = []

    def _add_log_message(self, message: str):
        """Appends a message to the internal loading log."""
        self.loading_log.append(message)

    def _add_error_message(self, message: str):
        """Appends an error to the internal error list and also logs it."""
        self.loading_errors.append(message)
        self._add_log_message(f"ERROR: {message}") # Also log errors for chronological view

    def load_and_link_characters(self, characters_dir_path: str) -> bool:
        """
        Loads all character definitions from .yaml files in the specified directory,
        populates self.characters and self.player_character_id, and links relationships.

        Returns:
            bool: True if loading was successful (even with non-critical warnings), 
                  False if critical errors occurred (e.g., directory not found, no player).
                  The presence of messages in self.loading_errors indicates issues.
        """
        self.characters.clear()
        self.player_character_id = None
        self.loading_log.clear()
        self.loading_errors.clear()

        self._add_log_message(f"CharacterManager: Starting character load from directory: '{characters_dir_path}'")

        if not os.path.isdir(characters_dir_path):
            self._add_error_message(f"Characters directory not found: {characters_dir_path}")
            return False # Critical error

        yaml_files = glob.glob(os.path.join(characters_dir_path, "*.yaml"))
        yaml_files.extend(glob.glob(os.path.join(characters_dir_path, "*.yml")))

        if not yaml_files:
            self._add_log_message(f"WARN: No character YAML files found in {characters_dir_path}.")
            # This is not necessarily a failure of the loading process itself.
            # The game might be able to run without characters, or this might be an error
            # depending on game rules. For the manager, it just means no characters were loaded.
            return True # No files found, but process didn't fail.

        self._add_log_message(f"CharacterManager: Found {len(yaml_files)} potential character files.")
        
        loaded_character_objects: list[Character] = [] # Temp list before adding to dict, to handle duplicates first

        for file_path in yaml_files:
            try:
                # Character.load_from_yaml_file is a @classmethod
                char_obj = Character.load_from_yaml_file(file_path)
                loaded_character_objects.append(char_obj)
            except Exception as e:
                self._add_error_message(f"Failed to load or parse character file '{os.path.basename(file_path)}': {e}")
                # Continue to try loading other files

        # Process loaded objects: check for duplicates and assign player
        processed_ids = set()
        for char_obj in loaded_character_objects:
            if char_obj.id in processed_ids:
                self._add_error_message(f"Duplicate character ID '{char_obj.id}'. Original kept, duplicate ignored.")
                continue
            
            self.characters[char_obj.id] = char_obj
            processed_ids.add(char_obj.id)

            if char_obj.is_player:
                if self.player_character_id is not None:
                    self._add_error_message(
                        f"Multiple player characters defined! Old: {self.player_character_id}, "
                        f"New: {char_obj.id}. Using the latter: {char_obj.id}."
                    )
                self.player_character_id = char_obj.id
        
        self._add_log_message(f"CharacterManager: Successfully parsed and preliminarily processed {len(self.characters)} unique characters.")

        # Validate if a player character was set (if any characters were loaded)
        if self.characters and self.player_character_id is None:
            self._add_error_message("No player character (is_player: true) was designated among the loaded characters.")
            # This could be a critical error depending on game logic.
            # For now, CharacterManager flags it. GameState/GameRunner can decide if it's fatal.

        # Link relationships
        self._link_relationships_internal()

        if self.loading_errors:
            self._add_log_message(f"CharacterManager: Character loading and linking completed with {len(self.loading_errors)} issues.")
            # Even with errors, the process itself might be considered "complete" by the manager.
            # The calling code (GameState) will inspect loading_errors to decide overall success.
            return True # Process completed, but check errors.
        
        self._add_log_message("CharacterManager: All characters loaded and linked successfully.")
        return True

    def _link_relationships_internal(self):
        """
        Iterates through all loaded characters in self.characters and populates their
        direct object relationship attributes (spouse_obj, children_objs, etc.)
        based on the IDs stored in their relationships_data.
        """
        self._add_log_message("CharacterManager: Linking character relationships...")
        if not self.characters:
            self._add_log_message("  No characters to link (character dictionary is empty).")
            return

        for char_id, character in self.characters.items():
            # Link Spouse
            spouse_id = character.get_spouse_id() # Helper method from Character class
            if spouse_id:
                character.spouse_obj = self.characters.get(spouse_id)
                if not character.spouse_obj:
                    # Log as a warning because the file might be missing, or ID mistyped.
                    self._add_log_message(f"  WARN: For character '{char_id}', spouse ID '{spouse_id}' not found in loaded characters.")
                    # Optionally add to self.loading_errors if this should be a more prominent issue
                    # self.loading_errors.append(f"Linking Warning: Spouse ID '{spouse_id}' for '{char_id}' not found.")

            # Link Parents
            parent_ids = character.get_parent_ids()
            if parent_ids:
                character.parent_objs = [] # Initialize if not already (good practice)
                for p_id in parent_ids:
                    parent_obj = self.characters.get(p_id)
                    if parent_obj:
                        character.parent_objs.append(parent_obj)
                    else:
                        self._add_log_message(f"  WARN: For character '{char_id}', parent ID '{p_id}' not found.")
                        # self.loading_errors.append(f"Linking Warning: Parent ID '{p_id}' for '{char_id}' not found.")
            
            # Link Children
            children_ids = character.get_children_ids()
            if children_ids:
                character.children_objs = []
                for c_id in children_ids:
                    child_obj = self.characters.get(c_id)
                    if child_obj:
                        character.children_objs.append(child_obj)
                    else:
                        self._add_log_message(f"  WARN: For character '{char_id}', child ID '{c_id}' not found.")
                        # self.loading_errors.append(f"Linking Warning: Child ID '{c_id}' for '{char_id}' not found.")

            # Link Siblings
            sibling_ids = character.get_sibling_ids()
            if sibling_ids:
                character.sibling_objs = []
                for s_id in sibling_ids:
                    sibling_obj = self.characters.get(s_id)
                    if sibling_obj:
                        character.sibling_objs.append(sibling_obj)
                    else:
                        self._add_log_message(f"  WARN: For character '{char_id}', sibling ID '{s_id}' not found.")
                        # self.loading_errors.append(f"Linking Warning: Sibling ID '{s_id}' for '{char_id}' not found.")

        self._add_log_message("CharacterManager: Character relationship linking attempt complete.")