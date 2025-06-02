import os

class CLIHandler:
    def __init__(self, game_runner):
        self.game_runner = game_runner
        self.DIVIDER = "-" * 40 # Simple divider
        self.context = ["So it begins."]
        self.options = []
        self.prompt = "What is your name?"

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self):
        running = True
        while running:
            self.display_ui()
            command = input()
            self.context, self.options, self.prompt = self.game_runner.handle_input(command)
            

    def display_ui(self):
        """
        Displays the UI based on data provided by GameRunner.
        """
        self._clear_screen()
        print("--- Mormon Trek Survival ---\n") # Title

        # 1. Display Context
        if self.context:
            for msg in self.context:
                print(f"> {msg}")
            print(self.DIVIDER)

        # 2. Display Options (if any)
        if self.options:
            print("Options:")
            for i, option_data in enumerate(self.options):
                print(f"  {i+1}. {option_data}")
            print(self.DIVIDER)
        
        # 3. Display the Prompt String
        print(f"{self.prompt}")
