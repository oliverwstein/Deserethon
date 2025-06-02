# enhanced_cli_runner.py
from prompt_toolkit import prompt
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.application import get_app
import asyncio
from typing import List, Tuple, Optional

class ConversationMessage:
    """Represents a single message in the conversation history."""
    def __init__(self, content: str, message_type: str = "system"):
        self.content = content
        self.type = message_type  # "system", "user", "prompt", "options"

class CLIRunner:
    def __init__(self, game_runner):
        self.game_runner = game_runner
        self.conversation_history: List[ConversationMessage] = []
        self.current_context = []
        self.current_options = []
        self.current_prompt = "Enter command:"
        self.available_commands = []
        self.app: Optional[Application] = None
        
        # Initialize with game title
        self.conversation_history.append(
            ConversationMessage("--- Mormon Trek Survival ---", "title")
        )
        
        # Get initial game state
        self._update_game_state()

    def _update_game_state(self):
        """Get current state from game runner."""
        # For now, we'll simulate the API calls since game_runner needs updating
        # In real implementation, these would be:
        # self.current_context, self.current_options, self.current_prompt = self.game_runner.get_current_display()
        # self.available_commands = self.game_runner.get_available_commands()
        
        # Simulated initial state
        self.current_context = ["Welcome to Mormon Trek Survival!", "Your journey begins..."]
        self.current_options = ["1. Start new game", "2. Load saved game", "3. View credits"]
        self.current_prompt = "Choose an option:"
        self.available_commands = ["help", "quit", "save", "status", "inventory"]

    def _add_to_history(self, content: str, message_type: str = "system"):
        """Add a message to conversation history."""
        self.conversation_history.append(ConversationMessage(content, message_type))

    def _format_history(self) -> FormattedText:
        """Format conversation history for display."""
        formatted_lines = []
        
        for msg in self.conversation_history:
            if msg.type == "title":
                formatted_lines.append(("class:title", f"{msg.content}\n\n"))
            elif msg.type == "system":
                formatted_lines.append(("class:system", f"> {msg.content}\n"))
            elif msg.type == "user":
                formatted_lines.append(("class:user", f"< {msg.content}\n"))
            elif msg.type == "options":
                formatted_lines.append(("class:options", f"{msg.content}\n"))
            elif msg.type == "prompt":
                formatted_lines.append(("class:prompt", f"\n{msg.content}\n"))
        
        return FormattedText(formatted_lines)

    def _show_current_state(self):
        """Display current game state in conversation."""
        # Add context messages
        for context_msg in self.current_context:
            self._add_to_history(context_msg, "system")
        
        # Add options if available
        if self.current_options:
            options_text = "Options:\n" + "\n".join(f"  {option}" for option in self.current_options)
            self._add_to_history(options_text, "options")
        
        # Add current prompt
        self._add_to_history(self.current_prompt, "prompt")

    def _handle_command(self, command: str) -> bool:
        """Handle slash commands. Returns True if app should continue."""
        command = command.lower().strip()
        
        if command == "quit":
            return False
        elif command == "help":
            help_text = "Available commands: " + ", ".join(self.available_commands)
            self._add_to_history(help_text, "system")
        elif command == "clear":
            self.conversation_history.clear()
            self.conversation_history.append(
                ConversationMessage("--- Mormon Trek Survival ---", "title")
            )
            self._show_current_state()
        elif command == "status":
            # This would call game_runner.get_status() or similar
            self._add_to_history("Status: Healthy, Day 1, 2000 pounds supplies", "system")
        elif command == "inventory":
            # This would call game_runner.get_inventory() or similar
            self._add_to_history("Inventory: Rifle, 200 rounds, 50 pounds food", "system")
        else:
            self._add_to_history(f"Unknown command: {command}", "system")
        
        return True

    def _handle_user_input(self, user_input: str):
        """Process user input and update game state."""
        # Add user input to history
        self._add_to_history(user_input, "user")
        
        # Send to game runner (simulated for now)
        # In real implementation: 
        # self.current_context, self.current_options, self.current_prompt = self.game_runner.handle_input(user_input)
        
        # Simulated response
        if user_input == "1":
            self.current_context = ["You have chosen to start a new game.", "Creating your character..."]
            self.current_options = []
            self.current_prompt = "What is your name?"
        elif user_input.lower() in ["help", "?"]:
            self.current_context = [f"Available commands: {', '.join(self.available_commands)}"]
            self.current_options = self.current_options  # Keep current options
            self.current_prompt = self.current_prompt    # Keep current prompt
        else:
            self.current_context = [f"You entered: {user_input}"]
            self.current_options = ["1. Continue", "2. Go back"]
            self.current_prompt = "What would you like to do?"
        
        # Show updated state
        self._show_current_state()

    def create_application(self) -> Application:
        """Create the prompt_toolkit application."""
        
        # Create text area for history display
        history_display = Window(
            content=FormattedTextControl(
                text=self._format_history,
                focusable=False,
            ),
            scrollable=True,
        )
        
        # Create input area
        input_field = TextArea(
            prompt="> ",
            multiline=False,
            scrollbar=False,
            focusable=True,
        )
        
        # Key bindings
        kb = KeyBindings()
        
        @kb.add('c-c')
        def _(event):
            """Ctrl+C to quit."""
            event.app.exit()
        
        @kb.add('enter')
        def _(event):
            """Handle enter key."""
            text = input_field.text.strip()
            input_field.text = ""
            
            if not text:
                return
            
            # Check if it's a command (starts with /)
            if text.startswith('/'):
                command = text[1:]  # Remove the /
                should_continue = self._handle_command(command)
                if not should_continue:
                    event.app.exit()
                    return
            else:
                # Regular input
                self._handle_user_input(text)
            
            # Refresh the display
            event.app.invalidate()
        
        # Create layout
        root_container = HSplit([
            history_display,
            Window(height=1, char='-', style='class:line'),  # Separator line
            input_field,
        ])
        
        # Define style
        style = Style.from_dict({
            'title': '#00aa00 bold',
            'system': '#ffffff',
            'user': '#0088ff',
            'options': '#ffaa00',
            'prompt': '#00aa00 bold',
            'line': '#444444',
        })
        
        # Create application
        app = Application(
            layout=Layout(root_container),
            key_bindings=kb,
            style=style,
            mouse_support=True,
            full_screen=True,
        )
        
        return app

    def run(self):
        """Run the enhanced CLI interface."""
        # Show initial state
        self._show_current_state()
        
        # Create and run application
        self.app = self.create_application()
        
        print("Mormon Trek Survival - Enhanced Interface")
        print("Type /help for commands, /quit to exit")
        print("Press Ctrl+C to force quit\n")
        
        try:
            self.app.run()
        except KeyboardInterrupt:
            print("\nGame interrupted. Goodbye!")
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            print("Thanks for playing!")