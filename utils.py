import time
import platform
import sys
import os
import datetime
import pickle
from typing import Dict, List, Tuple, Any

from config import DIVIDER, SAVE_DIR, VERSION

def clear_screen():
    """Clear the console screen based on operating system."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def print_slow(text: str, delay: float = 0.03):
    """Print text character by character with a delay."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

def print_centered(text: str, width: int = 70):
    """Print text centered within a specified width."""
    print(text.center(width))

def input_with_timeout(prompt: str, timeout: float = 3.0) -> str:
    """Custom input function with timeout for quick-time events."""
    print(prompt, end="", flush=True)
    start_time = time.time()
    user_input = ""
    
    while time.time() - start_time < timeout:
        if sys.stdin.isatty():  # Check if input is coming from a terminal
            if platform.system() == "Windows":
                import msvcrt
            else:
                import select
            
            if platform.system() == "Windows":
                if msvcrt.kbhit():
                    char = msvcrt.getch().decode("utf-8")
                    if char == "\r":  # Enter key
                        break
                    user_input += char
                    print(char, end="", flush=True)
            else:
                if select.select([sys.stdin], [], [], 0)[0]:
                    char = sys.stdin.read(1)
                    if char == "\n":  # Enter key
                        break
                    user_input += char
                    print(char, end="", flush=True)
        else:
            # Fallback for environments without terminal input
            return input(prompt)
            
        time.sleep(0.1)
    
    print()  # Newline after input
    return user_input

def display_bar(current: int, maximum: int, width: int = 10, char: str = "█") -> str:
    """Create a visual bar representing a value."""
    filled = int(current / maximum * width)
    return f"[{char * filled}{('░' * (width - filled))}] {current}/{maximum}"

def display_countdown(seconds: int, message: str = "Time remaining: "):
    """Display a countdown timer for timed events."""
    for i in range(seconds, 0, -1):
        print(f"\r{message}{i}s", end="", flush=True)
        time.sleep(1)
    print()

def save_game(player, world, filename: str = None):
    """Save the game state to a file."""
    if filename is None:
        # Generate a filename based on current time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(SAVE_DIR, f"save_{timestamp}.sav")
    
    save_data = {
        "version": VERSION,
        "player": player.to_dict(),
        "world": world.to_dict(),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(filename, "wb") as f:
        pickle.dump(save_data, f)
    
    return filename

def load_game(filename: str) -> Tuple[Any, Any]:
    """Load a saved game from a file."""
    with open(filename, "rb") as f:
        save_data = pickle.load(f)
    
    # Check version compatibility
    if save_data["version"] != VERSION:
        print("Warning: Save file version mismatch. Some features may not work correctly.")
    
    # These will be imported at runtime to avoid circular imports
    from models_part2 import Player
    from models_part3 import World
    
    player = Player.from_dict(save_data["player"])
    world = World.from_dict(save_data["world"])
    
    return player, world

def list_saves() -> List[str]:
    """List all available save files."""
    saves = []
    for file in os.listdir(SAVE_DIR):
        if file.endswith(".sav"):
            saves.append(os.path.join(SAVE_DIR, file))
    return saves

def get_save_info(filename: str) -> Dict:
    """Get information about a save file."""
    try:
        with open(filename, "rb") as f:
            save_data = pickle.load(f)
        
        player_data = save_data.get("player", {})
        
        return {
            "player_name": player_data.get("name", "Unknown"),
            "player_level": player_data.get("level", 1),
            "location": player_data.get("current_location", "Unknown"),
            "timestamp": save_data.get("timestamp", "Unknown date"),
            "version": save_data.get("version", "Unknown version")
        }
    except Exception as e:
        return {
            "error": str(e),
            "filename": filename
        } 