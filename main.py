# main.py
import os
from game_engine.game_state import GameState
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARACTERS_DATA_DIR = os.path.join(BASE_DIR, "data", "characters")

def main():
    print("--- Minimalist Mormon Trek Survival Test ---")
    print(f"Attempting to load characters from: {CHARACTERS_DATA_DIR}\n")

    # 1. Create GameState instance
    game_state = GameState()

    # 2. Tell GameState to load all characters
    #    The load_all_characters_from_files method now handles logging within GameState
    load_successful = game_state.load_all_characters_from_files(CHARACTERS_DATA_DIR)

    # Print logs from the loading process (which GameState populates)
    print("\n--- Loading Log ---")
    if game_state.log_messages:
        for msg in game_state.log_messages:
            print(msg)
    else:
        print("No log messages from GameState during loading.")
    print("--- End Loading Log ---\n")


    # 3. Check if loading was generally successful and characters were loaded
    if load_successful and game_state.initial_load_complete:
        print("Character loading and linking reported as successful by GameState.")
        
        all_characters = game_state.get_all_characters()
        player_character = game_state.get_player_character()

        if player_character:
            print(f"\nPlayer Character: {player_character.name} (ID: {player_character.id})")
        else:
            print("\nNo player character was identified.")

        if all_characters:
            print(f"\n--- All Loaded Characters ({len(all_characters)}) ---")
            for i, char_obj in enumerate(all_characters):
                print(f"{i+1}")
                print(f"   Name: {char_obj.name}")
                print(f"   Age: {char_obj.age}, Gender: {char_obj.gender}")
                # You can choose to print the short description or full bio here for testing
                print(f"   Short Desc: {char_obj.get_short_description()}")
                # print(f"   Bio:\n{char_obj.get_full_bio_display()}\n") # Uncomment for more detail
                
                # Test linked relationships (optional, but good)
                if char_obj.spouse_obj:
                    print(f"   Spouse: {char_obj.spouse_obj.name}")
                if char_obj.children_objs:
                    child_names = [child.name for child in char_obj.children_objs]
                    print(f"   Children: {', '.join(child_names)}")
                print("-" * 10) # Separator
        else:
            print("\nNo characters were loaded into GameState.")

    else:
        print("Character loading failed or was incomplete.")
        if game_state.loading_errors:
            print("\n--- Loading Errors ---")
            for error_msg in game_state.loading_errors:
                print(error_msg)
            print("--- End Loading Errors ---")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    main()