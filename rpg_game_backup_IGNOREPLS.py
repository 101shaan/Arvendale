import os
import json
import time
import random
import pickle
import datetime
import platform
import sys
from typing import Dict, List, Optional, Tuple, Union, Any

# Constants
SAVE_DIR = "saves"
AUTOSAVE_FILE = os.path.join(SAVE_DIR, "autosave.sav")
VERSION = "1.0.0"

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# ASCII Art and UI Elements
TITLE_ART = """
  ╔═══════════════════════════════════════════════════════════╗
  ║  ▄████▄   ██▀███   █    ██  ███▄ ▄███▓ ▄▄▄▄    ██▓    ██▓ ║
  ║ ▒██▀ ▀█  ▓██ ▒ ██▒ ██  ▓██▒▓██▒▀█▀ ██▒▓█████▄ ▓██▒   ▓██▒ ║
  ║ ▒▓█    ▄ ▓██ ░▄█ ▒▓██  ▒██░▓██    ▓██░▒██▒ ▄██▒██░   ▒██░ ║
  ║ ▒▓▓▄ ▄██▒▒██▀▀█▄  ▓▓█  ░██░▒██    ▒██ ▒██░█▀  ▒██░   ▒██░ ║
  ║ ▒ ▓███▀ ░░██▓ ▒██▒▒▒█████▓ ▒██▒   ░██▒░▓█  ▀█▓░██████░██████╗
  ║ ░ ░▒ ▒  ░░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ░ ▒░   ░  ░░▒▓███▀▒░ ▒░▓  ░ ▒░▓  ║
  ║   ░  ▒     ░▒ ░ ▒░░░▒░ ░ ░ ░  ░      ░▒░▒   ░ ░ ░ ▒  ░ ░ ▒  ║
  ║ ░          ░░   ░  ░░░ ░ ░ ░      ░    ░    ░   ░ ░    ░ ░  ║
  ║ ░ ░         ░        ░            ░    ░          ░  ░   ░  ║
  ║                           ARDENVALE                        ║
  ╚═══════════════════════════════════════════════════════════╝
                A REALM SHATTERED BY A FADING FLAME
"""

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                      ARDENVALE                            ║
╚═══════════════════════════════════════════════════════════╝
"""

DIVIDER = "═" * 70

# Utility Functions
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
        
        return {
            "player_name": save_data["player"]["name"],
            "player_level": save_data["player"]["level"],
            "location": save_data["player"]["current_location"],
            "timestamp": save_data["timestamp"],
            "version": save_data["version"]
        }
    except Exception as e:
        return {
            "error": str(e),
            "filename": filename
        }

# Game Classes
class Item:
    def __init__(self, id: str, name: str, description: str, item_type: str, value: int = 0, 
                 weight: float = 0.0, stats: Dict = None, usable: bool = False, 
                 equippable: bool = False, quantity: int = 1):
        self.id = id
        self.name = name
        self.description = description
        self.item_type = item_type  # weapon, armor, consumable, key, etc.
        self.value = value
        self.weight = weight
        self.stats = stats or {}
        self.usable = usable
        self.equippable = equippable
        self.quantity = quantity
        self.equipped = False
    
    def use(self, player) -> str:
        """Use the item and return result message."""
        if not self.usable:
            return f"You cannot use the {self.name}."
        
        # Implement item usage logic here
        result = "You used the item, but nothing happened."
        
        # Example: Healing potion
        if self.item_type == "consumable" and "healing" in self.stats:
            heal_amount = self.stats["healing"]
            player.heal(heal_amount)
            result = f"You drink the {self.name} and recover {heal_amount} health."
            self.quantity -= 1
            
        return result
    
    def to_dict(self) -> Dict:
        """Convert item to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "value": self.value,
            "weight": self.weight,
            "stats": self.stats,
            "usable": self.usable,
            "equippable": self.equippable,
            "quantity": self.quantity,
            "equipped": self.equipped
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Create an item from dictionary data."""
        item = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=data["item_type"],
            value=data["value"],
            weight=data["weight"],
            stats=data["stats"],
            usable=data["usable"],
            equippable=data["equippable"],
            quantity=data["quantity"]
        )
        item.equipped = data["equipped"]
        return item

class Weapon(Item):
    def __init__(self, id: str, name: str, description: str, damage: int, 
                 damage_type: str, weight: float, value: int, 
                 special_ability: Dict = None, two_handed: bool = False):
        stats = {
            "damage": damage,
            "damage_type": damage_type,
            "two_handed": two_handed
        }
        if special_ability:
            stats["special_ability"] = special_ability
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="weapon",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )
    
    def get_damage(self) -> int:
        """Calculate the weapon's damage."""
        base_damage = self.stats["damage"]
        return base_damage
    
    def weapon_art(self, player, target) -> str:
        """Use the weapon's special ability."""
        if "special_ability" not in self.stats:
            return "This weapon has no special ability."
        
        ability = self.stats["special_ability"]
        # Implement weapon special ability logic
        
        return f"You use {ability['name']}!"

class Armor(Item):
    def __init__(self, id: str, name: str, description: str, defense: int, 
                 armor_type: str, weight: float, value: int, 
                 resistance: Dict = None):
        stats = {
            "defense": defense,
            "armor_type": armor_type,
        }
        if resistance:
            stats["resistance"] = resistance
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="armor",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )

class Consumable(Item):
    def __init__(self, id: str, name: str, description: str, effect: Dict, 
                 value: int, weight: float = 0.1, quantity: int = 1):
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="consumable",
            value=value,
            weight=weight,
            stats=effect,
            usable=True,
            equippable=False,
            quantity=quantity
        )

class Enemy:
    def __init__(self, id: str, name: str, description: str, level: int, 
                 hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.attack_patterns = attack_patterns or []
        self.loot_table = loot_table or []
        self.essence = essence
        self.weaknesses = weaknesses or []
        self.current_pattern_index = 0
    
    def get_next_attack(self) -> Dict:
        """Get the next attack pattern in sequence."""
        if not self.attack_patterns:
            return {"name": "Basic Attack", "damage": self.attack, "type": "physical"}
        
        pattern = self.attack_patterns[self.current_pattern_index]
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.attack_patterns)
        return pattern
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        # Apply weakness multipliers
        multiplier = 1.0
        if damage_type in self.weaknesses:
            multiplier = 1.5
            
        damage = int(max(1, amount * multiplier - self.defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the enemy is dead."""
        return self.hp <= 0
    
    def drop_loot(self) -> List[Item]:
        """Generate loot drops based on loot table."""
        drops = []
        for loot_entry in self.loot_table:
            if random.random() < loot_entry["chance"]:
                # Create the item from the item database
                item_id = loot_entry["item_id"]
                item = create_item(item_id)
                if item:
                    # Set quantity if specified
                    if "quantity" in loot_entry:
                        item.quantity = random.randint(
                            loot_entry["quantity"]["min"], 
                            loot_entry["quantity"]["max"]
                        )
                    drops.append(item)
        return drops
    
    def to_dict(self) -> Dict:
        """Convert enemy to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "attack_patterns": self.attack_patterns,
            "loot_table": self.loot_table,
            "essence": self.essence,
            "weaknesses": self.weaknesses,
            "current_pattern_index": self.current_pattern_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Enemy':
        """Create an enemy from dictionary data."""
        enemy = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            level=data["level"],
            hp=data["max_hp"],
            attack=data["attack"],
            defense=data["defense"],
            attack_patterns=data["attack_patterns"],
            loot_table=data["loot_table"],
            essence=data["essence"],
            weaknesses=data["weaknesses"]
        )
        enemy.hp = data["hp"]
        enemy.current_pattern_index = data["current_pattern_index"]
        return enemy

class Boss(Enemy):
    def __init__(self, id: str, name: str, title: str, description: str, 
                 level: int, hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None,
                 phases: List[Dict] = None):
        super().__init__(
            id=id,
            name=f"{name}, {title}",
            description=description,
            level=level,
            hp=hp,
            attack=attack,
            defense=defense,
            attack_patterns=attack_patterns,
            loot_table=loot_table,
            essence=essence,
            weaknesses=weaknesses
        )
        self.phases = phases or []
        self.current_phase = 0
        self.phase_triggers = [phase["trigger"] for phase in self.phases] if phases else []
    
    def update_phase(self) -> bool:
        """Check and update boss phase based on HP. Return True if phase changed."""
        if not self.phases:
            return False
            
        # Check if we should transition to the next phase
        hp_percentage = self.hp / self.max_hp * 100
        
        for i, trigger in enumerate(self.phase_triggers):
            if hp_percentage <= trigger and i > self.current_phase:
                self.current_phase = i
                # Apply phase changes
                phase = self.phases[i]
                if "attack_patterns" in phase:
                    self.attack_patterns = phase["attack_patterns"]
                    self.current_pattern_index = 0
                if "attack_boost" in phase:
                    self.attack += phase["attack_boost"]
                if "defense_boost" in phase:
                    self.defense += phase["defense_boost"]
                if "message" in phase:
                    print_slow(phase["message"])
                    
                return True
                
        return False

class Location:
    def __init__(self, id: str, name: str, description: str, 
                 connections: Dict[str, str] = None,
                 enemies: List[str] = None,
                 items: List[str] = None,
                 npcs: List[str] = None,
                 is_beacon: bool = False,
                 map_art: str = None,
                 first_visit_text: str = None,
                 events: Dict = None):
        self.id = id
        self.name = name
        self.description = description
        self.connections = connections or {}  # Direction: location_id
        self.enemies = enemies or []  # List of enemy ids that can spawn here
        self.items = items or []  # List of item ids that can be found here
        self.npcs = npcs or []  # List of NPC ids that can be found here
        self.is_beacon = is_beacon
        self.map_art = map_art
        self.first_visit_text = first_visit_text
        self.events = events or {}  # Event triggers
        self.visited = False
    
    def get_description(self) -> str:
        """Get the location description."""
        return self.description
    
    def get_connections_string(self) -> str:
        """Get a string describing available exits."""
        if not self.connections:
            return "There are no obvious exits."
            
        exits = []
        for direction, _ in self.connections.items():
            exits.append(direction)
        
        return f"Exits: {', '.join(exits)}"
    
    def to_dict(self) -> Dict:
        """Convert location to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connections": self.connections,
            "enemies": self.enemies,
            "items": self.items,
            "npcs": self.npcs,
            "is_beacon": self.is_beacon,
            "map_art": self.map_art,
            "first_visit_text": self.first_visit_text,
            "events": self.events,
            "visited": self.visited
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        """Create a location from dictionary data."""
        location = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            connections=data["connections"],
            enemies=data["enemies"],
            items=data["items"],
            npcs=data["npcs"],
            is_beacon=data["is_beacon"],
            map_art=data["map_art"],
            first_visit_text=data["first_visit_text"],
            events=data["events"]
        )
        location.visited = data["visited"]
        return location

class NPC:
    def __init__(self, id: str, name: str, description: str, 
                 dialogue: Dict[str, Dict] = None,
                 quest: Dict = None,
                 shop_inventory: List[str] = None,
                 faction: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.dialogue = dialogue or {"default": {"text": "...", "options": {}}}
        self.current_dialogue = "default"
        self.quest = quest
        self.shop_inventory = shop_inventory or []
        self.faction = faction
        self.met = False
        self.relationship = 0  # -100 to 100
    
    def get_dialogue(self) -> Dict:
        """Get the current dialogue options."""
        return self.dialogue.get(self.current_dialogue, self.dialogue["default"])
    
    def talk(self) -> str:
        """Start a conversation with the NPC."""
        if not self.met:
            self.met = True
            return f"You meet {self.name} for the first time.\n{self.description}"
        
        return f"{self.name}: {self.get_dialogue()['text']}"
    
    def respond(self, option: str) -> str:
        """Respond to a dialogue option."""
        dialogue = self.get_dialogue()
        
        if option in dialogue["options"]:
            response = dialogue["options"][option]
            
            # Update dialogue state if needed
            if "next" in response:
                self.current_dialogue = response["next"]
            
            # Handle quest progression
            if "quest_progress" in response and self.quest:
                # Implement quest progression logic
                pass
            
            # Handle relationship changes
            if "relationship" in response:
                self.relationship += response["relationship"]
                
            return response["text"]
        
        return "Invalid response."
    
    def to_dict(self) -> Dict:
        """Convert NPC to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dialogue": self.dialogue,
            "current_dialogue": self.current_dialogue,
            "quest": self.quest,
            "shop_inventory": self.shop_inventory,
            "faction": self.faction,
            "met": self.met,
            "relationship": self.relationship
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        """Create an NPC from dictionary data."""
        npc = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            dialogue=data["dialogue"],
            quest=data["quest"],
            shop_inventory=data["shop_inventory"],
            faction=data["faction"]
        )
        npc.current_dialogue = data["current_dialogue"]
        npc.met = data["met"]
        npc.relationship = data["relationship"]
        return npc

class Player:
    def __init__(self, name: str, character_class: str, level: int = 1):
        self.name = name
        self.character_class = character_class
        self.level = level
        self.essence = 0  # Currency
        self.lost_essence = 0  # Lost on death
        self.lost_essence_location = None
        
        # Initialize stats based on class
        if character_class == "Warrior":
            self.max_hp = 100
            self.max_stamina = 80
            self.strength = 14
            self.dexterity = 9
            self.intelligence = 7
            self.faith = 8
            self.vitality = 12
            self.endurance = 10
        elif character_class == "Knight":
            self.max_hp = 90
            self.max_stamina = 90
            self.strength = 12
            self.dexterity = 12
            self.intelligence = 9
            self.faith = 11
            self.vitality = 10
            self.endurance = 11
        elif character_class == "Pyromancer":
            self.max_hp = 80
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 12
            self.faith = 14
            self.vitality = 8
            self.endurance = 9
        elif character_class == "Thief":
            self.max_hp = 75
            self.max_stamina = 100
            self.strength = 9
            self.dexterity = 14
            self.intelligence = 10
            self.faith = 8
            self.vitality = 9
            self.endurance = 14
        else:  # Default
            self.max_hp = 85
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 10
            self.faith = 10
            self.vitality = 10
            self.endurance = 10
        
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.inventory = []
        self.equipment = {
            "weapon": None,
            "shield": None,
            "armor": None,
            "ring1": None,
            "ring2": None,
            "amulet": None
        }
        self.estus_flask = {
            "current": 3,
            "max": 3
        }
        self.current_location = "highcastle_entrance"
        self.quests = {}
        self.discovered_locations = set()
        self.killed_enemies = {}
        self.stance = "balanced"  # balanced, aggressive, defensive
    
    def heal(self, amount: int) -> int:
        """Heal the player and return amount healed."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def restore_stamina(self, amount: int) -> int:
        """Restore stamina and return amount restored."""
        old_stamina = self.stamina
        self.stamina = min(self.max_stamina, self.stamina + amount)
        return self.stamina - old_stamina
    
    def use_estus(self) -> bool:
        """Use an estus flask charge to heal."""
        if self.estus_flask["current"] <= 0:
            return False
        
        self.estus_flask["current"] -= 1
        heal_amount = int(self.max_hp * 0.4)  # Heal 40% of max HP
        self.heal(heal_amount)
        return True
    
    def rest_at_beacon(self):
        """Rest at a beacon to restore HP, stamina, and estus."""
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.estus_flask["current"] = self.estus_flask["max"]
    
    def add_item(self, item: Item) -> bool:
        """Add an item to inventory. Return True if successful."""
        # Check if the item is stackable and exists in inventory
        if item.quantity > 1:
            for inv_item in self.inventory:
                if inv_item.id == item.id:
                    inv_item.quantity += item.quantity
                    return True
                    
        self.inventory.append(item)
        return True
    
    def remove_item(self, item: Item) -> bool:
        """Remove an item from inventory. Return True if successful."""
        for i, inv_item in enumerate(self.inventory):
            if inv_item.id == item.id:
                if inv_item.quantity > 1:
                    inv_item.quantity -= 1
                    return True
                else:
                    self.inventory.pop(i)
                    return True
        return False
    
    def equip_item(self, item: Item) -> str:
        """Equip an item. Return result message."""
        if not item.equippable:
            return f"You cannot equip {item.name}."
            
        # Determine equipment slot
        slot = None
        if item.item_type == "weapon":
            slot = "weapon"
        elif item.item_type == "shield":
            slot = "shield"
        elif item.item_type == "armor":
            slot = "armor"
        elif item.item_type == "ring":
            # Check if ring slots are available
            if self.equipment["ring1"] is None:
                slot = "ring1"
            elif self.equipment["ring2"] is None:
                slot = "ring2"
            else:
                return "You cannot equip more rings."
        elif item.item_type == "amulet":
            slot = "amulet"
        else:
            return f"Cannot equip {item.name}."
            
        # Unequip current item in that slot if any
        if self.equipment[slot] is not None:
            self.equipment[slot].equipped = False
            
        # Equip new item
        self.equipment[slot] = item
        item.equipped = True
        
        return f"You equipped {item.name}."
    
    def unequip_item(self, slot: str) -> str:
        """Unequip an item from specified slot. Return result message."""
        if slot not in self.equipment or self.equipment[slot] is None:
            return f"Nothing equipped in {slot}."
            
        item = self.equipment[slot]
        item.equipped = False
        self.equipment[slot] = None
        
        return f"You unequipped {item.name}."
    
    def get_attack_power(self) -> int:
        """Calculate the player's attack power."""
        base_attack = self.strength // 2
        
        if self.equipment["weapon"]:
            weapon_damage = self.equipment["weapon"].get_damage()
            # Apply stat scaling based on weapon type
            weapon_stats = self.equipment["weapon"].stats
            if "scaling" in weapon_stats:
                if weapon_stats["scaling"] == "strength":
                    scaling_bonus = self.strength // 3
                elif weapon_stats["scaling"] == "dexterity":
                    scaling_bonus = self.dexterity // 3
                else:
                    scaling_bonus = 0
                weapon_damage += scaling_bonus
            
            base_attack += weapon_damage
        
        # Apply stance modifiers
        if self.stance == "aggressive":
            base_attack = int(base_attack * 1.2)  # 20% more damage
        elif self.stance == "defensive":
            base_attack = int(base_attack * 0.8)  # 20% less damage
            
        return base_attack
    
    def get_defense(self) -> int:
        """Calculate the player's defense value."""
        base_defense = self.vitality // 2
        
        if self.equipment["armor"]:
            base_defense += self.equipment["armor"].stats["defense"]
            
        if self.equipment["shield"] and self.stance != "aggressive":
            base_defense += self.equipment["shield"].stats["defense"]
        
        # Apply stance modifiers
        if self.stance == "defensive":
            base_defense = int(base_defense * 1.2)  # 20% more defense
        elif self.stance == "aggressive":
            base_defense = int(base_defense * 0.8)  # 20% less defense
            
        return base_defense
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        defense = self.get_defense()
        
        # Apply resistances from equipment
        resistance_mult = 1.0
        for slot, item in self.equipment.items():
            if item and "resistance" in item.stats and damage_type in item.stats["resistance"]:
                resistance_mult -= item.stats["resistance"][damage_type] / 100.0
        
        # Ensure resistance multiplier is at least 0.2 (80% damage reduction max)
        resistance_mult = max(0.2, resistance_mult)
        
        # Calculate final damage
        damage = int(max(1, amount * resistance_mult - defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the player is dead."""
        return self.hp <= 0
    
    def die(self):
        """Handle player death."""
        # Drop essence at current location
        self.lost_essence = self.essence
        self.lost_essence_location = self.current_location
        self.essence = 0
        
        # Respawn at last beacon
        # This would be implemented in the game loop logic
    
    def recover_lost_essence(self):
        """Recover lost essence."""
        if self.lost_essence > 0:
            self.essence += self.lost_essence
            self.lost_essence = 0
            self.lost_essence_location = None
            return True
        return False
    
    def level_up(self, stat: str) -> bool:
        """Level up a stat. Return True if successful."""
        cost = self.calculate_level_cost()
        
        if self.essence < cost:
            return False
            
        self.essence -= cost
        self.level += 1
        
        # Increase the chosen stat
        if stat == "strength":
            self.strength += 1
        elif stat == "dexterity":
            self.dexterity += 1
        elif stat == "intelligence":
            self.intelligence += 1
        elif stat == "faith":
            self.faith += 1
        elif stat == "vitality":
            self.vitality += 1
            self.max_hp += 5
            self.hp += 5
        elif stat == "endurance":
            self.endurance += 1
            self.max_stamina += 5
            self.stamina += 5
        
        return True
    
    def calculate_level_cost(self) -> int:
        """Calculate the essence cost for the next level."""
        return int(100 * (1.1 ** (self.level - 1)))
    
    def use_item(self, item_index: int) -> str:
        """Use an item from inventory by index."""
        if item_index < 0 or item_index >= len(self.inventory):
            return "Invalid item index."
            
        item = self.inventory[item_index]
        
        if not item.usable:
            return f"You cannot use {item.name}."
            
        result = item.use(self)
        
        # Remove item if quantity reaches 0
        if item.quantity <= 0:
            self.inventory.pop(item_index)
            
        return result
    
    def change_stance(self, new_stance: str) -> str:
        """Change combat stance. Return result message."""
        valid_stances = ["balanced", "aggressive", "defensive"]
        
        if new_stance not in valid_stances:
            return f"Invalid stance. Choose from: {', '.join(valid_stances)}"
            
        old_stance = self.stance
        self.stance = new_stance
        
        return f"Changed stance from {old_stance} to {new_stance}."
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for saving."""
        return {
            "name": self.name,
            "character_class": self.character_class,
            "level": self.level,
            "essence": self.essence,
            "lost_essence": self.lost_essence,
            "lost_essence_location": self.lost_essence_location,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "max_stamina": self.max_stamina,
            "stamina": self.stamina,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "faith": self.faith,
            "vitality": self.vitality,
            "endurance": self.endurance,
            "inventory": [item.to_dict() for item in self.inventory],
            "equipment": {slot: (item.to_dict() if item else None) for slot, item in self.equipment.items()},
            "estus_flask": self.estus_flask,
            "current_location": self.current_location,
            "quests": self.quests,
            "discovered_locations": list(self.discovered_locations),
            "killed_enemies": self.killed_enemies,
            "stance": self.stance
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create a player from dictionary data."""
        player = cls(
            name=data["name"],
            character_class=data["character_class"],
            level=data["level"]
        )
        player.essence = data["essence"]
        player.lost_essence = data["lost_essence"]
        player.lost_essence_location = data["lost_essence_location"]
        player.max_hp = data["max_hp"]
        player.hp = data["hp"]
        player.max_stamina = data["max_stamina"]
        player.stamina = data["stamina"]
        player.strength = data["strength"]
        player.dexterity = data["dexterity"]
        player.intelligence = data["intelligence"]
        player.faith = data["faith"]
        player.vitality = data["vitality"]
        player.endurance = data["endurance"]
        
        # Reconstruct inventory
        player.inventory = []
        for item_data in data["inventory"]:
            if item_data["item_type"] == "weapon":
                item = Weapon(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    damage=item_data["stats"]["damage"],
                    damage_type=item_data["stats"]["damage_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    special_ability=item_data["stats"].get("special_ability"),
                    two_handed=item_data["stats"].get("two_handed", False)
                )
            elif item_data["item_type"] == "armor":
                item = Armor(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    defense=item_data["stats"]["defense"],
                    armor_type=item_data["stats"]["armor_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    resistance=item_data["stats"].get("resistance")
                )
            elif item_data["item_type"] == "consumable":
                item = Consumable(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    effect=item_data["stats"],
                    value=item_data["value"],
                    weight=item_data["weight"],
                    quantity=item_data["quantity"]
                )
            else:
                item = Item.from_dict(item_data)
                
            item.quantity = item_data["quantity"]
            item.equipped = item_data["equipped"]
            player.inventory.append(item)
        
        # Reconstruct equipment
        player.equipment = {slot: None for slot in player.equipment.keys()}
        for slot, item_data in data["equipment"].items():
            if item_data:
                for item in player.inventory:
                    if item.id == item_data["id"]:
                        player.equipment[slot] = item
                        break
                        
        player.estus_flask = data["estus_flask"]
        player.current_location = data["current_location"]
        player.quests = data["quests"]
        player.discovered_locations = set(data["discovered_locations"])
        player.killed_enemies = data["killed_enemies"]
        player.stance = data["stance"]
        
        return player

class World:
    def __init__(self):
        self.locations = {}
        self.npcs = {}
        self.items = {}
        self.enemies = {}
        self.bosses = {}
        self.quests = {}
        self.active_events = set()
        self.game_state = {}
        
        # Initialize world components
        self.initialize_world()
    
    def initialize_world(self):
        """Initialize and load all world data."""
        self.load_locations()
        self.load_npcs()
        self.load_items()
        self.load_enemies()
        self.load_bosses()
        self.load_quests()
    
    def load_locations(self):
        """Load all location data."""
        # Highcastle Region
        self.locations["highcastle_entrance"] = Location(
            id="highcastle_entrance",
            name="Highcastle Gate",
            description="The towering gates of Highcastle stand before you, worn by time but still majestic. The once-bustling gatehouse is now quiet, with only a few guards maintaining their eternal vigil.",
            connections={
                "north": "highcastle_plaza",
                "east": "eastern_road",
                "west": "western_path"
            },
            enemies=["wandering_hollow", "fallen_knight"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Gate
       v S       o - You
  
  #################
  #####.....######
  ####...o...#####
  ###.........####
  ##.....+.....###
  #...............
  #...............
            """,
            first_visit_text="You arrive at the once-grand entrance to Highcastle, the last bastion of humanity in these dark times. The walls, though weathered, still stand tall against the encroaching darkness that has consumed much of Ardenvale."
        )
        
        self.locations["highcastle_plaza"] = Location(
            id="highcastle_plaza",
            name="Highcastle Central Plaza",
            description="The central plaza of Highcastle is a shadow of its former glory. Cracked fountains and weathered statues are silent witnesses to a time of prosperity long gone. A few desperate souls still wander here, clinging to routines of a life that no longer exists.",
            connections={
                "north": "highcastle_cathedral",
                "east": "eastern_district",
                "west": "western_district",
                "south": "highcastle_entrance"
            },
            enemies=["hollow_citizen", "corrupted_guard"],
            npcs=["andre_smith", "merchant_ulrich"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ###+######+####
  #...........+.#
  #.....o.......#
  #...#...#...#.#
  #.............#
  #...#...#...#.#
  ###....+....###
            """
        )
        
        self.locations["highcastle_cathedral"] = Location(
            id="highcastle_cathedral",
            name="Cathedral of the Fading Light",
            description="This once-magnificent cathedral now stands in partial ruin. Shafts of light pierce through holes in the ceiling, illuminating dust-covered pews and crumbling statues of forgotten deities. Despite its state, there is still an aura of reverence here.",
            connections={
                "south": "highcastle_plaza",
                "east": "cathedral_tower"
            },
            enemies=["cathedral_knight", "deacon_of_the_deep"],
            npcs=["sister_friede"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ########+######
  #..#.......#..#
  #...........+.#
  #.............#
  #....o........#
  #.....###.....#
  ##....+....####
            """
        )
        
        # Ashen Woods Region
        self.locations["western_path"] = Location(
            id="western_path",
            name="Western Path",
            description="A winding path leads westward from Highcastle. Once a well-traveled trade route, it is now overgrown and dangerous. The trees along the path seem to lean inward, as if watching passersby with malicious intent.",
            connections={
                "east": "highcastle_entrance",
                "west": "ashen_woods_entrance"
            },
            enemies=["wild_beast", "hollow_woodsman"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     % - Trees
       |         ~ - Water
       v S       o - You
  
  %%%%%%%%%%%    
  %%%..........
  %%%...o......
  %%%...........
  %%%...........
  %%%.......%%%%
  %%%%%%%%%%%    
            """
        )
        
        self.locations["ashen_woods_entrance"] = Location(
            id="ashen_woods_entrance",
            name="Ashen Woods Entrance",
            description="The entrance to the Ashen Woods is marked by a sudden change in the landscape. The trees here are grey and lifeless, their bark turned to ash. Wisps of smoke rise from the ground, though there is no fire to be seen.",
            connections={
                "east": "western_path",
                "west": "ashen_woods_clearing"
            },
            enemies=["ember_wolf", "ashen_treant"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         % - Trees
  W <----> E     ^ - Ash trees
       |         ~ - Water
       v S       o - You
  
  ^^^^^^^^^^^^^^
  ^^.....^^^.^^^
  ^.......o...^^
  ^............^
  ^^^..........^
  ^^^^^^^^^^^^^^
  ^^^^^^^^^^^^^^
            """
        )
        
        # Add more locations as needed...
    
    def load_npcs(self):
        """Load all NPC data."""
        self.npcs["andre_smith"] = NPC(
            id="andre_smith",
            name="Andre the Smith",
            description="A muscular blacksmith with arms like tree trunks. Despite the dark times, his eyes still hold a passionate fire for his craft. His hammer strikes rhythmically in the background.",
            dialogue={
                "default": {
                    "text": "Need something forged? Or perhaps an upgrade to that weapon of yours?",
                    "options": {
                        "1": {
                            "text": "I'd like to upgrade my weapon.",
                            "next": "upgrade"
                        },
                        "2": {
                            "text": "Tell me about yourself.",
                            "next": "about"
                        },
                        "3": {
                            "text": "What happened to this place?",
                            "next": "history"
                        },
                        "4": {
                            "text": "Do you have any work for me?",
                            "next": "quest"
                        }
                    }
                },
                "upgrade": {
                    "text": "Ah, let me see what you've got. I can work with most materials, given enough time and the right components.",
                    "options": {
                        "1": {
                            "text": "What materials do you need?",
                            "next": "materials"
                        },
                        "2": {
                            "text": "Actually, let's talk about something else.",
                            "next": "default"
                        }
                    }
                },
                "materials": {
                    "text": "For basic reinforcement, I need titanite shards. For special weapons, I might need ember essence from the Ashen Woods, or perhaps something more exotic. Bring me materials, and I'll see what I can do.",
                    "options": {
                        "1": {
                            "text": "I'll keep an eye out for those.",
                            "next": "default"
                        }
                    }
                },
                "about": {
                    "text": "Been a smith all my life. Learned from my father, who learned from his. I've seen kingdoms rise and fall, but the forge remains. As long as there are warriors who need weapons, I'll be here.",
                    "options": {
                        "1": {
                            "text": "How have you survived the hollowing?",
                            "next": "survived"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "survived": {
                    "text": "Purpose, friend. Those who hollow are those who've lost their purpose. As long as I have my hammer and anvil, I have a reason to keep going. Find your purpose, and you'll never hollow.",
                    "options": {
                        "1": {
                            "text": "That's profound wisdom.",
                            "next": "default",
                            "relationship": 5
                        }
                    }
                },
                "history": {
                    "text": "Highcastle was once the jewel of Ardenvale. When the First Flame began to fade, everything changed. The corruption spread, people hollowed, and darkness crept in. But we endure. We always do.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the First Flame.",
                            "next": "first_flame"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "first_flame": {
                    "text": "The First Flame is what brought light and disparity to our world. Heat and cold, life and death, light and dark... all because of the Flame. Now it fades, and the balance tips toward darkness. Some seek to rekindle it, others to usher in an Age of Dark. Me? I just forge.",
                    "options": {
                        "1": {
                            "text": "Can the Flame be rekindled?",
                            "next": "rekindle"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "rekindle": {
                    "text": "The old legends say it can, but at a cost. Great souls must be sacrificed to feed the Flame. The King... they say he sought another way, and look where that got us. But who knows? Maybe you'll find answers where others failed.",
                    "options": {
                        "1": {
                            "text": "I'll discover the truth.",
                            "next": "default"
                        }
                    }
                },
                "quest": {
                    "text": "As a matter of fact, I do. My old forge has run cold without proper ember. If you could venture to the Ashen Woods and bring back some ember essence, I could craft you something special.",
                    "options": {
                        "1": {
                            "text": "I'll find this ember essence for you.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "That sounds too dangerous.",
                            "next": "quest_decline"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Excellent! Look for it near what they call Ember Lake, deep in the Ashen Woods. The essence glows like a captured sunset. Careful though, the woods have grown wild and hostile since the Flame began to fade.",
                    "options": {
                        "1": {
                            "text": "I'll be careful.",
                            "next": "default",
                            "quest_progress": {"start": "ember_quest"}
                        }
                    }
                },
                "quest_decline": {
                    "text": "Fair enough. It's no small task. The offer stands if you change your mind.",
                    "options": {
                        "1": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_complete": {
                    "text": "By the Flame, you actually found it! This ember essence is perfect. Give me some time, and I'll forge you something worthy of your courage.",
                    "options": {
                        "1": {
                            "text": "Thank you, Andre.",
                            "next": "reward"
                        }
                    }
                },
                "reward": {
                    "text": "Here, take this blade. I call it the Flamebrand. The ember essence is forged into its very core. May it serve you well in the darkness ahead.",
                    "options": {
                        "1": {
                            "text": "It's beautiful. Thank you.",
                            "next": "default",
                            "quest_progress": {"complete": "ember_quest"}
                        }
                    }
                }
            },
            quest={
                "id": "ember_quest",
                "name": "The Smith's Request",
                "description": "Andre needs ember essence from the Ashen Woods to rekindle his forge.",
                "objectives": [
                    {"type": "item", "target": "ember_essence", "quantity": 1}
                ],
                "rewards": {
                    "item": "flamebrand",
                    "essence": 200
                }
            },
            shop_inventory=["reinforced_sword", "knight_shield", "ember"]
        )
        
        self.npcs["merchant_ulrich"] = NPC(
            id="merchant_ulrich",
            name="Merchant Ulrich",
            description="A hunched man with a perpetual nervous twitch. His eyes dart about constantly, and his fingers fidget with the hem of his tattered cloak. Despite his appearance, he has somehow managed to maintain a stock of rare goods.",
            dialogue={
                "default": {
                    "text": "Ah, a customer! Rare sight these days. Looking to trade? I've got wares from all corners of Ardenvale, before... well, before everything went to ruin.",
                    "options": {
                        "1": {
                            "text": "Show me what you have for sale.",
                            "next": "shop"
                        },
                        "2": {
                            "text": "Any rumors lately?",
                            "next": "rumors"
                        },
                        "3": {
                            "text": "How do you get your merchandise?",
                            "next": "merchandise"
                        },
                        "4": {
                            "text": "I'm looking for something specific.",
                            "next": "quest_intro"
                        }
                    }
                },
                "shop": {
                    "text": "Take a look, take a look! Fine goods at reasonable prices. Well, reasonable considering the state of the world.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "rumors": {
                    "text": "Rumors? Oh, I hear many things... They say the old king still wanders the Ringed Citadel, hollowed but retaining a fragment of his former self. And in the Ashen Woods, the tree shepherds have gone mad, attacking any who venture too deep.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the king.",
                            "next": "king"
                        },
                        "2": {
                            "text": "What are tree shepherds?",
                            "next": "shepherds"
                        },
                        "3": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "king": {
                    "text": "King Morgaeth was a wise ruler, once. They say he delved too deep into forbidden arts in his quest to save the kingdom from the fading of the Flame. Now he's neither dead nor truly alive... a hollow shell of royalty.",
                    "options": {
                        "1": {
                            "text": "What forbidden arts did he study?",
                            "next": "forbidden_arts"
                        },
                        "2": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        }
                    }
                },
                "forbidden_arts": {
                    "text": "They say he sought to draw power from the Abyss itself. To use darkness to preserve light, if you can imagine such madness. The royal archives might hold more answers, but none dare venture to the Ringed Citadel now.",
                    "options": {
                        "1": {
                            "text": "Interesting. Thank you for the information.",
                            "next": "default",
                            "quest_progress": {"hint": "kings_fall"}
                        }
                    }
                },
                "shepherds": {
                    "text": "Ancient creatures, like walking trees but with awareness. They tended the forests for millennia in peace. The corruption has twisted them, made them violent. A shame. They were magnificent beings.",
                    "options": {
                        "1": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "merchandise": {
                    "text": "Ah, professional secrets! *winks nervously* Let's just say I have... arrangements with certain brave souls who venture where others fear to tread. They bring me goods, I give them essence, everyone profits!",
                    "options": {
                        "1": {
                            "text": "Sounds dangerous.",
                            "next": "dangerous"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dangerous": {
                    "text": "Dangerous? *laughs shakily* My friend, everything is dangerous now. At least my suppliers choose their danger. Most of them return... some of the time.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "quest_intro": {
                    "text": "Something specific? *eyes narrow with interest* I might have what you need, or know where to find it. What are you looking for?",
                    "options": {
                        "1": {
                            "text": "I need access to the Ringed Citadel.",
                            "next": "quest_citadel"
                        },
                        "2": {
                            "text": "Just browsing, actually.",
                            "next": "default"
                        }
                    }
                },
                "quest_citadel": {
                    "text": "*lowers voice* The Citadel? Not many seek to go there willingly. *glances around nervously* I might know of a way, but it will cost you. Not just essence, but a favor.",
                    "options": {
                        "1": {
                            "text": "What kind of favor?",
                            "next": "quest_details"
                        },
                        "2": {
                            "text": "Never mind, too risky.",
                            "next": "default"
                        }
                    }
                },
                "quest_details": {
                    "text": "One of my suppliers ventured into the Blighted Marshes east of here. Never returned. Carried a signet ring I need back. Find it, and I'll give you what you need to enter the Citadel.",
                    "options": {
                        "1": {
                            "text": "I'll find your ring.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Good, good. The marshes are treacherous, but look for a broken cart near the eastern path. That's where my supplier was headed. The ring has a blue stone, can't miss it.",
                    "options": {
                        "1": {
                            "text": "I'll return when I have it.",
                            "next": "default",
                            "quest_progress": {"start": "signet_quest"}
                        }
                    }
                },
                "quest_complete": {
                    "text": "*eyes widen* You found it! And lived to tell the tale! I'm impressed. As promised, here's what you need—a royal seal. It will grant you passage through the outer gates of the Ringed Citadel.",
                    "options": {
                        "1": {
                            "text": "Thank you for your help.",
                            "next": "default",
                            "quest_progress": {"complete": "signet_quest"}
                        }
                    }
                }
            },
            quest={
                "id": "signet_quest",
                "name": "The Merchant's Signet",
                "description": "Find Ulrich's missing signet ring in the Blighted Marshes.",
                "objectives": [
                    {"type": "item", "target": "blue_signet", "quantity": 1}
                ],
                "rewards": {
                    "item": "royal_seal",
                    "essence": 300
                }
            },
            shop_inventory=["estus_shard", "life_gem", "homeward_bone", "green_blossom"]
        )
        
        self.npcs["sister_friede"] = NPC(
            id="sister_friede",
            name="Sister Friede",
            description="A tall, slender woman in white robes that seem untouched by the grime and decay around her. Her face is partially obscured by a hood, but you can see her pale skin and piercing blue eyes. She moves with eerie grace.",
            dialogue={
                "default": {
                    "text": "Ashen One, why do you disturb this sanctuary? This is a place of quiet reflection, not for those who would perpetuate a doomed cycle.",
                    "options": {
                        "1": {
                            "text": "I seek guidance.",
                            "next": "guidance"
                        },
                        "2": {
                            "text": "What cycle do you speak of?",
                            "next": "cycle"
                        },
                        "3": {
                            "text": "Who are you?",
                            "next": "identity"
                        },
                        "4": {
                            "text": "Are you in danger here?",
                            "next": "quest_intro"
                        }
                    }
                },
                "guidance": {
                    "text": "Guidance? *soft laugh* The path ahead is shrouded for all of us. But if you must continue your journey, seek the depths of the Ashen Woods. There lies an ancient tree shepherd who remembers the time before corruption. His wisdom may aid you, if he doesn't kill you first.",
                    "options": {
                        "1": {
                            "text": "Thank you for the information.",
                            "next": "default"
                        },
                        "2": {
                            "text": "Why would he help me?",
                            "next": "help"
                        }
                    }
                },
                "help": {
                    "text": "He wouldn't, not willingly. But in his madness, truths slip out between attempts to end your life. Listen carefully... if you survive long enough to hear anything at all.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "cycle": {
                    "text": "The endless cycle of Light and Dark. For eons, the First Flame has been rekindled when it begins to fade, postponing the Age of Dark that is our birthright. Each rekindling only makes the inevitable collapse more devastating.",
                    "options": {
                        "1": {
                            "text": "You want the Flame to fade?",
                            "next": "fade"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "fade": {
                    "text": "*her eyes narrow slightly* I want what is natural. All fires eventually burn out. Fighting this truth has brought us to this state of perpetual decay. Let it end, and something new may begin.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "identity": {
                    "text": "I am simply a watcher. I've seen kingdoms rise and fall, flames kindle and fade. Now I wait here, in this broken cathedral, observing the final gasps of a dying age.",
                    "options": {
                        "1": {
                            "text": "You speak as if you're ancient.",
                            "next": "ancient"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "ancient": {
                    "text": "*she smiles enigmatically* Time loses meaning when you've witnessed enough cycles. But enough about me. What will you do, Ashen One? Perpetuate this dying world, or help usher in something new?",
                    "options": {
                        "1": {
                            "text": "I'll restore the Flame.",
                            "next": "restore",
                            "relationship": -10
                        },
                        "2": {
                            "text": "Perhaps the Dark should have its time.",
                            "next": "dark",
                            "relationship": 10
                        },
                        "3": {
                            "text": "I haven't decided yet.",
                            "next": "undecided"
                        }
                    }
                },
                "restore": {
                    "text": "*her expression hardens* Then you are no different from the others. Go your way, Ashen One. May you find what you seek... and understand its true cost.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dark": {
                    "text": "*she studies you with new interest* Perhaps there is wisdom in you after all. The Dark is not to be feared, but embraced as part of the natural order. Remember this when your resolve is tested.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "undecided": {
                    "text": "Indecision is... understandable. The weight of such choices is immense. Reflect carefully, Ashen One. Not all is as it seems in Ardenvale.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "quest_intro": {
                    "*she seems surprised by your concern* No, not from the hollowed ones. They avoid this place. But there is a matter that... troubles me. The cathedral's sacred chalice has been stolen, taken to the bell tower by one who has fallen far from grace.",
                    "options": {
                        "1": {
                            "text": "I could retrieve it for you.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "Why is the chalice important?",
                            "next": "chalice_importance"
                        }
                    }
                },
                "chalice_importance": {
                    "text": "It contains old knowledge, symbols of both light and dark in perfect balance. In the wrong hands, this knowledge could upset the natural order, prolong this agonizing age of transition.",
                    "options": {
                        "1": {
                            "text": "I'll retrieve the chalice.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Your offer is... unexpected. The thief is a former deacon, now corrupted beyond recognition. Ascend to the bell tower, but be wary—he will not surrender the chalice willingly.",
                    "options": {
                        "1": {
                            "text": "I'll be careful.",
                            "next": "default",
                            "quest_progress": {"start": "chalice_quest"}
                        }
                    }
                },
                "quest_complete": {
                    "text": "*her eyes widen slightly as you present the chalice* You succeeded where others would have failed. The balance is preserved, for now. Please, take this talisman as a token of my... gratitude. It bears an old symbol of the dark.",
                    "options": {
                        "1": {
                            "text": "Thank you, Sister Friede.",
                            "next": "default",
                            "quest_progress": {"complete": "chalice_quest"},
                            "relationship": 15
                        }
                    }
                }
            },
            quest={
                "id": "chalice_quest",
                "name": "The Sacred Chalice",
                "description": "Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
                "objectives": [
                    {"type": "item", "target": "sacred_chalice", "quantity": 1}
                ],
                "rewards": {
                    "item": "dark_talisman",
                    "essence": 350,
                    "faction": "Children of Dark",
                    "reputation": 15
                }
            },
            faction="Children of Dark"
        )
    
    def load_items(self):
        """Load all item data."""
        # Weapons
        self.items["reinforced_sword"] = Weapon(
            id="reinforced_sword",
            name="Reinforced Longsword",
            description="A sturdy longsword with reinforced steel. Reliable and well-balanced.",
            damage=15,
            damage_type="physical",
            weight=3.0,
            value=200,
            two_handed=False
        )
        
        self.items["knight_sword"] = Weapon(
            id="knight_sword",
            name="Knight's Sword",
            description="A well-crafted sword used by the knights of Highcastle. The blade bears the insignia of the royal guard.",
            damage=18,
            damage_type="physical",
            weight=3.5,
            value=300,
            two_handed=False
        )
        
        self.items["woodsman_axe"] = Weapon(
            id="woodsman_axe",
            name="Woodsman's Axe",
            description="A heavy axe used for chopping wood, now repurposed as a weapon. Slow but powerful.",
            damage=22,
            damage_type="physical",
            weight=4.5,
            value=180,
            two_handed=True
        )
        
        self.items["cathedral_greatsword"] = Weapon(
            id="cathedral_greatsword",
            name="Cathedral Greatsword",
            description="A massive sword wielded by the knights of the cathedral. Holy symbols are etched into the blade.",
            damage=26,
            damage_type="physical",
            weight=6.0,
            value=450,
            two_handed=True,
            special_ability={"name": "Holy Light", "damage": 15, "type": "holy"}
        )
        
        self.items["ember_blade"] = Weapon(
            id="ember_blade",
            name="Ember Blade",
            description="A sword forged in the heart of the Ashen Woods. The blade seems to smolder with inner heat.",
            damage=20,
            damage_type="fire",
            weight=3.0,
            value=500,
            two_handed=False,
            special_ability={"name": "Ignite", "damage": 12, "type": "fire", "duration": 3}
        )
        
        self.items["vordt_mace"] = Weapon(
            id="vordt_mace",
            name="Vordt's Frostmace",
            description="A massive mace once wielded by Vordt, Guardian of the Frost Gate. Crystals of ice form along its surface.",
            damage=30,
            damage_type="physical",
            weight=8.0,
            value=700,
            two_handed=True,
            special_ability={"name": "Frost Strike", "damage": 20, "type": "ice", "slow_effect": True}
        )
        
        self.items["kings_greatsword"] = Weapon(
            id="kings_greatsword",
            name="King's Greatsword",
            description="The royal greatsword of King Morgaeth, now tainted with dark energy. It pulses with corrupted power.",
            damage=35,
            damage_type="physical",
            weight=7.0,
            value=1000,
            two_handed=True,
            special_ability={"name": "Royal Wrath", "damage": 40, "type": "dark", "cooldown": 5}
        )
        
        # Armor
        self.items["knight_helm"] = Armor(
            id="knight_helm",
            name="Knight's Helm",
            description="A standard helmet worn by the knights of Highcastle. Provides good protection but limits visibility.",
            defense=10,
            armor_type="head",
            weight=2.0,
            value=200
        )
        
        self.items["knight_shield"] = Armor(
            id="knight_shield",
            name="Knight's Shield",
            description="A sturdy kite shield bearing the crest of Highcastle. Well-balanced for both defense and mobility.",
            defense=15,
            armor_type="shield",
            weight=3.5,
            value=250
        )
        
        self.items["rusted_shield"] = Armor(
            id="rusted_shield",
            name="Rusted Shield",
            description="A worn shield that has seen better days. Despite the rust, it still offers adequate protection.",
            defense=8,
            armor_type="shield",
            weight=3.0,
            value=100
        )
        
        self.items["cathedral_plate"] = Armor(
            id="cathedral_plate",
            name="Cathedral Plate Armor",
            description="Heavy armor worn by the elite knights of the cathedral. Ornate religious symbols adorn the breastplate.",
            defense=25,
            armor_type="chest",
            weight=8.0,
            value=500,
            resistance={"dark": 15}
        )
        
        self.items["deacon_robes"] = Armor(
            id="deacon_robes",
            name="Deacon's Robes",
            description="Dark robes worn by the deacons of the cathedral. Offers little physical protection but imbued with arcane resistance.",
            defense=5,
            armor_type="chest",
            weight=1.5,
            value=300,
            resistance={"magic": 20, "fire": 10}
        )
        
        self.items["frost_knight_armor"] = Armor(
            id="frost_knight_armor",
            name="Frost Knight Armor",
            description="Armor coated in a permanent layer of frost. Extremely heavy but offers exceptional protection.",
            defense=30,
            armor_type="chest",
            weight=12.0,
            value=800,
            resistance={"fire": 25, "ice": -10}  # Vulnerable to ice
        )
        
        self.items["hollowed_crown"] = Armor(
            id="hollowed_crown",
            name="Hollowed Crown",
            description="The tarnished crown of King Morgaeth. Dark energy swirls within its jewels.",
            defense=12,
            armor_type="head",
            weight=1.0,
            value=1200,
            resistance={"dark": 30, "holy": -25}  # Vulnerable to holy
        )
        
        # Consumables
        self.items["soul_remnant"] = Consumable(
            id="soul_remnant",
            name="Soul Remnant",
            description="A fragment of essence that can be consumed to restore a small amount of health.",
            effect={"healing": 15},
            value=10,
            quantity=1
        )
        
        self.items["life_gem"] = Consumable(
            id="life_gem",
            name="Life Gem",
            description="A crystal that slowly restores health when crushed and consumed.",
            effect={"healing": 30, "over_time": True, "duration": 5},
            value=100,
            quantity=1
        )
        
        self.items["ember"] = Consumable(
            id="ember",
            name="Ember",
            description="A warm ember that temporarily boosts maximum health when consumed.",
            effect={"max_health_boost": 20, "duration": 180},
            value=150,
            quantity=1
        )
        
        self.items["green_blossom"] = Consumable(
            id="green_blossom",
            name="Green Blossom",
            description="A fragrant green herb that temporarily boosts stamina regeneration.",
            effect={"stamina_regen": 20, "duration": 60},
            value=120,
            quantity=1
        )
        
        self.items["estus_shard"] = Item(
            id="estus_shard",
            name="Estus Shard",
            description="A fragment of an Estus Flask. Can be used to increase the number of uses for your Estus Flask.",
            item_type="key",
            value=500,
            usable=True
        )
        
        self.items["homeward_bone"] = Item(
            id="homeward_bone",
            name="Homeward Bone",
            description="A charred bone that carries the scent of home. Use to return to the last rested beacon.",
            item_type="consumable",
            value=150,
            usable=True,
            quantity=1
        )
        
        self.items["dark_residue"] = Item(
            id="dark_residue",
            name="Dark Residue",
            description="A strange, viscous substance that seems to absorb light. Used in certain crafting recipes.",
            item_type="material",
            value=50,
            usable=False,
            quantity=1
        )
        
        self.items["ember_essence"] = Item(
            id="ember_essence",
            name="Ember Essence",
            description="A concentrated form of fire energy. Warm to the touch and glows softly in darkness.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["frost_essence"] = Item(
            id="frost_essence",
            name="Frost Essence",
            description="Crystallized cold energy. The air around it is perpetually chilled.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["blessed_medallion"] = Item(
            id="blessed_medallion",
            name="Blessed Medallion",
            description="A holy symbol that provides protection against the dark. Slowly regenerates health when equipped.",
            item_type="amulet",
            value=300,
            equippable=True,
            stats={"health_regen": 1, "resistance": {"dark": 10}},
            quantity=1
        )
        
        self.items["dark_tome"] = Item(
            id="dark_tome",
            name="Dark Tome",
            description="An ancient book containing forbidden knowledge. The pages seem to whisper when turned.",
            item_type="catalyst",
            value=400,
            equippable=True,
            stats={"spell_boost": 15, "intelligence_scaling": True},
            quantity=1
        )
        
        self.items["royal_signet"] = Item(
            id="royal_signet",
            name="Royal Signet Ring",
            description="The royal signet of King Morgaeth. Grants authority and increases essence gained from defeating enemies.",
            item_type="ring",
            value=800,
            equippable=True,
            stats={"essence_gain": 1.2, "charisma": 5},
            quantity=1
        )
        
    def load_enemies(self):
        """Load all enemy data."""
        # Basic enemies
        self.enemies["wandering_hollow"] = Enemy(
            id="wandering_hollow",
            name="Wandering Hollow",
            description="A hollowed out corpse that wanders aimlessly. It's eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=1,
            hp=50,
            attack=10,
            defense=5,
            attack_patterns=[{"name": "Basic Attack", "damage": 10, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=10
        )
        
        self.enemies["fallen_knight"] = Enemy(
            id="fallen_knight",
            name="Fallen Knight",
            description="A knight in armor that has been hollowed out. Its eyes are dark and lifeless, reflecting the corruption that has consumed it.",
            level=2,
            hp=70,
            attack=15,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 15, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=20
        )
        
        # Add more enemies as needed...
    
    def load_bosses(self):
        """Load all boss data."""
        # Basic bosses
        self.bosses["hollow_citizen"] = Enemy(
            id="hollow_citizen",
            name="Hollow Citizen",
            description="A hollowed out citizen that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=3,
            hp=100,
            attack=20,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 20, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=30
        )
        
        self.bosses["corrupted_guard"] = Enemy(
            id="corrupted_guard",
            name="Corrupted Guard",
            description="A guard in armor that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=4,
            hp=120,
            attack=25,
            defense=15,
            attack_patterns=[{"name": "Basic Attack", "damage": 25, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=40
        )
        
        # Add more bosses as needed...
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
import os
import json
import time
import random
import pickle
import datetime
import platform
import sys
from typing import Dict, List, Optional, Tuple, Union, Any

# Constants
SAVE_DIR = "saves"
AUTOSAVE_FILE = os.path.join(SAVE_DIR, "autosave.sav")
VERSION = "1.0.0"

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# ASCII Art and UI Elements
TITLE_ART = """
  ╔═══════════════════════════════════════════════════════════╗
  ║  ▄████▄   ██▀███   █    ██  ███▄ ▄███▓ ▄▄▄▄    ██▓    ██▓ ║
  ║ ▒██▀ ▀█  ▓██ ▒ ██▒ ██  ▓██▒▓██▒▀█▀ ██▒▓█████▄ ▓██▒   ▓██▒ ║
  ║ ▒▓█    ▄ ▓██ ░▄█ ▒▓██  ▒██░▓██    ▓██░▒██▒ ▄██▒██░   ▒██░ ║
  ║ ▒▓▓▄ ▄██▒▒██▀▀█▄  ▓▓█  ░██░▒██    ▒██ ▒██░█▀  ▒██░   ▒██░ ║
  ║ ▒ ▓███▀ ░░██▓ ▒██▒▒▒█████▓ ▒██▒   ░██▒░▓█  ▀█▓░██████░██████╗
  ║ ░ ░▒ ▒  ░░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ░ ▒░   ░  ░░▒▓███▀▒░ ▒░▓  ░ ▒░▓  ║
  ║   ░  ▒     ░▒ ░ ▒░░░▒░ ░ ░ ░  ░      ░▒░▒   ░ ░ ░ ▒  ░ ░ ▒  ║
  ║ ░          ░░   ░  ░░░ ░ ░ ░      ░    ░    ░   ░ ░    ░ ░  ║
  ║ ░ ░         ░        ░            ░    ░          ░  ░   ░  ║
  ║                           ARDENVALE                        ║
  ╚═══════════════════════════════════════════════════════════╝
                A REALM SHATTERED BY A FADING FLAME
"""

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                      ARDENVALE                            ║
╚═══════════════════════════════════════════════════════════╝
"""

DIVIDER = "═" * 70

# Utility Functions
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
        
        return {
            "player_name": save_data["player"]["name"],
            "player_level": save_data["player"]["level"],
            "location": save_data["player"]["current_location"],
            "timestamp": save_data["timestamp"],
            "version": save_data["version"]
        }
    except Exception as e:
        return {
            "error": str(e),
            "filename": filename
        }

# Game Classes
class Item:
    def __init__(self, id: str, name: str, description: str, item_type: str, value: int = 0, 
                 weight: float = 0.0, stats: Dict = None, usable: bool = False, 
                 equippable: bool = False, quantity: int = 1):
        self.id = id
        self.name = name
        self.description = description
        self.item_type = item_type  # weapon, armor, consumable, key, etc.
        self.value = value
        self.weight = weight
        self.stats = stats or {}
        self.usable = usable
        self.equippable = equippable
        self.quantity = quantity
        self.equipped = False
    
    def use(self, player) -> str:
        """Use the item and return result message."""
        if not self.usable:
            return f"You cannot use the {self.name}."
        
        # Implement item usage logic here
        result = "You used the item, but nothing happened."
        
        # Example: Healing potion
        if self.item_type == "consumable" and "healing" in self.stats:
            heal_amount = self.stats["healing"]
            player.heal(heal_amount)
            result = f"You drink the {self.name} and recover {heal_amount} health."
            self.quantity -= 1
            
        return result
    
    def to_dict(self) -> Dict:
        """Convert item to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "value": self.value,
            "weight": self.weight,
            "stats": self.stats,
            "usable": self.usable,
            "equippable": self.equippable,
            "quantity": self.quantity,
            "equipped": self.equipped
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Create an item from dictionary data."""
        item = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=data["item_type"],
            value=data["value"],
            weight=data["weight"],
            stats=data["stats"],
            usable=data["usable"],
            equippable=data["equippable"],
            quantity=data["quantity"]
        )
        item.equipped = data["equipped"]
        return item

class Weapon(Item):
    def __init__(self, id: str, name: str, description: str, damage: int, 
                 damage_type: str, weight: float, value: int, 
                 special_ability: Dict = None, two_handed: bool = False):
        stats = {
            "damage": damage,
            "damage_type": damage_type,
            "two_handed": two_handed
        }
        if special_ability:
            stats["special_ability"] = special_ability
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="weapon",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )
    
    def get_damage(self) -> int:
        """Calculate the weapon's damage."""
        base_damage = self.stats["damage"]
        return base_damage
    
    def weapon_art(self, player, target) -> str:
        """Use the weapon's special ability."""
        if "special_ability" not in self.stats:
            return "This weapon has no special ability."
        
        ability = self.stats["special_ability"]
        # Implement weapon special ability logic
        
        return f"You use {ability['name']}!"

class Armor(Item):
    def __init__(self, id: str, name: str, description: str, defense: int, 
                 armor_type: str, weight: float, value: int, 
                 resistance: Dict = None):
        stats = {
            "defense": defense,
            "armor_type": armor_type,
        }
        if resistance:
            stats["resistance"] = resistance
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="armor",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )

class Consumable(Item):
    def __init__(self, id: str, name: str, description: str, effect: Dict, 
                 value: int, weight: float = 0.1, quantity: int = 1):
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="consumable",
            value=value,
            weight=weight,
            stats=effect,
            usable=True,
            equippable=False,
            quantity=quantity
        )

class Enemy:
    def __init__(self, id: str, name: str, description: str, level: int, 
                 hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.attack_patterns = attack_patterns or []
        self.loot_table = loot_table or []
        self.essence = essence
        self.weaknesses = weaknesses or []
        self.current_pattern_index = 0
    
    def get_next_attack(self) -> Dict:
        """Get the next attack pattern in sequence."""
        if not self.attack_patterns:
            return {"name": "Basic Attack", "damage": self.attack, "type": "physical"}
        
        pattern = self.attack_patterns[self.current_pattern_index]
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.attack_patterns)
        return pattern
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        # Apply weakness multipliers
        multiplier = 1.0
        if damage_type in self.weaknesses:
            multiplier = 1.5
            
        damage = int(max(1, amount * multiplier - self.defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the enemy is dead."""
        return self.hp <= 0
    
    def drop_loot(self) -> List[Item]:
        """Generate loot drops based on loot table."""
        drops = []
        for loot_entry in self.loot_table:
            if random.random() < loot_entry["chance"]:
                # Create the item from the item database
                item_id = loot_entry["item_id"]
                item = create_item(item_id)
                if item:
                    # Set quantity if specified
                    if "quantity" in loot_entry:
                        item.quantity = random.randint(
                            loot_entry["quantity"]["min"], 
                            loot_entry["quantity"]["max"]
                        )
                    drops.append(item)
        return drops
    
    def to_dict(self) -> Dict:
        """Convert enemy to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "attack_patterns": self.attack_patterns,
            "loot_table": self.loot_table,
            "essence": self.essence,
            "weaknesses": self.weaknesses,
            "current_pattern_index": self.current_pattern_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Enemy':
        """Create an enemy from dictionary data."""
        enemy = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            level=data["level"],
            hp=data["max_hp"],
            attack=data["attack"],
            defense=data["defense"],
            attack_patterns=data["attack_patterns"],
            loot_table=data["loot_table"],
            essence=data["essence"],
            weaknesses=data["weaknesses"]
        )
        enemy.hp = data["hp"]
        enemy.current_pattern_index = data["current_pattern_index"]
        return enemy

class Boss(Enemy):
    def __init__(self, id: str, name: str, title: str, description: str, 
                 level: int, hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None,
                 phases: List[Dict] = None):
        super().__init__(
            id=id,
            name=f"{name}, {title}",
            description=description,
            level=level,
            hp=hp,
            attack=attack,
            defense=defense,
            attack_patterns=attack_patterns,
            loot_table=loot_table,
            essence=essence,
            weaknesses=weaknesses
        )
        self.phases = phases or []
        self.current_phase = 0
        self.phase_triggers = [phase["trigger"] for phase in self.phases] if phases else []
    
    def update_phase(self) -> bool:
        """Check and update boss phase based on HP. Return True if phase changed."""
        if not self.phases:
            return False
            
        # Check if we should transition to the next phase
        hp_percentage = self.hp / self.max_hp * 100
        
        for i, trigger in enumerate(self.phase_triggers):
            if hp_percentage <= trigger and i > self.current_phase:
                self.current_phase = i
                # Apply phase changes
                phase = self.phases[i]
                if "attack_patterns" in phase:
                    self.attack_patterns = phase["attack_patterns"]
                    self.current_pattern_index = 0
                if "attack_boost" in phase:
                    self.attack += phase["attack_boost"]
                if "defense_boost" in phase:
                    self.defense += phase["defense_boost"]
                if "message" in phase:
                    print_slow(phase["message"])
                    
                return True
                
        return False

class Location:
    def __init__(self, id: str, name: str, description: str, 
                 connections: Dict[str, str] = None,
                 enemies: List[str] = None,
                 items: List[str] = None,
                 npcs: List[str] = None,
                 is_beacon: bool = False,
                 map_art: str = None,
                 first_visit_text: str = None,
                 events: Dict = None):
        self.id = id
        self.name = name
        self.description = description
        self.connections = connections or {}  # Direction: location_id
        self.enemies = enemies or []  # List of enemy ids that can spawn here
        self.items = items or []  # List of item ids that can be found here
        self.npcs = npcs or []  # List of NPC ids that can be found here
        self.is_beacon = is_beacon
        self.map_art = map_art
        self.first_visit_text = first_visit_text
        self.events = events or {}  # Event triggers
        self.visited = False
    
    def get_description(self) -> str:
        """Get the location description."""
        return self.description
    
    def get_connections_string(self) -> str:
        """Get a string describing available exits."""
        if not self.connections:
            return "There are no obvious exits."
            
        exits = []
        for direction, _ in self.connections.items():
            exits.append(direction)
        
        return f"Exits: {', '.join(exits)}"
    
    def to_dict(self) -> Dict:
        """Convert location to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connections": self.connections,
            "enemies": self.enemies,
            "items": self.items,
            "npcs": self.npcs,
            "is_beacon": self.is_beacon,
            "map_art": self.map_art,
            "first_visit_text": self.first_visit_text,
            "events": self.events,
            "visited": self.visited
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        """Create a location from dictionary data."""
        location = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            connections=data["connections"],
            enemies=data["enemies"],
            items=data["items"],
            npcs=data["npcs"],
            is_beacon=data["is_beacon"],
            map_art=data["map_art"],
            first_visit_text=data["first_visit_text"],
            events=data["events"]
        )
        location.visited = data["visited"]
        return location

class NPC:
    def __init__(self, id: str, name: str, description: str, 
                 dialogue: Dict[str, Dict] = None,
                 quest: Dict = None,
                 shop_inventory: List[str] = None,
                 faction: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.dialogue = dialogue or {"default": {"text": "...", "options": {}}}
        self.current_dialogue = "default"
        self.quest = quest
        self.shop_inventory = shop_inventory or []
        self.faction = faction
        self.met = False
        self.relationship = 0  # -100 to 100
    
    def get_dialogue(self) -> Dict:
        """Get the current dialogue options."""
        return self.dialogue.get(self.current_dialogue, self.dialogue["default"])
    
    def talk(self) -> str:
        """Start a conversation with the NPC."""
        if not self.met:
            self.met = True
            return f"You meet {self.name} for the first time.\n{self.description}"
        
        return f"{self.name}: {self.get_dialogue()['text']}"
    
    def respond(self, option: str) -> str:
        """Respond to a dialogue option."""
        dialogue = self.get_dialogue()
        
        if option in dialogue["options"]:
            response = dialogue["options"][option]
            
            # Update dialogue state if needed
            if "next" in response:
                self.current_dialogue = response["next"]
            
            # Handle quest progression
            if "quest_progress" in response and self.quest:
                # Implement quest progression logic
                pass
            
            # Handle relationship changes
            if "relationship" in response:
                self.relationship += response["relationship"]
                
            return response["text"]
        
        return "Invalid response."
    
    def to_dict(self) -> Dict:
        """Convert NPC to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dialogue": self.dialogue,
            "current_dialogue": self.current_dialogue,
            "quest": self.quest,
            "shop_inventory": self.shop_inventory,
            "faction": self.faction,
            "met": self.met,
            "relationship": self.relationship
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        """Create an NPC from dictionary data."""
        npc = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            dialogue=data["dialogue"],
            quest=data["quest"],
            shop_inventory=data["shop_inventory"],
            faction=data["faction"]
        )
        npc.current_dialogue = data["current_dialogue"]
        npc.met = data["met"]
        npc.relationship = data["relationship"]
        return npc

class Player:
    def __init__(self, name: str, character_class: str, level: int = 1):
        self.name = name
        self.character_class = character_class
        self.level = level
        self.essence = 0  # Currency
        self.lost_essence = 0  # Lost on death
        self.lost_essence_location = None
        
        # Initialize stats based on class
        if character_class == "Warrior":
            self.max_hp = 100
            self.max_stamina = 80
            self.strength = 14
            self.dexterity = 9
            self.intelligence = 7
            self.faith = 8
            self.vitality = 12
            self.endurance = 10
        elif character_class == "Knight":
            self.max_hp = 90
            self.max_stamina = 90
            self.strength = 12
            self.dexterity = 12
            self.intelligence = 9
            self.faith = 11
            self.vitality = 10
            self.endurance = 11
        elif character_class == "Pyromancer":
            self.max_hp = 80
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 12
            self.faith = 14
            self.vitality = 8
            self.endurance = 9
        elif character_class == "Thief":
            self.max_hp = 75
            self.max_stamina = 100
            self.strength = 9
            self.dexterity = 14
            self.intelligence = 10
            self.faith = 8
            self.vitality = 9
            self.endurance = 14
        else:  # Default
            self.max_hp = 85
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 10
            self.faith = 10
            self.vitality = 10
            self.endurance = 10
        
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.inventory = []
        self.equipment = {
            "weapon": None,
            "shield": None,
            "armor": None,
            "ring1": None,
            "ring2": None,
            "amulet": None
        }
        self.estus_flask = {
            "current": 3,
            "max": 3
        }
        self.current_location = "highcastle_entrance"
        self.quests = {}
        self.discovered_locations = set()
        self.killed_enemies = {}
        self.stance = "balanced"  # balanced, aggressive, defensive
    
    def heal(self, amount: int) -> int:
        """Heal the player and return amount healed."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def restore_stamina(self, amount: int) -> int:
        """Restore stamina and return amount restored."""
        old_stamina = self.stamina
        self.stamina = min(self.max_stamina, self.stamina + amount)
        return self.stamina - old_stamina
    
    def use_estus(self) -> bool:
        """Use an estus flask charge to heal."""
        if self.estus_flask["current"] <= 0:
            return False
        
        self.estus_flask["current"] -= 1
        heal_amount = int(self.max_hp * 0.4)  # Heal 40% of max HP
        self.heal(heal_amount)
        return True
    
    def rest_at_beacon(self):
        """Rest at a beacon to restore HP, stamina, and estus."""
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.estus_flask["current"] = self.estus_flask["max"]
    
    def add_item(self, item: Item) -> bool:
        """Add an item to inventory. Return True if successful."""
        # Check if the item is stackable and exists in inventory
        if item.quantity > 1:
            for inv_item in self.inventory:
                if inv_item.id == item.id:
                    inv_item.quantity += item.quantity
                    return True
                    
        self.inventory.append(item)
        return True
    
    def remove_item(self, item: Item) -> bool:
        """Remove an item from inventory. Return True if successful."""
        for i, inv_item in enumerate(self.inventory):
            if inv_item.id == item.id:
                if inv_item.quantity > 1:
                    inv_item.quantity -= 1
                    return True
                else:
                    self.inventory.pop(i)
                    return True
        return False
    
    def equip_item(self, item: Item) -> str:
        """Equip an item. Return result message."""
        if not item.equippable:
            return f"You cannot equip {item.name}."
            
        # Determine equipment slot
        slot = None
        if item.item_type == "weapon":
            slot = "weapon"
        elif item.item_type == "shield":
            slot = "shield"
        elif item.item_type == "armor":
            slot = "armor"
        elif item.item_type == "ring":
            # Check if ring slots are available
            if self.equipment["ring1"] is None:
                slot = "ring1"
            elif self.equipment["ring2"] is None:
                slot = "ring2"
            else:
                return "You cannot equip more rings."
        elif item.item_type == "amulet":
            slot = "amulet"
        else:
            return f"Cannot equip {item.name}."
            
        # Unequip current item in that slot if any
        if self.equipment[slot] is not None:
            self.equipment[slot].equipped = False
            
        # Equip new item
        self.equipment[slot] = item
        item.equipped = True
        
        return f"You equipped {item.name}."
    
    def unequip_item(self, slot: str) -> str:
        """Unequip an item from specified slot. Return result message."""
        if slot not in self.equipment or self.equipment[slot] is None:
            return f"Nothing equipped in {slot}."
            
        item = self.equipment[slot]
        item.equipped = False
        self.equipment[slot] = None
        
        return f"You unequipped {item.name}."
    
    def get_attack_power(self) -> int:
        """Calculate the player's attack power."""
        base_attack = self.strength // 2
        
        if self.equipment["weapon"]:
            weapon_damage = self.equipment["weapon"].get_damage()
            # Apply stat scaling based on weapon type
            weapon_stats = self.equipment["weapon"].stats
            if "scaling" in weapon_stats:
                if weapon_stats["scaling"] == "strength":
                    scaling_bonus = self.strength // 3
                elif weapon_stats["scaling"] == "dexterity":
                    scaling_bonus = self.dexterity // 3
                else:
                    scaling_bonus = 0
                weapon_damage += scaling_bonus
            
            base_attack += weapon_damage
        
        # Apply stance modifiers
        if self.stance == "aggressive":
            base_attack = int(base_attack * 1.2)  # 20% more damage
        elif self.stance == "defensive":
            base_attack = int(base_attack * 0.8)  # 20% less damage
            
        return base_attack
    
    def get_defense(self) -> int:
        """Calculate the player's defense value."""
        base_defense = self.vitality // 2
        
        if self.equipment["armor"]:
            base_defense += self.equipment["armor"].stats["defense"]
            
        if self.equipment["shield"] and self.stance != "aggressive":
            base_defense += self.equipment["shield"].stats["defense"]
        
        # Apply stance modifiers
        if self.stance == "defensive":
            base_defense = int(base_defense * 1.2)  # 20% more defense
        elif self.stance == "aggressive":
            base_defense = int(base_defense * 0.8)  # 20% less defense
            
        return base_defense
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        defense = self.get_defense()
        
        # Apply resistances from equipment
        resistance_mult = 1.0
        for slot, item in self.equipment.items():
            if item and "resistance" in item.stats and damage_type in item.stats["resistance"]:
                resistance_mult -= item.stats["resistance"][damage_type] / 100.0
        
        # Ensure resistance multiplier is at least 0.2 (80% damage reduction max)
        resistance_mult = max(0.2, resistance_mult)
        
        # Calculate final damage
        damage = int(max(1, amount * resistance_mult - defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the player is dead."""
        return self.hp <= 0
    
    def die(self):
        """Handle player death."""
        # Drop essence at current location
        self.lost_essence = self.essence
        self.lost_essence_location = self.current_location
        self.essence = 0
        
        # Respawn at last beacon
        # This would be implemented in the game loop logic
    
    def recover_lost_essence(self):
        """Recover lost essence."""
        if self.lost_essence > 0:
            self.essence += self.lost_essence
            self.lost_essence = 0
            self.lost_essence_location = None
            return True
        return False
    
    def level_up(self, stat: str) -> bool:
        """Level up a stat. Return True if successful."""
        cost = self.calculate_level_cost()
        
        if self.essence < cost:
            return False
            
        self.essence -= cost
        self.level += 1
        
        # Increase the chosen stat
        if stat == "strength":
            self.strength += 1
        elif stat == "dexterity":
            self.dexterity += 1
        elif stat == "intelligence":
            self.intelligence += 1
        elif stat == "faith":
            self.faith += 1
        elif stat == "vitality":
            self.vitality += 1
            self.max_hp += 5
            self.hp += 5
        elif stat == "endurance":
            self.endurance += 1
            self.max_stamina += 5
            self.stamina += 5
        
        return True
    
    def calculate_level_cost(self) -> int:
        """Calculate the essence cost for the next level."""
        return int(100 * (1.1 ** (self.level - 1)))
    
    def use_item(self, item_index: int) -> str:
        """Use an item from inventory by index."""
        if item_index < 0 or item_index >= len(self.inventory):
            return "Invalid item index."
            
        item = self.inventory[item_index]
        
        if not item.usable:
            return f"You cannot use {item.name}."
            
        result = item.use(self)
        
        # Remove item if quantity reaches 0
        if item.quantity <= 0:
            self.inventory.pop(item_index)
            
        return result
    
    def change_stance(self, new_stance: str) -> str:
        """Change combat stance. Return result message."""
        valid_stances = ["balanced", "aggressive", "defensive"]
        
        if new_stance not in valid_stances:
            return f"Invalid stance. Choose from: {', '.join(valid_stances)}"
            
        old_stance = self.stance
        self.stance = new_stance
        
        return f"Changed stance from {old_stance} to {new_stance}."
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for saving."""
        return {
            "name": self.name,
            "character_class": self.character_class,
            "level": self.level,
            "essence": self.essence,
            "lost_essence": self.lost_essence,
            "lost_essence_location": self.lost_essence_location,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "max_stamina": self.max_stamina,
            "stamina": self.stamina,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "faith": self.faith,
            "vitality": self.vitality,
            "endurance": self.endurance,
            "inventory": [item.to_dict() for item in self.inventory],
            "equipment": {slot: (item.to_dict() if item else None) for slot, item in self.equipment.items()},
            "estus_flask": self.estus_flask,
            "current_location": self.current_location,
            "quests": self.quests,
            "discovered_locations": list(self.discovered_locations),
            "killed_enemies": self.killed_enemies,
            "stance": self.stance
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create a player from dictionary data."""
        player = cls(
            name=data["name"],
            character_class=data["character_class"],
            level=data["level"]
        )
        player.essence = data["essence"]
        player.lost_essence = data["lost_essence"]
        player.lost_essence_location = data["lost_essence_location"]
        player.max_hp = data["max_hp"]
        player.hp = data["hp"]
        player.max_stamina = data["max_stamina"]
        player.stamina = data["stamina"]
        player.strength = data["strength"]
        player.dexterity = data["dexterity"]
        player.intelligence = data["intelligence"]
        player.faith = data["faith"]
        player.vitality = data["vitality"]
        player.endurance = data["endurance"]
        
        # Reconstruct inventory
        player.inventory = []
        for item_data in data["inventory"]:
            if item_data["item_type"] == "weapon":
                item = Weapon(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    damage=item_data["stats"]["damage"],
                    damage_type=item_data["stats"]["damage_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    special_ability=item_data["stats"].get("special_ability"),
                    two_handed=item_data["stats"].get("two_handed", False)
                )
            elif item_data["item_type"] == "armor":
                item = Armor(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    defense=item_data["stats"]["defense"],
                    armor_type=item_data["stats"]["armor_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    resistance=item_data["stats"].get("resistance")
                )
            elif item_data["item_type"] == "consumable":
                item = Consumable(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    effect=item_data["stats"],
                    value=item_data["value"],
                    weight=item_data["weight"],
                    quantity=item_data["quantity"]
                )
            else:
                item = Item.from_dict(item_data)
                
            item.quantity = item_data["quantity"]
            item.equipped = item_data["equipped"]
            player.inventory.append(item)
        
        # Reconstruct equipment
        player.equipment = {slot: None for slot in player.equipment.keys()}
        for slot, item_data in data["equipment"].items():
            if item_data:
                for item in player.inventory:
                    if item.id == item_data["id"]:
                        player.equipment[slot] = item
                        break
                        
        player.estus_flask = data["estus_flask"]
        player.current_location = data["current_location"]
        player.quests = data["quests"]
        player.discovered_locations = set(data["discovered_locations"])
        player.killed_enemies = data["killed_enemies"]
        player.stance = data["stance"]
        
        return player

import os
import json
import time
import random
import pickle
import datetime
import platform
import sys
from typing import Dict, List, Optional, Tuple, Union, Any

# Constants
SAVE_DIR = "saves"
AUTOSAVE_FILE = os.path.join(SAVE_DIR, "autosave.sav")
VERSION = "1.0.0"

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# ASCII Art and UI Elements
TITLE_ART = """
  ╔═══════════════════════════════════════════════════════════╗
  ║  ▄████▄   ██▀███   █    ██  ███▄ ▄███▓ ▄▄▄▄    ██▓    ██▓ ║
  ║ ▒██▀ ▀█  ▓██ ▒ ██▒ ██  ▓██▒▓██▒▀█▀ ██▒▓█████▄ ▓██▒   ▓██▒ ║
  ║ ▒▓█    ▄ ▓██ ░▄█ ▒▓██  ▒██░▓██    ▓██░▒██▒ ▄██▒██░   ▒██░ ║
  ║ ▒▓▓▄ ▄██▒▒██▀▀█▄  ▓▓█  ░██░▒██    ▒██ ▒██░█▀  ▒██░   ▒██░ ║
  ║ ▒ ▓███▀ ░░██▓ ▒██▒▒▒█████▓ ▒██▒   ░██▒░▓█  ▀█▓░██████░██████╗
  ║ ░ ░▒ ▒  ░░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ░ ▒░   ░  ░░▒▓███▀▒░ ▒░▓  ░ ▒░▓  ║
  ║   ░  ▒     ░▒ ░ ▒░░░▒░ ░ ░ ░  ░      ░▒░▒   ░ ░ ░ ▒  ░ ░ ▒  ║
  ║ ░          ░░   ░  ░░░ ░ ░ ░      ░    ░    ░   ░ ░    ░ ░  ║
  ║ ░ ░         ░        ░            ░    ░          ░  ░   ░  ║
  ║                           ARDENVALE                        ║
  ╚═══════════════════════════════════════════════════════════╝
                A REALM SHATTERED BY A FADING FLAME
"""

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                      ARDENVALE                            ║
╚═══════════════════════════════════════════════════════════╝
"""

DIVIDER = "═" * 70

# Utility Functions
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
        
        return {
            "player_name": save_data["player"]["name"],
            "player_level": save_data["player"]["level"],
            "location": save_data["player"]["current_location"],
            "timestamp": save_data["timestamp"],
            "version": save_data["version"]
        }
    except Exception as e:
        return {
            "error": str(e),
            "filename": filename
        }

# Game Classes
class Item:
    def __init__(self, id: str, name: str, description: str, item_type: str, value: int = 0, 
                 weight: float = 0.0, stats: Dict = None, usable: bool = False, 
                 equippable: bool = False, quantity: int = 1):
        self.id = id
        self.name = name
        self.description = description
        self.item_type = item_type  # weapon, armor, consumable, key, etc.
        self.value = value
        self.weight = weight
        self.stats = stats or {}
        self.usable = usable
        self.equippable = equippable
        self.quantity = quantity
        self.equipped = False
    
    def use(self, player) -> str:
        """Use the item and return result message."""
        if not self.usable:
            return f"You cannot use the {self.name}."
        
        # Implement item usage logic here
        result = "You used the item, but nothing happened."
        
        # Example: Healing potion
        if self.item_type == "consumable" and "healing" in self.stats:
            heal_amount = self.stats["healing"]
            player.heal(heal_amount)
            result = f"You drink the {self.name} and recover {heal_amount} health."
            self.quantity -= 1
            
        return result
    
    def to_dict(self) -> Dict:
        """Convert item to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "value": self.value,
            "weight": self.weight,
            "stats": self.stats,
            "usable": self.usable,
            "equippable": self.equippable,
            "quantity": self.quantity,
            "equipped": self.equipped
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Create an item from dictionary data."""
        item = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=data["item_type"],
            value=data["value"],
            weight=data["weight"],
            stats=data["stats"],
            usable=data["usable"],
            equippable=data["equippable"],
            quantity=data["quantity"]
        )
        item.equipped = data["equipped"]
        return item

class Weapon(Item):
    def __init__(self, id: str, name: str, description: str, damage: int, 
                 damage_type: str, weight: float, value: int, 
                 special_ability: Dict = None, two_handed: bool = False):
        stats = {
            "damage": damage,
            "damage_type": damage_type,
            "two_handed": two_handed
        }
        if special_ability:
            stats["special_ability"] = special_ability
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="weapon",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )
    
    def get_damage(self) -> int:
        """Calculate the weapon's damage."""
        base_damage = self.stats["damage"]
        return base_damage
    
    def weapon_art(self, player, target) -> str:
        """Use the weapon's special ability."""
        if "special_ability" not in self.stats:
            return "This weapon has no special ability."
        
        ability = self.stats["special_ability"]
        # Implement weapon special ability logic
        
        return f"You use {ability['name']}!"

class Armor(Item):
    def __init__(self, id: str, name: str, description: str, defense: int, 
                 armor_type: str, weight: float, value: int, 
                 resistance: Dict = None):
        stats = {
            "defense": defense,
            "armor_type": armor_type,
        }
        if resistance:
            stats["resistance"] = resistance
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="armor",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )

class Consumable(Item):
    def __init__(self, id: str, name: str, description: str, effect: Dict, 
                 value: int, weight: float = 0.1, quantity: int = 1):
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="consumable",
            value=value,
            weight=weight,
            stats=effect,
            usable=True,
            equippable=False,
            quantity=quantity
        )

class Enemy:
    def __init__(self, id: str, name: str, description: str, level: int, 
                 hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.attack_patterns = attack_patterns or []
        self.loot_table = loot_table or []
        self.essence = essence
        self.weaknesses = weaknesses or []
        self.current_pattern_index = 0
    
    def get_next_attack(self) -> Dict:
        """Get the next attack pattern in sequence."""
        if not self.attack_patterns:
            return {"name": "Basic Attack", "damage": self.attack, "type": "physical"}
        
        pattern = self.attack_patterns[self.current_pattern_index]
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.attack_patterns)
        return pattern
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        # Apply weakness multipliers
        multiplier = 1.0
        if damage_type in self.weaknesses:
            multiplier = 1.5
            
        damage = int(max(1, amount * multiplier - self.defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the enemy is dead."""
        return self.hp <= 0
    
    def drop_loot(self) -> List[Item]:
        """Generate loot drops based on loot table."""
        drops = []
        for loot_entry in self.loot_table:
            if random.random() < loot_entry["chance"]:
                # Create the item from the item database
                item_id = loot_entry["item_id"]
                item = create_item(item_id)
                if item:
                    # Set quantity if specified
                    if "quantity" in loot_entry:
                        item.quantity = random.randint(
                            loot_entry["quantity"]["min"], 
                            loot_entry["quantity"]["max"]
                        )
                    drops.append(item)
        return drops
    
    def to_dict(self) -> Dict:
        """Convert enemy to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "attack_patterns": self.attack_patterns,
            "loot_table": self.loot_table,
            "essence": self.essence,
            "weaknesses": self.weaknesses,
            "current_pattern_index": self.current_pattern_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Enemy':
        """Create an enemy from dictionary data."""
        enemy = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            level=data["level"],
            hp=data["max_hp"],
            attack=data["attack"],
            defense=data["defense"],
            attack_patterns=data["attack_patterns"],
            loot_table=data["loot_table"],
            essence=data["essence"],
            weaknesses=data["weaknesses"]
        )
        enemy.hp = data["hp"]
        enemy.current_pattern_index = data["current_pattern_index"]
        return enemy

class Boss(Enemy):
    def __init__(self, id: str, name: str, title: str, description: str, 
                 level: int, hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None,
                 phases: List[Dict] = None):
        super().__init__(
            id=id,
            name=f"{name}, {title}",
            description=description,
            level=level,
            hp=hp,
            attack=attack,
            defense=defense,
            attack_patterns=attack_patterns,
            loot_table=loot_table,
            essence=essence,
            weaknesses=weaknesses
        )
        self.phases = phases or []
        self.current_phase = 0
        self.phase_triggers = [phase["trigger"] for phase in self.phases] if phases else []
    
    def update_phase(self) -> bool:
        """Check and update boss phase based on HP. Return True if phase changed."""
        if not self.phases:
            return False
            
        # Check if we should transition to the next phase
        hp_percentage = self.hp / self.max_hp * 100
        
        for i, trigger in enumerate(self.phase_triggers):
            if hp_percentage <= trigger and i > self.current_phase:
                self.current_phase = i
                # Apply phase changes
                phase = self.phases[i]
                if "attack_patterns" in phase:
                    self.attack_patterns = phase["attack_patterns"]
                    self.current_pattern_index = 0
                if "attack_boost" in phase:
                    self.attack += phase["attack_boost"]
                if "defense_boost" in phase:
                    self.defense += phase["defense_boost"]
                if "message" in phase:
                    print_slow(phase["message"])
                    
                return True
                
        return False

class Location:
    def __init__(self, id: str, name: str, description: str, 
                 connections: Dict[str, str] = None,
                 enemies: List[str] = None,
                 items: List[str] = None,
                 npcs: List[str] = None,
                 is_beacon: bool = False,
                 map_art: str = None,
                 first_visit_text: str = None,
                 events: Dict = None):
        self.id = id
        self.name = name
        self.description = description
        self.connections = connections or {}  # Direction: location_id
        self.enemies = enemies or []  # List of enemy ids that can spawn here
        self.items = items or []  # List of item ids that can be found here
        self.npcs = npcs or []  # List of NPC ids that can be found here
        self.is_beacon = is_beacon
        self.map_art = map_art
        self.first_visit_text = first_visit_text
        self.events = events or {}  # Event triggers
        self.visited = False
    
    def get_description(self) -> str:
        """Get the location description."""
        return self.description
    
    def get_connections_string(self) -> str:
        """Get a string describing available exits."""
        if not self.connections:
            return "There are no obvious exits."
            
        exits = []
        for direction, _ in self.connections.items():
            exits.append(direction)
        
        return f"Exits: {', '.join(exits)}"
    
    def to_dict(self) -> Dict:
        """Convert location to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connections": self.connections,
            "enemies": self.enemies,
            "items": self.items,
            "npcs": self.npcs,
            "is_beacon": self.is_beacon,
            "map_art": self.map_art,
            "first_visit_text": self.first_visit_text,
            "events": self.events,
            "visited": self.visited
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        """Create a location from dictionary data."""
        location = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            connections=data["connections"],
            enemies=data["enemies"],
            items=data["items"],
            npcs=data["npcs"],
            is_beacon=data["is_beacon"],
            map_art=data["map_art"],
            first_visit_text=data["first_visit_text"],
            events=data["events"]
        )
        location.visited = data["visited"]
        return location

class NPC:
    def __init__(self, id: str, name: str, description: str, 
                 dialogue: Dict[str, Dict] = None,
                 quest: Dict = None,
                 shop_inventory: List[str] = None,
                 faction: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.dialogue = dialogue or {"default": {"text": "...", "options": {}}}
        self.current_dialogue = "default"
        self.quest = quest
        self.shop_inventory = shop_inventory or []
        self.faction = faction
        self.met = False
        self.relationship = 0  # -100 to 100
    
    def get_dialogue(self) -> Dict:
        """Get the current dialogue options."""
        return self.dialogue.get(self.current_dialogue, self.dialogue["default"])
    
    def talk(self) -> str:
        """Start a conversation with the NPC."""
        if not self.met:
            self.met = True
            return f"You meet {self.name} for the first time.\n{self.description}"
        
        return f"{self.name}: {self.get_dialogue()['text']}"
    
    def respond(self, option: str) -> str:
        """Respond to a dialogue option."""
        dialogue = self.get_dialogue()
        
        if option in dialogue["options"]:
            response = dialogue["options"][option]
            
            # Update dialogue state if needed
            if "next" in response:
                self.current_dialogue = response["next"]
            
            # Handle quest progression
            if "quest_progress" in response and self.quest:
                # Implement quest progression logic
                pass
            
            # Handle relationship changes
            if "relationship" in response:
                self.relationship += response["relationship"]
                
            return response["text"]
        
        return "Invalid response."
    
    def to_dict(self) -> Dict:
        """Convert NPC to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dialogue": self.dialogue,
            "current_dialogue": self.current_dialogue,
            "quest": self.quest,
            "shop_inventory": self.shop_inventory,
            "faction": self.faction,
            "met": self.met,
            "relationship": self.relationship
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        """Create an NPC from dictionary data."""
        npc = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            dialogue=data["dialogue"],
            quest=data["quest"],
            shop_inventory=data["shop_inventory"],
            faction=data["faction"]
        )
        npc.current_dialogue = data["current_dialogue"]
        npc.met = data["met"]
        npc.relationship = data["relationship"]
        return npc

class Player:
    def __init__(self, name: str, character_class: str, level: int = 1):
        self.name = name
        self.character_class = character_class
        self.level = level
        self.essence = 0  # Currency
        self.lost_essence = 0  # Lost on death
        self.lost_essence_location = None
        
        # Initialize stats based on class
        if character_class == "Warrior":
            self.max_hp = 100
            self.max_stamina = 80
            self.strength = 14
            self.dexterity = 9
            self.intelligence = 7
            self.faith = 8
            self.vitality = 12
            self.endurance = 10
        elif character_class == "Knight":
            self.max_hp = 90
            self.max_stamina = 90
            self.strength = 12
            self.dexterity = 12
            self.intelligence = 9
            self.faith = 11
            self.vitality = 10
            self.endurance = 11
        elif character_class == "Pyromancer":
            self.max_hp = 80
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 12
            self.faith = 14
            self.vitality = 8
            self.endurance = 9
        elif character_class == "Thief":
            self.max_hp = 75
            self.max_stamina = 100
            self.strength = 9
            self.dexterity = 14
            self.intelligence = 10
            self.faith = 8
            self.vitality = 9
            self.endurance = 14
        else:  # Default
            self.max_hp = 85
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 10
            self.faith = 10
            self.vitality = 10
            self.endurance = 10
        
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.inventory = []
        self.equipment = {
            "weapon": None,
            "shield": None,
            "armor": None,
            "ring1": None,
            "ring2": None,
            "amulet": None
        }
        self.estus_flask = {
            "current": 3,
            "max": 3
        }
        self.current_location = "highcastle_entrance"
        self.quests = {}
        self.discovered_locations = set()
        self.killed_enemies = {}
        self.stance = "balanced"  # balanced, aggressive, defensive
    
    def heal(self, amount: int) -> int:
        """Heal the player and return amount healed."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def restore_stamina(self, amount: int) -> int:
        """Restore stamina and return amount restored."""
        old_stamina = self.stamina
        self.stamina = min(self.max_stamina, self.stamina + amount)
        return self.stamina - old_stamina
    
    def use_estus(self) -> bool:
        """Use an estus flask charge to heal."""
        if self.estus_flask["current"] <= 0:
            return False
        
        self.estus_flask["current"] -= 1
        heal_amount = int(self.max_hp * 0.4)  # Heal 40% of max HP
        self.heal(heal_amount)
        return True
    
    def rest_at_beacon(self):
        """Rest at a beacon to restore HP, stamina, and estus."""
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.estus_flask["current"] = self.estus_flask["max"]
    
    def add_item(self, item: Item) -> bool:
        """Add an item to inventory. Return True if successful."""
        # Check if the item is stackable and exists in inventory
        if item.quantity > 1:
            for inv_item in self.inventory:
                if inv_item.id == item.id:
                    inv_item.quantity += item.quantity
                    return True
                    
        self.inventory.append(item)
        return True
    
    def remove_item(self, item: Item) -> bool:
        """Remove an item from inventory. Return True if successful."""
        for i, inv_item in enumerate(self.inventory):
            if inv_item.id == item.id:
                if inv_item.quantity > 1:
                    inv_item.quantity -= 1
                    return True
                else:
                    self.inventory.pop(i)
                    return True
        return False
    
    def equip_item(self, item: Item) -> str:
        """Equip an item. Return result message."""
        if not item.equippable:
            return f"You cannot equip {item.name}."
            
        # Determine equipment slot
        slot = None
        if item.item_type == "weapon":
            slot = "weapon"
        elif item.item_type == "shield":
            slot = "shield"
        elif item.item_type == "armor":
            slot = "armor"
        elif item.item_type == "ring":
            # Check if ring slots are available
            if self.equipment["ring1"] is None:
                slot = "ring1"
            elif self.equipment["ring2"] is None:
                slot = "ring2"
            else:
                return "You cannot equip more rings."
        elif item.item_type == "amulet":
            slot = "amulet"
        else:
            return f"Cannot equip {item.name}."
            
        # Unequip current item in that slot if any
        if self.equipment[slot] is not None:
            self.equipment[slot].equipped = False
            
        # Equip new item
        self.equipment[slot] = item
        item.equipped = True
        
        return f"You equipped {item.name}."
    
    def unequip_item(self, slot: str) -> str:
        """Unequip an item from specified slot. Return result message."""
        if slot not in self.equipment or self.equipment[slot] is None:
            return f"Nothing equipped in {slot}."
            
        item = self.equipment[slot]
        item.equipped = False
        self.equipment[slot] = None
        
        return f"You unequipped {item.name}."
    
    def get_attack_power(self) -> int:
        """Calculate the player's attack power."""
        base_attack = self.strength // 2
        
        if self.equipment["weapon"]:
            weapon_damage = self.equipment["weapon"].get_damage()
            # Apply stat scaling based on weapon type
            weapon_stats = self.equipment["weapon"].stats
            if "scaling" in weapon_stats:
                if weapon_stats["scaling"] == "strength":
                    scaling_bonus = self.strength // 3
                elif weapon_stats["scaling"] == "dexterity":
                    scaling_bonus = self.dexterity // 3
                else:
                    scaling_bonus = 0
                weapon_damage += scaling_bonus
            
            base_attack += weapon_damage
        
        # Apply stance modifiers
        if self.stance == "aggressive":
            base_attack = int(base_attack * 1.2)  # 20% more damage
        elif self.stance == "defensive":
            base_attack = int(base_attack * 0.8)  # 20% less damage
            
        return base_attack
    
    def get_defense(self) -> int:
        """Calculate the player's defense value."""
        base_defense = self.vitality // 2
        
        if self.equipment["armor"]:
            base_defense += self.equipment["armor"].stats["defense"]
            
        if self.equipment["shield"] and self.stance != "aggressive":
            base_defense += self.equipment["shield"].stats["defense"]
        
        # Apply stance modifiers
        if self.stance == "defensive":
            base_defense = int(base_defense * 1.2)  # 20% more defense
        elif self.stance == "aggressive":
            base_defense = int(base_defense * 0.8)  # 20% less defense
            
        return base_defense
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        defense = self.get_defense()
        
        # Apply resistances from equipment
        resistance_mult = 1.0
        for slot, item in self.equipment.items():
            if item and "resistance" in item.stats and damage_type in item.stats["resistance"]:
                resistance_mult -= item.stats["resistance"][damage_type] / 100.0
        
        # Ensure resistance multiplier is at least 0.2 (80% damage reduction max)
        resistance_mult = max(0.2, resistance_mult)
        
        # Calculate final damage
        damage = int(max(1, amount * resistance_mult - defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the player is dead."""
        return self.hp <= 0
    
    def die(self):
        """Handle player death."""
        # Drop essence at current location
        self.lost_essence = self.essence
        self.lost_essence_location = self.current_location
        self.essence = 0
        
        # Respawn at last beacon
        # This would be implemented in the game loop logic
    
    def recover_lost_essence(self):
        """Recover lost essence."""
        if self.lost_essence > 0:
            self.essence += self.lost_essence
            self.lost_essence = 0
            self.lost_essence_location = None
            return True
        return False
    
    def level_up(self, stat: str) -> bool:
        """Level up a stat. Return True if successful."""
        cost = self.calculate_level_cost()
        
        if self.essence < cost:
            return False
            
        self.essence -= cost
        self.level += 1
        
        # Increase the chosen stat
        if stat == "strength":
            self.strength += 1
        elif stat == "dexterity":
            self.dexterity += 1
        elif stat == "intelligence":
            self.intelligence += 1
        elif stat == "faith":
            self.faith += 1
        elif stat == "vitality":
            self.vitality += 1
            self.max_hp += 5
            self.hp += 5
        elif stat == "endurance":
            self.endurance += 1
            self.max_stamina += 5
            self.stamina += 5
        
        return True
    
    def calculate_level_cost(self) -> int:
        """Calculate the essence cost for the next level."""
        return int(100 * (1.1 ** (self.level - 1)))
    
    def use_item(self, item_index: int) -> str:
        """Use an item from inventory by index."""
        if item_index < 0 or item_index >= len(self.inventory):
            return "Invalid item index."
            
        item = self.inventory[item_index]
        
        if not item.usable:
            return f"You cannot use {item.name}."
            
        result = item.use(self)
        
        # Remove item if quantity reaches 0
        if item.quantity <= 0:
            self.inventory.pop(item_index)
            
        return result
    
    def change_stance(self, new_stance: str) -> str:
        """Change combat stance. Return result message."""
        valid_stances = ["balanced", "aggressive", "defensive"]
        
        if new_stance not in valid_stances:
            return f"Invalid stance. Choose from: {', '.join(valid_stances)}"
            
        old_stance = self.stance
        self.stance = new_stance
        
        return f"Changed stance from {old_stance} to {new_stance}."
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for saving."""
        return {
            "name": self.name,
            "character_class": self.character_class,
            "level": self.level,
            "essence": self.essence,
            "lost_essence": self.lost_essence,
            "lost_essence_location": self.lost_essence_location,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "max_stamina": self.max_stamina,
            "stamina": self.stamina,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "faith": self.faith,
            "vitality": self.vitality,
            "endurance": self.endurance,
            "inventory": [item.to_dict() for item in self.inventory],
            "equipment": {slot: (item.to_dict() if item else None) for slot, item in self.equipment.items()},
            "estus_flask": self.estus_flask,
            "current_location": self.current_location,
            "quests": self.quests,
            "discovered_locations": list(self.discovered_locations),
            "killed_enemies": self.killed_enemies,
            "stance": self.stance
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create a player from dictionary data."""
        player = cls(
            name=data["name"],
            character_class=data["character_class"],
            level=data["level"]
        )
        player.essence = data["essence"]
        player.lost_essence = data["lost_essence"]
        player.lost_essence_location = data["lost_essence_location"]
        player.max_hp = data["max_hp"]
        player.hp = data["hp"]
        player.max_stamina = data["max_stamina"]
        player.stamina = data["stamina"]
        player.strength = data["strength"]
        player.dexterity = data["dexterity"]
        player.intelligence = data["intelligence"]
        player.faith = data["faith"]
        player.vitality = data["vitality"]
        player.endurance = data["endurance"]
        
        # Reconstruct inventory
        player.inventory = []
        for item_data in data["inventory"]:
            if item_data["item_type"] == "weapon":
                item = Weapon(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    damage=item_data["stats"]["damage"],
                    damage_type=item_data["stats"]["damage_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    special_ability=item_data["stats"].get("special_ability"),
                    two_handed=item_data["stats"].get("two_handed", False)
                )
            elif item_data["item_type"] == "armor":
                item = Armor(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    defense=item_data["stats"]["defense"],
                    armor_type=item_data["stats"]["armor_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    resistance=item_data["stats"].get("resistance")
                )
            elif item_data["item_type"] == "consumable":
                item = Consumable(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    effect=item_data["stats"],
                    value=item_data["value"],
                    weight=item_data["weight"],
                    quantity=item_data["quantity"]
                )
            else:
                item = Item.from_dict(item_data)
                
            item.quantity = item_data["quantity"]
            item.equipped = item_data["equipped"]
            player.inventory.append(item)
        
        # Reconstruct equipment
        player.equipment = {slot: None for slot in player.equipment.keys()}
        for slot, item_data in data["equipment"].items():
            if item_data:
                for item in player.inventory:
                    if item.id == item_data["id"]:
                        player.equipment[slot] = item
                        break
                        
        player.estus_flask = data["estus_flask"]
        player.current_location = data["current_location"]
        player.quests = data["quests"]
        player.discovered_locations = set(data["discovered_locations"])
        player.killed_enemies = data["killed_enemies"]
        player.stance = data["stance"]
        
        return player

class World:
    def __init__(self):
        self.locations = {}
        self.npcs = {}
        self.items = {}
        self.enemies = {}
        self.bosses = {}
        self.quests = {}
        self.active_events = set()
        self.game_state = {}
        
        # Initialize world components
        self.initialize_world()
    
    def initialize_world(self):
        """Initialize and load all world data."""
        self.load_locations()
        self.load_npcs()
        self.load_items()
        self.load_enemies()
        self.load_bosses()
        self.load_quests()
    
    def load_locations(self):
        """Load all location data."""
        # Highcastle Region
        self.locations["highcastle_entrance"] = Location(
            id="highcastle_entrance",
            name="Highcastle Gate",
            description="The towering gates of Highcastle stand before you, worn by time but still majestic. The once-bustling gatehouse is now quiet, with only a few guards maintaining their eternal vigil.",
            connections={
                "north": "highcastle_plaza",
                "east": "eastern_road",
                "west": "western_path"
            },
            enemies=["wandering_hollow", "fallen_knight"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Gate
       v S       o - You
  
  #################
  #####.....######
  ####...o...#####
  ###.........####
  ##.....+.....###
  #...............
  #...............
            """,
            first_visit_text="You arrive at the once-grand entrance to Highcastle, the last bastion of humanity in these dark times. The walls, though weathered, still stand tall against the encroaching darkness that has consumed much of Ardenvale."
        )
        
        self.locations["highcastle_plaza"] = Location(
            id="highcastle_plaza",
            name="Highcastle Central Plaza",
            description="The central plaza of Highcastle is a shadow of its former glory. Cracked fountains and weathered statues are silent witnesses to a time of prosperity long gone. A few desperate souls still wander here, clinging to routines of a life that no longer exists.",
            connections={
                "north": "highcastle_cathedral",
                "east": "eastern_district",
                "west": "western_district",
                "south": "highcastle_entrance"
            },
            enemies=["hollow_citizen", "corrupted_guard"],
            npcs=["andre_smith", "merchant_ulrich"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ###+######+####
  #...........+.#
  #.....o.......#
  #...#...#...#.#
  #.............#
  #...#...#...#.#
  ###....+....###
            """
        )
        
        self.locations["highcastle_cathedral"] = Location(
            id="highcastle_cathedral",
            name="Cathedral of the Fading Light",
            description="This once-magnificent cathedral now stands in partial ruin. Shafts of light pierce through holes in the ceiling, illuminating dust-covered pews and crumbling statues of forgotten deities. Despite its state, there is still an aura of reverence here.",
            connections={
                "south": "highcastle_plaza",
                "east": "cathedral_tower"
            },
            enemies=["cathedral_knight", "deacon_of_the_deep"],
            npcs=["sister_friede"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ########+######
  #..#.......#..#
  #...........+.#
  #.............#
  #....o........#
  #.....###.....#
  ##....+....####
            """
        )
        
        # Ashen Woods Region
        self.locations["western_path"] = Location(
            id="western_path",
            name="Western Path",
            description="A winding path leads westward from Highcastle. Once a well-traveled trade route, it is now overgrown and dangerous. The trees along the path seem to lean inward, as if watching passersby with malicious intent.",
            connections={
                "east": "highcastle_entrance",
                "west": "ashen_woods_entrance"
            },
            enemies=["wild_beast", "hollow_woodsman"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     % - Trees
       |         ~ - Water
       v S       o - You
  
  %%%%%%%%%%%    
  %%%..........
  %%%...o......
  %%%...........
  %%%...........
  %%%.......%%%%
  %%%%%%%%%%%    
            """
        )
        
        self.locations["ashen_woods_entrance"] = Location(
            id="ashen_woods_entrance",
            name="Ashen Woods Entrance",
            description="The entrance to the Ashen Woods is marked by a sudden change in the landscape. The trees here are grey and lifeless, their bark turned to ash. Wisps of smoke rise from the ground, though there is no fire to be seen.",
            connections={
                "east": "western_path",
                "west": "ashen_woods_clearing"
            },
            enemies=["ember_wolf", "ashen_treant"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         % - Trees
  W <----> E     ^ - Ash trees
       |         ~ - Water
       v S       o - You
  
  ^^^^^^^^^^^^^^
  ^^.....^^^.^^^
  ^.......o...^^
  ^............^
  ^^^..........^
  ^^^^^^^^^^^^^^
  ^^^^^^^^^^^^^^
            """
        )
        
        # Add more locations as needed...
    
    def load_npcs(self):
        """Load all NPC data."""
        self.npcs["andre_smith"] = NPC(
            id="andre_smith",
            name="Andre the Smith",
            description="A muscular blacksmith with arms like tree trunks. Despite the dark times, his eyes still hold a passionate fire for his craft. His hammer strikes rhythmically in the background.",
            dialogue={
                "default": {
                    "text": "Need something forged? Or perhaps an upgrade to that weapon of yours?",
                    "options": {
                        "1": {
                            "text": "I'd like to upgrade my weapon.",
                            "next": "upgrade"
                        },
                        "2": {
                            "text": "Tell me about yourself.",
                            "next": "about"
                        },
                        "3": {
                            "text": "What happened to this place?",
                            "next": "history"
                        },
                        "4": {
                            "text": "Do you have any work for me?",
                            "next": "quest"
                        }
                    }
                },
                "upgrade": {
                    "text": "Ah, let me see what you've got. I can work with most materials, given enough time and the right components.",
                    "options": {
                        "1": {
                            "text": "What materials do you need?",
                            "next": "materials"
                        },
                        "2": {
                            "text": "Actually, let's talk about something else.",
                            "next": "default"
                        }
                    }
                },
                "materials": {
                    "text": "For basic reinforcement, I need titanite shards. For special weapons, I might need ember essence from the Ashen Woods, or perhaps something more exotic. Bring me materials, and I'll see what I can do.",
                    "options": {
                        "1": {
                            "text": "I'll keep an eye out for those.",
                            "next": "default"
                        }
                    }
                },
                "about": {
                    "text": "Been a smith all my life. Learned from my father, who learned from his. I've seen kingdoms rise and fall, but the forge remains. As long as there are warriors who need weapons, I'll be here.",
                    "options": {
                        "1": {
                            "text": "How have you survived the hollowing?",
                            "next": "survived"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "survived": {
                    "text": "Purpose, friend. Those who hollow are those who've lost their purpose. As long as I have my hammer and anvil, I have a reason to keep going. Find your purpose, and you'll never hollow.",
                    "options": {
                        "1": {
                            "text": "That's profound wisdom.",
                            "next": "default",
                            "relationship": 5
                        }
                    }
                },
                "history": {
                    "text": "Highcastle was once the jewel of Ardenvale. When the First Flame began to fade, everything changed. The corruption spread, people hollowed, and darkness crept in. But we endure. We always do.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the First Flame.",
                            "next": "first_flame"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "first_flame": {
                    "text": "The First Flame is what brought light and disparity to our world. Heat and cold, life and death, light and dark... all because of the Flame. Now it fades, and the balance tips toward darkness. Some seek to rekindle it, others to usher in an Age of Dark. Me? I just forge.",
                    "options": {
                        "1": {
                            "text": "Can the Flame be rekindled?",
                            "next": "rekindle"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "rekindle": {
                    "text": "The old legends say it can, but at a cost. Great souls must be sacrificed to feed the Flame. The King... they say he sought another way, and look where that got us. But who knows? Maybe you'll find answers where others failed.",
                    "options": {
                        "1": {
                            "text": "I'll discover the truth.",
                            "next": "default"
                        }
                    }
                },
                "quest": {
                    "text": "As a matter of fact, I do. My old forge has run cold without proper ember. If you could venture to the Ashen Woods and bring back some ember essence, I could craft you something special.",
                    "options": {
                        "1": {
                            "text": "I'll find this ember essence for you.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "That sounds too dangerous.",
                            "next": "quest_decline"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Excellent! Look for it near what they call Ember Lake, deep in the Ashen Woods. The essence glows like a captured sunset. Careful though, the woods have grown wild and hostile since the Flame began to fade.",
                    "options": {
                        "1": {
                            "text": "I'll be careful.",
                            "next": "default",
                            "quest_progress": {"start": "ember_quest"}
                        }
                    }
                },
                "quest_decline": {
                    "text": "Fair enough. It's no small task. The offer stands if you change your mind.",
                    "options": {
                        "1": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_complete": {
                    "text": "By the Flame, you actually found it! This ember essence is perfect. Give me some time, and I'll forge you something worthy of your courage.",
                    "options": {
                        "1": {
                            "text": "Thank you, Andre.",
                            "next": "reward"
                        }
                    }
                },
                "reward": {
                    "text": "Here, take this blade. I call it the Flamebrand. The ember essence is forged into its very core. May it serve you well in the darkness ahead.",
                    "options": {
                        "1": {
                            "text": "It's beautiful. Thank you.",
                            "next": "default",
                            "quest_progress": {"complete": "ember_quest"}
                        }
                    }
                }
            },
            quest={
                "id": "ember_quest",
                "name": "The Smith's Request",
                "description": "Andre needs ember essence from the Ashen Woods to rekindle his forge.",
                "objectives": [
                    {"type": "item", "target": "ember_essence", "quantity": 1}
                ],
                "rewards": {
                    "item": "flamebrand",
                    "essence": 200
                }
            },
            shop_inventory=["reinforced_sword", "knight_shield", "ember"]
        )
        
        self.npcs["merchant_ulrich"] = NPC(
            id="merchant_ulrich",
            name="Merchant Ulrich",
            description="A hunched man with a perpetual nervous twitch. His eyes dart about constantly, and his fingers fidget with the hem of his tattered cloak. Despite his appearance, he has somehow managed to maintain a stock of rare goods.",
            dialogue={
                "default": {
                    "text": "Ah, a customer! Rare sight these days. Looking to trade? I've got wares from all corners of Ardenvale, before... well, before everything went to ruin.",
                    "options": {
                        "1": {
                            "text": "Show me what you have for sale.",
                            "next": "shop"
                        },
                        "2": {
                            "text": "Any rumors lately?",
                            "next": "rumors"
                        },
                        "3": {
                            "text": "How do you get your merchandise?",
                            "next": "merchandise"
                        },
                        "4": {
                            "text": "I'm looking for something specific.",
                            "next": "quest_intro"
                        }
                    }
                },
                "shop": {
                    "text": "Take a look, take a look! Fine goods at reasonable prices. Well, reasonable considering the state of the world.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "rumors": {
                    "text": "Rumors? Oh, I hear many things... They say the old king still wanders the Ringed Citadel, hollowed but retaining a fragment of his former self. And in the Ashen Woods, the tree shepherds have gone mad, attacking any who venture too deep.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the king.",
                            "next": "king"
                        },
                        "2": {
                            "text": "What are tree shepherds?",
                            "next": "shepherds"
                        },
                        "3": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "king": {
                    "text": "King Morgaeth was a wise ruler, once. They say he delved too deep into forbidden arts in his quest to save the kingdom from the fading of the Flame. Now he's neither dead nor truly alive... a hollow shell of royalty.",
                    "options": {
                        "1": {
                            "text": "What forbidden arts did he study?",
                            "next": "forbidden_arts"
                        },
                        "2": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        }
                    }
                },
                "forbidden_arts": {
                    "text": "They say he sought to draw power from the Abyss itself. To use darkness to preserve light, if you can imagine such madness. The royal archives might hold more answers, but none dare venture to the Ringed Citadel now.",
                    "options": {
                        "1": {
                            "text": "Interesting. Thank you for the information.",
                            "next": "default",
                            "quest_progress": {"hint": "kings_fall"}
                        }
                    }
                },
                "shepherds": {
                    "text": "Ancient creatures, like walking trees but with awareness. They tended the forests for millennia in peace. The corruption has twisted them, made them violent. A shame. They were magnificent beings.",
                    "options": {
                        "1": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "merchandise": {
                    "text": "Ah, professional secrets! *winks nervously* Let's just say I have... arrangements with certain brave souls who venture where others fear to tread. They bring me goods, I give them essence, everyone profits!",
                    "options": {
                        "1": {
                            "text": "Sounds dangerous.",
                            "next": "dangerous"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dangerous": {
                    "text": "Dangerous? *laughs shakily* My friend, everything is dangerous now. At least my suppliers choose their danger. Most of them return... some of the time.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "quest_intro": {
                    "text": "Something specific? *eyes narrow with interest* I might have what you need, or know where to find it. What are you looking for?",
                    "options": {
                        "1": {
                            "text": "I need access to the Ringed Citadel.",
                            "next": "quest_citadel"
                        },
                        "2": {
                            "text": "Just browsing, actually.",
                            "next": "default"
                        }
                    }
                },
                "quest_citadel": {
                    "text": "*lowers voice* The Citadel? Not many seek to go there willingly. *glances around nervously* I might know of a way, but it will cost you. Not just essence, but a favor.",
                    "options": {
                        "1": {
                            "text": "What kind of favor?",
                            "next": "quest_details"
                        },
                        "2": {
                            "text": "Never mind, too risky.",
                            "next": "default"
                        }
                    }
                },
                "quest_details": {
                    "text": "One of my suppliers ventured into the Blighted Marshes east of here. Never returned. Carried a signet ring I need back. Find it, and I'll give you what you need to enter the Citadel.",
                    "options": {
                        "1": {
                            "text": "I'll find your ring.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Good, good. The marshes are treacherous, but look for a broken cart near the eastern path. That's where my supplier was headed. The ring has a blue stone, can't miss it.",
                    "options": {
                        "1": {
                            "text": "I'll return when I have it.",
                            "next": "default",
                            "quest_progress": {"start": "signet_quest"}
                        }
                    }
                },
                "quest_complete": {
                    "*eyes widen* You found it! And lived to tell the tale! I'm impressed. As promised, here's what you need—a royal seal. It will grant you passage through the outer gates of the Ringed Citadel.",
                    "options": {
                        "1": {
                            "text": "Thank you for your help.",
                            "next": "default",
                            "quest_progress": {"complete": "signet_quest"}
                        }
                    }
                }
            },
            quest={
                "id": "signet_quest",
                "name": "The Merchant's Signet",
                "description": "Find Ulrich's missing signet ring in the Blighted Marshes.",
                "objectives": [
                    {"type": "item", "target": "blue_signet", "quantity": 1}
                ],
                "rewards": {
                    "item": "royal_seal",
                    "essence": 300
                }
            },
            shop_inventory=["estus_shard", "life_gem", "homeward_bone", "green_blossom"]
        )
        
        self.npcs["sister_friede"] = NPC(
            id="sister_friede",
            name="Sister Friede",
            description="A tall, slender woman in white robes that seem untouched by the grime and decay around her. Her face is partially obscured by a hood, but you can see her pale skin and piercing blue eyes. She moves with eerie grace.",
            dialogue={
                "default": {
                    "text": "Ashen One, why do you disturb this sanctuary? This is a place of quiet reflection, not for those who would perpetuate a doomed cycle.",
                    "options": {
                        "1": {
                            "text": "I seek guidance.",
                            "next": "guidance"
                        },
                        "2": {
                            "text": "What cycle do you speak of?",
                            "next": "cycle"
                        },
                        "3": {
                            "text": "Who are you?",
                            "next": "identity"
                        },
                        "4": {
                            "text": "Are you in danger here?",
                            "next": "quest_intro"
                        }
                    }
                },
                "guidance": {
                    "text": "Guidance? *soft laugh* The path ahead is shrouded for all of us. But if you must continue your journey, seek the depths of the Ashen Woods. There lies an ancient tree shepherd who remembers the time before corruption. His wisdom may aid you, if he doesn't kill you first.",
                    "options": {
                        "1": {
                            "text": "Thank you for the information.",
                            "next": "default"
                        },
                        "2": {
                            "text": "Why would he help me?",
                            "next": "help"
                        }
                    }
                },
                "help": {
                    "text": "He wouldn't, not willingly. But in his madness, truths slip out between attempts to end your life. Listen carefully... if you survive long enough to hear anything at all.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "cycle": {
                    "text": "The endless cycle of Light and Dark. For eons, the First Flame has been rekindled when it begins to fade, postponing the Age of Dark that is our birthright. Each rekindling only makes the inevitable collapse more devastating.",
                    "options": {
                        "1": {
                            "text": "You want the Flame to fade?",
                            "next": "fade"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "fade": {
                    "text": "*her eyes narrow slightly* I want what is natural. All fires eventually burn out. Fighting this truth has brought us to this state of perpetual decay. Let it end, and something new may begin.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "identity": {
                    "text": "I am simply a watcher. I've seen kingdoms rise and fall, flames kindle and fade. Now I wait here, in this broken cathedral, observing the final gasps of a dying age.",
                    "options": {
                        "1": {
                            "text": "You speak as if you're ancient.",
                            "next": "ancient"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "ancient": {
                    "text": "*she smiles enigmatically* Time loses meaning when you've witnessed enough cycles. But enough about me. What will you do, Ashen One? Perpetuate this dying world, or help usher in something new?",
                    "options": {
                        "1": {
                            "text": "I'll restore the Flame.",
                            "next": "restore",
                            "relationship": -10
                        },
                        "2": {
                            "text": "Perhaps the Dark should have its time.",
                            "next": "dark",
                            "relationship": 10
                        },
                        "3": {
                            "text": "I haven't decided yet.",
                            "next": "undecided"
                        }
                    }
                },
                "restore": {
                    "text": "*her expression hardens* Then you are no different from the others. Go your way, Ashen One. May you find what you seek... and understand its true cost.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dark": {
                    "text": "*she studies you with new interest* Perhaps there is wisdom in you after all. The Dark is not to be feared, but embraced as part of the natural order. Remember this when your resolve is tested.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "undecided": {
                    "text": "Indecision is... understandable. The weight of such choices is immense. Reflect carefully, Ashen One. Not all is as it seems in Ardenvale.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "quest_intro": {
                    "*she seems surprised by your concern* No, not from the hollowed ones. They avoid this place. But there is a matter that... troubles me. The cathedral's sacred chalice has been stolen, taken to the bell tower by one who has fallen far from grace.",
                    "options": {
                        "1": {
                            "text": "I could retrieve it for you.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "Why is the chalice important?",
                            "next": "chalice_importance"
                        }
                    }
                },
                "chalice_importance": {
                    "text": "It contains old knowledge, symbols of both light and dark in perfect balance. In the wrong hands, this knowledge could upset the natural order, prolong this agonizing age of transition.",
                    "options": {
                        "1": {
                            "text": "I'll retrieve the chalice.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Your offer is... unexpected. The thief is a former deacon, now corrupted beyond recognition. Ascend to the bell tower, but be wary—he will not surrender the chalice willingly.",
                    "options": {
                        "1": {
                            "text": "I'll be careful.",
                            "next": "default",
                            "quest_progress": {"start": "chalice_quest"}
                        }
                    }
                },
                "quest_complete": {
                    "*her eyes widen slightly as you present the chalice* You succeeded where others would have failed. The balance is preserved, for now. Please, take this talisman as a token of my... gratitude. It bears an old symbol of the dark.",
                    "options": {
                        "1": {
                            "text": "Thank you, Sister Friede.",
                            "next": "default",
                            "quest_progress": {"complete": "chalice_quest"},
                            "relationship": 15
                        }
                    }
                }
            },
            quest={
                "id": "chalice_quest",
                "name": "The Sacred Chalice",
                "description": "Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
                "objectives": [
                    {"type": "item", "target": "sacred_chalice", "quantity": 1}
                ],
                "rewards": {
                    "item": "dark_talisman",
                    "essence": 350,
                    "faction": "Children of Dark",
                    "reputation": 15
                }
            },
            faction="Children of Dark"
        )
    
    def load_items(self):
        """Load all item data."""
        # Weapons
        self.items["reinforced_sword"] = Weapon(
            id="reinforced_sword",
            name="Reinforced Longsword",
            description="A sturdy longsword with reinforced steel. Reliable and well-balanced.",
            damage=15,
            damage_type="physical",
            weight=3.0,
            value=200,
            two_handed=False
        )
        
        self.items["knight_sword"] = Weapon(
            id="knight_sword",
            name="Knight's Sword",
            description="A well-crafted sword used by the knights of Highcastle. The blade bears the insignia of the royal guard.",
            damage=18,
            damage_type="physical",
            weight=3.5,
            value=300,
            two_handed=False
        )
        
        self.items["woodsman_axe"] = Weapon(
            id="woodsman_axe",
            name="Woodsman's Axe",
            description="A heavy axe used for chopping wood, now repurposed as a weapon. Slow but powerful.",
            damage=22,
            damage_type="physical",
            weight=4.5,
            value=180,
            two_handed=True
        )
        
        self.items["cathedral_greatsword"] = Weapon(
            id="cathedral_greatsword",
            name="Cathedral Greatsword",
            description="A massive sword wielded by the knights of the cathedral. Holy symbols are etched into the blade.",
            damage=26,
            damage_type="physical",
            weight=6.0,
            value=450,
            two_handed=True,
            special_ability={"name": "Holy Light", "damage": 15, "type": "holy"}
        )
        
        self.items["ember_blade"] = Weapon(
            id="ember_blade",
            name="Ember Blade",
            description="A sword forged in the heart of the Ashen Woods. The blade seems to smolder with inner heat.",
            damage=20,
            damage_type="fire",
            weight=3.0,
            value=500,
            two_handed=False,
            special_ability={"name": "Ignite", "damage": 12, "type": "fire", "duration": 3}
        )
        
        self.items["vordt_mace"] = Weapon(
            id="vordt_mace",
            name="Vordt's Frostmace",
            description="A massive mace once wielded by Vordt, Guardian of the Frost Gate. Crystals of ice form along its surface.",
            damage=30,
            damage_type="physical",
            weight=8.0,
            value=700,
            two_handed=True,
            special_ability={"name": "Frost Strike", "damage": 20, "type": "ice", "slow_effect": True}
        )
        
        self.items["kings_greatsword"] = Weapon(
            id="kings_greatsword",
            name="King's Greatsword",
            description="The royal greatsword of King Morgaeth, now tainted with dark energy. It pulses with corrupted power.",
            damage=35,
            damage_type="physical",
            weight=7.0,
            value=1000,
            two_handed=True,
            special_ability={"name": "Royal Wrath", "damage": 40, "type": "dark", "cooldown": 5}
        )
        
        # Armor
        self.items["knight_helm"] = Armor(
            id="knight_helm",
            name="Knight's Helm",
            description="A standard helmet worn by the knights of Highcastle. Provides good protection but limits visibility.",
            defense=10,
            armor_type="head",
            weight=2.0,
            value=200
        )
        
        self.items["knight_shield"] = Armor(
            id="knight_shield",
            name="Knight's Shield",
            description="A sturdy kite shield bearing the crest of Highcastle. Well-balanced for both defense and mobility.",
            defense=15,
            armor_type="shield",
            weight=3.5,
            value=250
        )
        
        self.items["rusted_shield"] = Armor(
            id="rusted_shield",
            name="Rusted Shield",
            description="A worn shield that has seen better days. Despite the rust, it still offers adequate protection.",
            defense=8,
            armor_type="shield",
            weight=3.0,
            value=100
        )
        
        self.items["cathedral_plate"] = Armor(
            id="cathedral_plate",
            name="Cathedral Plate Armor",
            description="Heavy armor worn by the elite knights of the cathedral. Ornate religious symbols adorn the breastplate.",
            defense=25,
            armor_type="chest",
            weight=8.0,
            value=500,
            resistance={"dark": 15}
        )
        
        self.items["deacon_robes"] = Armor(
            id="deacon_robes",
            name="Deacon's Robes",
            description="Dark robes worn by the deacons of the cathedral. Offers little physical protection but imbued with arcane resistance.",
            defense=5,
            armor_type="chest",
            weight=1.5,
            value=300,
            resistance={"magic": 20, "fire": 10}
        )
        
        self.items["frost_knight_armor"] = Armor(
            id="frost_knight_armor",
            name="Frost Knight Armor",
            description="Armor coated in a permanent layer of frost. Extremely heavy but offers exceptional protection.",
            defense=30,
            armor_type="chest",
            weight=12.0,
            value=800,
            resistance={"fire": 25, "ice": -10}  # Vulnerable to ice
        )
        
        self.items["hollowed_crown"] = Armor(
            id="hollowed_crown",
            name="Hollowed Crown",
            description="The tarnished crown of King Morgaeth. Dark energy swirls within its jewels.",
            defense=12,
            armor_type="head",
            weight=1.0,
            value=1200,
            resistance={"dark": 30, "holy": -25}  # Vulnerable to holy
        )
        
        # Consumables
        self.items["soul_remnant"] = Consumable(
            id="soul_remnant",
            name="Soul Remnant",
            description="A fragment of essence that can be consumed to restore a small amount of health.",
            effect={"healing": 15},
            value=10,
            quantity=1
        )
        
        self.items["life_gem"] = Consumable(
            id="life_gem",
            name="Life Gem",
            description="A crystal that slowly restores health when crushed and consumed.",
            effect={"healing": 30, "over_time": True, "duration": 5},
            value=100,
            quantity=1
        )
        
        self.items["ember"] = Consumable(
            id="ember",
            name="Ember",
            description="A warm ember that temporarily boosts maximum health when consumed.",
            effect={"max_health_boost": 20, "duration": 180},
            value=150,
            quantity=1
        )
        
        self.items["green_blossom"] = Consumable(
            id="green_blossom",
            name="Green Blossom",
            description="A fragrant green herb that temporarily boosts stamina regeneration.",
            effect={"stamina_regen": 20, "duration": 60},
            value=120,
            quantity=1
        )
        
        self.items["estus_shard"] = Item(
            id="estus_shard",
            name="Estus Shard",
            description="A fragment of an Estus Flask. Can be used to increase the number of uses for your Estus Flask.",
            item_type="key",
            value=500,
            usable=True
        )
        
        self.items["homeward_bone"] = Item(
            id="homeward_bone",
            name="Homeward Bone",
            description="A charred bone that carries the scent of home. Use to return to the last rested beacon.",
            item_type="consumable",
            value=150,
            usable=True,
            quantity=1
        )
        
        self.items["dark_residue"] = Item(
            id="dark_residue",
            name="Dark Residue",
            description="A strange, viscous substance that seems to absorb light. Used in certain crafting recipes.",
            item_type="material",
            value=50,
            usable=False,
            quantity=1
        )
        
        self.items["ember_essence"] = Item(
            id="ember_essence",
            name="Ember Essence",
            description="A concentrated form of fire energy. Warm to the touch and glows softly in darkness.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["frost_essence"] = Item(
            id="frost_essence",
            name="Frost Essence",
            description="Crystallized cold energy. The air around it is perpetually chilled.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["blessed_medallion"] = Item(
            id="blessed_medallion",
            name="Blessed Medallion",
            description="A holy symbol that provides protection against the dark. Slowly regenerates health when equipped.",
            item_type="amulet",
            value=300,
            equippable=True,
            stats={"health_regen": 1, "resistance": {"dark": 10}},
            quantity=1
        )
        
        self.items["dark_tome"] = Item(
            id="dark_tome",
            name="Dark Tome",
            description="An ancient book containing forbidden knowledge. The pages seem to whisper when turned.",
            item_type="catalyst",
            value=400,
            equippable=True,
            stats={"spell_boost": 15, "intelligence_scaling": True},
            quantity=1
        )
        
        self.items["royal_signet"] = Item(
            id="royal_signet",
            name="Royal Signet Ring",
            description="The royal signet of King Morgaeth. Grants authority and increases essence gained from defeating enemies.",
            item_type="ring",
            value=800,
            equippable=True,
            stats={"essence_gain": 1.2, "charisma": 5},
            quantity=1
        )
        
    def load_enemies(self):
        """Load all enemy data."""
        # Basic enemies
        self.enemies["wandering_hollow"] = Enemy(
            id="wandering_hollow",
            name="Wandering Hollow",
            description="A hollowed out corpse that wanders aimlessly. It's eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=1,
            hp=50,
            attack=10,
            defense=5,
            attack_patterns=[{"name": "Basic Attack", "damage": 10, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=10
        )
        
        self.enemies["fallen_knight"] = Enemy(
            id="fallen_knight",
            name="Fallen Knight",
            description="A knight in armor that has been hollowed out. Its eyes are dark and lifeless, reflecting the corruption that has consumed it.",
            level=2,
            hp=70,
            attack=15,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 15, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=20
        )
        
        # Add more enemies as needed...
    
    def load_bosses(self):
        """Load all boss data."""
        # Basic bosses
        self.bosses["hollow_citizen"] = Enemy(
            id="hollow_citizen",
            name="Hollow Citizen",
            description="A hollowed out citizen that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=3,
            hp=100,
            attack=20,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 20, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=30
        )
        
        self.bosses["corrupted_guard"] = Enemy(
            id="corrupted_guard",
            name="Corrupted Guard",
            description="A guard in armor that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=4,
            hp=120,
            attack=25,
            defense=15,
            attack_patterns=[{"name": "Basic Attack", "damage": 25, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=40
        )
        
        # Add more bosses as needed...
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
import os
import json
import time
import random
import pickle
import datetime
import platform
import sys
from typing import Dict, List, Optional, Tuple, Union, Any

# Constants
SAVE_DIR = "saves"
AUTOSAVE_FILE = os.path.join(SAVE_DIR, "autosave.sav")
VERSION = "1.0.0"

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# ASCII Art and UI Elements
TITLE_ART = """
  ╔═══════════════════════════════════════════════════════════╗
  ║  ▄████▄   ██▀███   █    ██  ███▄ ▄███▓ ▄▄▄▄    ██▓    ██▓ ║
  ║ ▒██▀ ▀█  ▓██ ▒ ██▒ ██  ▓██▒▓██▒▀█▀ ██▒▓█████▄ ▓██▒   ▓██▒ ║
  ║ ▒▓█    ▄ ▓██ ░▄█ ▒▓██  ▒██░▓██    ▓██░▒██▒ ▄██▒██░   ▒██░ ║
  ║ ▒▓▓▄ ▄██▒▒██▀▀█▄  ▓▓█  ░██░▒██    ▒██ ▒██░█▀  ▒██░   ▒██░ ║
  ║ ▒ ▓███▀ ░░██▓ ▒██▒▒▒█████▓ ▒██▒   ░██▒░▓█  ▀█▓░██████░██████╗
  ║ ░ ░▒ ▒  ░░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ░ ▒░   ░  ░░▒▓███▀▒░ ▒░▓  ░ ▒░▓  ║
  ║   ░  ▒     ░▒ ░ ▒░░░▒░ ░ ░ ░  ░      ░▒░▒   ░ ░ ░ ▒  ░ ░ ▒  ║
  ║ ░          ░░   ░  ░░░ ░ ░ ░      ░    ░    ░   ░ ░    ░ ░  ║
  ║ ░ ░         ░        ░            ░    ░          ░  ░   ░  ║
  ║                           ARDENVALE                        ║
  ╚═══════════════════════════════════════════════════════════╝
                A REALM SHATTERED BY A FADING FLAME
"""

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                      ARDENVALE                            ║
╚═══════════════════════════════════════════════════════════╝
"""

DIVIDER = "═" * 70

# Utility Functions
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
        
        return {
            "player_name": save_data["player"]["name"],
            "player_level": save_data["player"]["level"],
            "location": save_data["player"]["current_location"],
            "timestamp": save_data["timestamp"],
            "version": save_data["version"]
        }
    except Exception as e:
        return {
            "error": str(e),
            "filename": filename
        }

# Game Classes
class Item:
    def __init__(self, id: str, name: str, description: str, item_type: str, value: int = 0, 
                 weight: float = 0.0, stats: Dict = None, usable: bool = False, 
                 equippable: bool = False, quantity: int = 1):
        self.id = id
        self.name = name
        self.description = description
        self.item_type = item_type  # weapon, armor, consumable, key, etc.
        self.value = value
        self.weight = weight
        self.stats = stats or {}
        self.usable = usable
        self.equippable = equippable
        self.quantity = quantity
        self.equipped = False
    
    def use(self, player) -> str:
        """Use the item and return result message."""
        if not self.usable:
            return f"You cannot use the {self.name}."
        
        # Implement item usage logic here
        result = "You used the item, but nothing happened."
        
        # Example: Healing potion
        if self.item_type == "consumable" and "healing" in self.stats:
            heal_amount = self.stats["healing"]
            player.heal(heal_amount)
            result = f"You drink the {self.name} and recover {heal_amount} health."
            self.quantity -= 1
            
        return result
    
    def to_dict(self) -> Dict:
        """Convert item to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "value": self.value,
            "weight": self.weight,
            "stats": self.stats,
            "usable": self.usable,
            "equippable": self.equippable,
            "quantity": self.quantity,
            "equipped": self.equipped
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Create an item from dictionary data."""
        item = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=data["item_type"],
            value=data["value"],
            weight=data["weight"],
            stats=data["stats"],
            usable=data["usable"],
            equippable=data["equippable"],
            quantity=data["quantity"]
        )
        item.equipped = data["equipped"]
        return item

class Weapon(Item):
    def __init__(self, id: str, name: str, description: str, damage: int, 
                 damage_type: str, weight: float, value: int, 
                 special_ability: Dict = None, two_handed: bool = False):
        stats = {
            "damage": damage,
            "damage_type": damage_type,
            "two_handed": two_handed
        }
        if special_ability:
            stats["special_ability"] = special_ability
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="weapon",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )
    
    def get_damage(self) -> int:
        """Calculate the weapon's damage."""
        base_damage = self.stats["damage"]
        return base_damage
    
    def weapon_art(self, player, target) -> str:
        """Use the weapon's special ability."""
        if "special_ability" not in self.stats:
            return "This weapon has no special ability."
        
        ability = self.stats["special_ability"]
        # Implement weapon special ability logic
        
        return f"You use {ability['name']}!"

class Armor(Item):
    def __init__(self, id: str, name: str, description: str, defense: int, 
                 armor_type: str, weight: float, value: int, 
                 resistance: Dict = None):
        stats = {
            "defense": defense,
            "armor_type": armor_type,
        }
        if resistance:
            stats["resistance"] = resistance
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="armor",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )

class Consumable(Item):
    def __init__(self, id: str, name: str, description: str, effect: Dict, 
                 value: int, weight: float = 0.1, quantity: int = 1):
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="consumable",
            value=value,
            weight=weight,
            stats=effect,
            usable=True,
            equippable=False,
            quantity=quantity
        )

class Enemy:
    def __init__(self, id: str, name: str, description: str, level: int, 
                 hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.attack_patterns = attack_patterns or []
        self.loot_table = loot_table or []
        self.essence = essence
        self.weaknesses = weaknesses or []
        self.current_pattern_index = 0
    
    def get_next_attack(self) -> Dict:
        """Get the next attack pattern in sequence."""
        if not self.attack_patterns:
            return {"name": "Basic Attack", "damage": self.attack, "type": "physical"}
        
        pattern = self.attack_patterns[self.current_pattern_index]
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.attack_patterns)
        return pattern
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        # Apply weakness multipliers
        multiplier = 1.0
        if damage_type in self.weaknesses:
            multiplier = 1.5
            
        damage = int(max(1, amount * multiplier - self.defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the enemy is dead."""
        return self.hp <= 0
    
    def drop_loot(self) -> List[Item]:
        """Generate loot drops based on loot table."""
        drops = []
        for loot_entry in self.loot_table:
            if random.random() < loot_entry["chance"]:
                # Create the item from the item database
                item_id = loot_entry["item_id"]
                item = create_item(item_id)
                if item:
                    # Set quantity if specified
                    if "quantity" in loot_entry:
                        item.quantity = random.randint(
                            loot_entry["quantity"]["min"], 
                            loot_entry["quantity"]["max"]
                        )
                    drops.append(item)
        return drops
    
    def to_dict(self) -> Dict:
        """Convert enemy to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "attack_patterns": self.attack_patterns,
            "loot_table": self.loot_table,
            "essence": self.essence,
            "weaknesses": self.weaknesses,
            "current_pattern_index": self.current_pattern_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Enemy':
        """Create an enemy from dictionary data."""
        enemy = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            level=data["level"],
            hp=data["max_hp"],
            attack=data["attack"],
            defense=data["defense"],
            attack_patterns=data["attack_patterns"],
            loot_table=data["loot_table"],
            essence=data["essence"],
            weaknesses=data["weaknesses"]
        )
        enemy.hp = data["hp"]
        enemy.current_pattern_index = data["current_pattern_index"]
        return enemy

class Boss(Enemy):
    def __init__(self, id: str, name: str, title: str, description: str, 
                 level: int, hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None,
                 phases: List[Dict] = None):
        super().__init__(
            id=id,
            name=f"{name}, {title}",
            description=description,
            level=level,
            hp=hp,
            attack=attack,
            defense=defense,
            attack_patterns=attack_patterns,
            loot_table=loot_table,
            essence=essence,
            weaknesses=weaknesses
        )
        self.phases = phases or []
        self.current_phase = 0
        self.phase_triggers = [phase["trigger"] for phase in self.phases] if phases else []
    
    def update_phase(self) -> bool:
        """Check and update boss phase based on HP. Return True if phase changed."""
        if not self.phases:
            return False
            
        # Check if we should transition to the next phase
        hp_percentage = self.hp / self.max_hp * 100
        
        for i, trigger in enumerate(self.phase_triggers):
            if hp_percentage <= trigger and i > self.current_phase:
                self.current_phase = i
                # Apply phase changes
                phase = self.phases[i]
                if "attack_patterns" in phase:
                    self.attack_patterns = phase["attack_patterns"]
                    self.current_pattern_index = 0
                if "attack_boost" in phase:
                    self.attack += phase["attack_boost"]
                if "defense_boost" in phase:
                    self.defense += phase["defense_boost"]
                if "message" in phase:
                    print_slow(phase["message"])
                    
                return True
                
        return False

class Location:
    def __init__(self, id: str, name: str, description: str, 
                 connections: Dict[str, str] = None,
                 enemies: List[str] = None,
                 items: List[str] = None,
                 npcs: List[str] = None,
                 is_beacon: bool = False,
                 map_art: str = None,
                 first_visit_text: str = None,
                 events: Dict = None):
        self.id = id
        self.name = name
        self.description = description
        self.connections = connections or {}  # Direction: location_id
        self.enemies = enemies or []  # List of enemy ids that can spawn here
        self.items = items or []  # List of item ids that can be found here
        self.npcs = npcs or []  # List of NPC ids that can be found here
        self.is_beacon = is_beacon
        self.map_art = map_art
        self.first_visit_text = first_visit_text
        self.events = events or {}  # Event triggers
        self.visited = False
    
    def get_description(self) -> str:
        """Get the location description."""
        return self.description
    
    def get_connections_string(self) -> str:
        """Get a string describing available exits."""
        if not self.connections:
            return "There are no obvious exits."
            
        exits = []
        for direction, _ in self.connections.items():
            exits.append(direction)
        
        return f"Exits: {', '.join(exits)}"
    
    def to_dict(self) -> Dict:
        """Convert location to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connections": self.connections,
            "enemies": self.enemies,
            "items": self.items,
            "npcs": self.npcs,
            "is_beacon": self.is_beacon,
            "map_art": self.map_art,
            "first_visit_text": self.first_visit_text,
            "events": self.events,
            "visited": self.visited
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        """Create a location from dictionary data."""
        location = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            connections=data["connections"],
            enemies=data["enemies"],
            items=data["items"],
            npcs=data["npcs"],
            is_beacon=data["is_beacon"],
            map_art=data["map_art"],
            first_visit_text=data["first_visit_text"],
            events=data["events"]
        )
        location.visited = data["visited"]
        return location

class NPC:
    def __init__(self, id: str, name: str, description: str, 
                 dialogue: Dict[str, Dict] = None,
                 quest: Dict = None,
                 shop_inventory: List[str] = None,
                 faction: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.dialogue = dialogue or {"default": {"text": "...", "options": {}}}
        self.current_dialogue = "default"
        self.quest = quest
        self.shop_inventory = shop_inventory or []
        self.faction = faction
        self.met = False
        self.relationship = 0  # -100 to 100
    
    def get_dialogue(self) -> Dict:
        """Get the current dialogue options."""
        return self.dialogue.get(self.current_dialogue, self.dialogue["default"])
    
    def talk(self) -> str:
        """Start a conversation with the NPC."""
        if not self.met:
            self.met = True
            return f"You meet {self.name} for the first time.\n{self.description}"
        
        return f"{self.name}: {self.get_dialogue()['text']}"
    
    def respond(self, option: str) -> str:
        """Respond to a dialogue option."""
        dialogue = self.get_dialogue()
        
        if option in dialogue["options"]:
            response = dialogue["options"][option]
            
            # Update dialogue state if needed
            if "next" in response:
                self.current_dialogue = response["next"]
            
            # Handle quest progression
            if "quest_progress" in response and self.quest:
                # Implement quest progression logic
                pass
            
            # Handle relationship changes
            if "relationship" in response:
                self.relationship += response["relationship"]
                
            return response["text"]
        
        return "Invalid response."
    
    def to_dict(self) -> Dict:
        """Convert NPC to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dialogue": self.dialogue,
            "current_dialogue": self.current_dialogue,
            "quest": self.quest,
            "shop_inventory": self.shop_inventory,
            "faction": self.faction,
            "met": self.met,
            "relationship": self.relationship
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        """Create an NPC from dictionary data."""
        npc = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            dialogue=data["dialogue"],
            quest=data["quest"],
            shop_inventory=data["shop_inventory"],
            faction=data["faction"]
        )
        npc.current_dialogue = data["current_dialogue"]
        npc.met = data["met"]
        npc.relationship = data["relationship"]
        return npc

class Player:
    def __init__(self, name: str, character_class: str, level: int = 1):
        self.name = name
        self.character_class = character_class
        self.level = level
        self.essence = 0  # Currency
        self.lost_essence = 0  # Lost on death
        self.lost_essence_location = None
        
        # Initialize stats based on class
        if character_class == "Warrior":
            self.max_hp = 100
            self.max_stamina = 80
            self.strength = 14
            self.dexterity = 9
            self.intelligence = 7
            self.faith = 8
            self.vitality = 12
            self.endurance = 10
        elif character_class == "Knight":
            self.max_hp = 90
            self.max_stamina = 90
            self.strength = 12
            self.dexterity = 12
            self.intelligence = 9
            self.faith = 11
            self.vitality = 10
            self.endurance = 11
        elif character_class == "Pyromancer":
            self.max_hp = 80
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 12
            self.faith = 14
            self.vitality = 8
            self.endurance = 9
        elif character_class == "Thief":
            self.max_hp = 75
            self.max_stamina = 100
            self.strength = 9
            self.dexterity = 14
            self.intelligence = 10
            self.faith = 8
            self.vitality = 9
            self.endurance = 14
        else:  # Default
            self.max_hp = 85
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 10
            self.faith = 10
            self.vitality = 10
            self.endurance = 10
        
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.inventory = []
        self.equipment = {
            "weapon": None,
            "shield": None,
            "armor": None,
            "ring1": None,
            "ring2": None,
            "amulet": None
        }
        self.estus_flask = {
            "current": 3,
            "max": 3
        }
        self.current_location = "highcastle_entrance"
        self.quests = {}
        self.discovered_locations = set()
        self.killed_enemies = {}
        self.stance = "balanced"  # balanced, aggressive, defensive
    
    def heal(self, amount: int) -> int:
        """Heal the player and return amount healed."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def restore_stamina(self, amount: int) -> int:
        """Restore stamina and return amount restored."""
        old_stamina = self.stamina
        self.stamina = min(self.max_stamina, self.stamina + amount)
        return self.stamina - old_stamina
    
    def use_estus(self) -> bool:
        """Use an estus flask charge to heal."""
        if self.estus_flask["current"] <= 0:
            return False
        
        self.estus_flask["current"] -= 1
        heal_amount = int(self.max_hp * 0.4)  # Heal 40% of max HP
        self.heal(heal_amount)
        return True
    
    def rest_at_beacon(self):
        """Rest at a beacon to restore HP, stamina, and estus."""
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.estus_flask["current"] = self.estus_flask["max"]
    
    def add_item(self, item: Item) -> bool:
        """Add an item to inventory. Return True if successful."""
        # Check if the item is stackable and exists in inventory
        if item.quantity > 1:
            for inv_item in self.inventory:
                if inv_item.id == item.id:
                    inv_item.quantity += item.quantity
                    return True
                    
        self.inventory.append(item)
        return True
    
    def remove_item(self, item: Item) -> bool:
        """Remove an item from inventory. Return True if successful."""
        for i, inv_item in enumerate(self.inventory):
            if inv_item.id == item.id:
                if inv_item.quantity > 1:
                    inv_item.quantity -= 1
                    return True
                else:
                    self.inventory.pop(i)
                    return True
        return False
    
    def equip_item(self, item: Item) -> str:
        """Equip an item. Return result message."""
        if not item.equippable:
            return f"You cannot equip {item.name}."
            
        # Determine equipment slot
        slot = None
        if item.item_type == "weapon":
            slot = "weapon"
        elif item.item_type == "shield":
            slot = "shield"
        elif item.item_type == "armor":
            slot = "armor"
        elif item.item_type == "ring":
            # Check if ring slots are available
            if self.equipment["ring1"] is None:
                slot = "ring1"
            elif self.equipment["ring2"] is None:
                slot = "ring2"
            else:
                return "You cannot equip more rings."
        elif item.item_type == "amulet":
            slot = "amulet"
        else:
            return f"Cannot equip {item.name}."
            
        # Unequip current item in that slot if any
        if self.equipment[slot] is not None:
            self.equipment[slot].equipped = False
            
        # Equip new item
        self.equipment[slot] = item
        item.equipped = True
        
        return f"You equipped {item.name}."
    
    def unequip_item(self, slot: str) -> str:
        """Unequip an item from specified slot. Return result message."""
        if slot not in self.equipment or self.equipment[slot] is None:
            return f"Nothing equipped in {slot}."
            
        item = self.equipment[slot]
        item.equipped = False
        self.equipment[slot] = None
        
        return f"You unequipped {item.name}."
    
    def get_attack_power(self) -> int:
        """Calculate the player's attack power."""
        base_attack = self.strength // 2
        
        if self.equipment["weapon"]:
            weapon_damage = self.equipment["weapon"].get_damage()
            # Apply stat scaling based on weapon type
            weapon_stats = self.equipment["weapon"].stats
            if "scaling" in weapon_stats:
                if weapon_stats["scaling"] == "strength":
                    scaling_bonus = self.strength // 3
                elif weapon_stats["scaling"] == "dexterity":
                    scaling_bonus = self.dexterity // 3
                else:
                    scaling_bonus = 0
                weapon_damage += scaling_bonus
            
            base_attack += weapon_damage
        
        # Apply stance modifiers
        if self.stance == "aggressive":
            base_attack = int(base_attack * 1.2)  # 20% more damage
        elif self.stance == "defensive":
            base_attack = int(base_attack * 0.8)  # 20% less damage
            
        return base_attack
    
    def get_defense(self) -> int:
        """Calculate the player's defense value."""
        base_defense = self.vitality // 2
        
        if self.equipment["armor"]:
            base_defense += self.equipment["armor"].stats["defense"]
            
        if self.equipment["shield"] and self.stance != "aggressive":
            base_defense += self.equipment["shield"].stats["defense"]
        
        # Apply stance modifiers
        if self.stance == "defensive":
            base_defense = int(base_defense * 1.2)  # 20% more defense
        elif self.stance == "aggressive":
            base_defense = int(base_defense * 0.8)  # 20% less defense
            
        return base_defense
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        defense = self.get_defense()
        
        # Apply resistances from equipment
        resistance_mult = 1.0
        for slot, item in self.equipment.items():
            if item and "resistance" in item.stats and damage_type in item.stats["resistance"]:
                resistance_mult -= item.stats["resistance"][damage_type] / 100.0
        
        # Ensure resistance multiplier is at least 0.2 (80% damage reduction max)
        resistance_mult = max(0.2, resistance_mult)
        
        # Calculate final damage
        damage = int(max(1, amount * resistance_mult - defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the player is dead."""
        return self.hp <= 0
    
    def die(self):
        """Handle player death."""
        # Drop essence at current location
        self.lost_essence = self.essence
        self.lost_essence_location = self.current_location
        self.essence = 0
        
        # Respawn at last beacon
        # This would be implemented in the game loop logic
    
    def recover_lost_essence(self):
        """Recover lost essence."""
        if self.lost_essence > 0:
            self.essence += self.lost_essence
            self.lost_essence = 0
            self.lost_essence_location = None
            return True
        return False
    
    def level_up(self, stat: str) -> bool:
        """Level up a stat. Return True if successful."""
        cost = self.calculate_level_cost()
        
        if self.essence < cost:
            return False
            
        self.essence -= cost
        self.level += 1
        
        # Increase the chosen stat
        if stat == "strength":
            self.strength += 1
        elif stat == "dexterity":
            self.dexterity += 1
        elif stat == "intelligence":
            self.intelligence += 1
        elif stat == "faith":
            self.faith += 1
        elif stat == "vitality":
            self.vitality += 1
            self.max_hp += 5
            self.hp += 5
        elif stat == "endurance":
            self.endurance += 1
            self.max_stamina += 5
            self.stamina += 5
        
        return True
    
    def calculate_level_cost(self) -> int:
        """Calculate the essence cost for the next level."""
        return int(100 * (1.1 ** (self.level - 1)))
    
    def use_item(self, item_index: int) -> str:
        """Use an item from inventory by index."""
        if item_index < 0 or item_index >= len(self.inventory):
            return "Invalid item index."
            
        item = self.inventory[item_index]
        
        if not item.usable:
            return f"You cannot use {item.name}."
            
        result = item.use(self)
        
        # Remove item if quantity reaches 0
        if item.quantity <= 0:
            self.inventory.pop(item_index)
            
        return result
    
    def change_stance(self, new_stance: str) -> str:
        """Change combat stance. Return result message."""
        valid_stances = ["balanced", "aggressive", "defensive"]
        
        if new_stance not in valid_stances:
            return f"Invalid stance. Choose from: {', '.join(valid_stances)}"
            
        old_stance = self.stance
        self.stance = new_stance
        
        return f"Changed stance from {old_stance} to {new_stance}."
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for saving."""
        return {
            "name": self.name,
            "character_class": self.character_class,
            "level": self.level,
            "essence": self.essence,
            "lost_essence": self.lost_essence,
            "lost_essence_location": self.lost_essence_location,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "max_stamina": self.max_stamina,
            "stamina": self.stamina,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "faith": self.faith,
            "vitality": self.vitality,
            "endurance": self.endurance,
            "inventory": [item.to_dict() for item in self.inventory],
            "equipment": {slot: (item.to_dict() if item else None) for slot, item in self.equipment.items()},
            "estus_flask": self.estus_flask,
            "current_location": self.current_location,
            "quests": self.quests,
            "discovered_locations": list(self.discovered_locations),
            "killed_enemies": self.killed_enemies,
            "stance": self.stance
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create a player from dictionary data."""
        player = cls(
            name=data["name"],
            character_class=data["character_class"],
            level=data["level"]
        )
        player.essence = data["essence"]
        player.lost_essence = data["lost_essence"]
        player.lost_essence_location = data["lost_essence_location"]
        player.max_hp = data["max_hp"]
        player.hp = data["hp"]
        player.max_stamina = data["max_stamina"]
        player.stamina = data["stamina"]
        player.strength = data["strength"]
        player.dexterity = data["dexterity"]
        player.intelligence = data["intelligence"]
        player.faith = data["faith"]
        player.vitality = data["vitality"]
        player.endurance = data["endurance"]
        
        # Reconstruct inventory
        player.inventory = []
        for item_data in data["inventory"]:
            if item_data["item_type"] == "weapon":
                item = Weapon(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    damage=item_data["stats"]["damage"],
                    damage_type=item_data["stats"]["damage_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    special_ability=item_data["stats"].get("special_ability"),
                    two_handed=item_data["stats"].get("two_handed", False)
                )
            elif item_data["item_type"] == "armor":
                item = Armor(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    defense=item_data["stats"]["defense"],
                    armor_type=item_data["stats"]["armor_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    resistance=item_data["stats"].get("resistance")
                )
            elif item_data["item_type"] == "consumable":
                item = Consumable(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    effect=item_data["stats"],
                    value=item_data["value"],
                    weight=item_data["weight"],
                    quantity=item_data["quantity"]
                )
            else:
                item = Item.from_dict(item_data)
                
            item.quantity = item_data["quantity"]
            item.equipped = item_data["equipped"]
            player.inventory.append(item)
        
        # Reconstruct equipment
        player.equipment = {slot: None for slot in player.equipment.keys()}
        for slot, item_data in data["equipment"].items():
            if item_data:
                for item in player.inventory:
                    if item.id == item_data["id"]:
                        player.equipment[slot] = item
                        break
                        
        player.estus_flask = data["estus_flask"]
        player.current_location = data["current_location"]
        player.quests = data["quests"]
        player.discovered_locations = set(data["discovered_locations"])
        player.killed_enemies = data["killed_enemies"]
        player.stance = data["stance"]
        
        return player

class World:
    def __init__(self):
        self.locations = {}
        self.npcs = {}
        self.items = {}
        self.enemies = {}
        self.bosses = {}
        self.quests = {}
        self.active_events = set()
        self.game_state = {}
        
        # Initialize world components
        self.initialize_world()
    
    def initialize_world(self):
        """Initialize and load all world data."""
        self.load_locations()
        self.load_npcs()
        self.load_items()
        self.load_enemies()
        self.load_bosses()
        self.load_quests()
    
    def load_locations(self):
        """Load all location data."""
        # Highcastle Region
        self.locations["highcastle_entrance"] = Location(
            id="highcastle_entrance",
            name="Highcastle Gate",
            description="The towering gates of Highcastle stand before you, worn by time but still majestic. The once-bustling gatehouse is now quiet, with only a few guards maintaining their eternal vigil.",
            connections={
                "north": "highcastle_plaza",
                "east": "eastern_road",
                "west": "western_path"
            },
            enemies=["wandering_hollow", "fallen_knight"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Gate
       v S       o - You
  
  #################
  #####.....######
  ####...o...#####
  ###.........####
  ##.....+.....###
  #...............
  #...............
            """,
            first_visit_text="You arrive at the once-grand entrance to Highcastle, the last bastion of humanity in these dark times. The walls, though weathered, still stand tall against the encroaching darkness that has consumed much of Ardenvale."
        )
        
        self.locations["highcastle_plaza"] = Location(
            id="highcastle_plaza",
            name="Highcastle Central Plaza",
            description="The central plaza of Highcastle is a shadow of its former glory. Cracked fountains and weathered statues are silent witnesses to a time of prosperity long gone. A few desperate souls still wander here, clinging to routines of a life that no longer exists.",
            connections={
                "north": "highcastle_cathedral",
                "east": "eastern_district",
                "west": "western_district",
                "south": "highcastle_entrance"
            },
            enemies=["hollow_citizen", "corrupted_guard"],
            npcs=["andre_smith", "merchant_ulrich"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ###+######+####
  #...........+.#
  #.....o.......#
  #...#...#...#.#
  #.............#
  #...#...#...#.#
  ###....+....###
            """
        )
        
        self.locations["highcastle_cathedral"] = Location(
            id="highcastle_cathedral",
            name="Cathedral of the Fading Light",
            description="This once-magnificent cathedral now stands in partial ruin. Shafts of light pierce through holes in the ceiling, illuminating dust-covered pews and crumbling statues of forgotten deities. Despite its state, there is still an aura of reverence here.",
            connections={
                "south": "highcastle_plaza",
                "east": "cathedral_tower"
            },
            enemies=["cathedral_knight", "deacon_of_the_deep"],
            npcs=["sister_friede"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ########+######
  #..#.......#..#
  #...........+.#
  #.............#
  #....o........#
  #.....###.....#
  ##....+....####
            """
        )
        
        # Ashen Woods Region
        self.locations["western_path"] = Location(
            id="western_path",
            name="Western Path",
            description="A winding path leads westward from Highcastle. Once a well-traveled trade route, it is now overgrown and dangerous. The trees along the path seem to lean inward, as if watching passersby with malicious intent.",
            connections={
                "east": "highcastle_entrance",
                "west": "ashen_woods_entrance"
            },
            enemies=["wild_beast", "hollow_woodsman"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     % - Trees
       |         ~ - Water
       v S       o - You
  
  %%%%%%%%%%%    
  %%%..........
  %%%...o......
  %%%...........
  %%%...........
  %%%.......%%%%
  %%%%%%%%%%%    
            """
        )
        
        self.locations["ashen_woods_entrance"] = Location(
            id="ashen_woods_entrance",
            name="Ashen Woods Entrance",
            description="The entrance to the Ashen Woods is marked by a sudden change in the landscape. The trees here are grey and lifeless, their bark turned to ash. Wisps of smoke rise from the ground, though there is no fire to be seen.",
            connections={
                "east": "western_path",
                "west": "ashen_woods_clearing"
            },
            enemies=["ember_wolf", "ashen_treant"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         % - Trees
  W <----> E     ^ - Ash trees
       |         ~ - Water
       v S       o - You
  
  ^^^^^^^^^^^^^^
  ^^.....^^^.^^^
  ^.......o...^^
  ^............^
  ^^^..........^
  ^^^^^^^^^^^^^^
  ^^^^^^^^^^^^^^
            """
        )
        
        # Add more locations as needed...
    
    def load_npcs(self):
        """Load all NPC data."""
        self.npcs["andre_smith"] = NPC(
            id="andre_smith",
            name="Andre the Smith",
            description="A muscular blacksmith with arms like tree trunks. Despite the dark times, his eyes still hold a passionate fire for his craft. His hammer strikes rhythmically in the background.",
            dialogue={
                "default": {
                    "text": "Need something forged? Or perhaps an upgrade to that weapon of yours?",
                    "options": {
                        "1": {
                            "text": "I'd like to upgrade my weapon.",
                            "next": "upgrade"
                        },
                        "2": {
                            "text": "Tell me about yourself.",
                            "next": "about"
                        },
                        "3": {
                            "text": "What happened to this place?",
                            "next": "history"
                        },
                        "4": {
                            "text": "Do you have any work for me?",
                            "next": "quest"
                        }
                    }
                },
                "upgrade": {
                    "text": "Ah, let me see what you've got. I can work with most materials, given enough time and the right components.",
                    "options": {
                        "1": {
                            "text": "What materials do you need?",
                            "next": "materials"
                        },
                        "2": {
                            "text": "Actually, let's talk about something else.",
                            "next": "default"
                        }
                    }
                },
                "materials": {
                    "text": "For basic reinforcement, I need titanite shards. For special weapons, I might need ember essence from the Ashen Woods, or perhaps something more exotic. Bring me materials, and I'll see what I can do.",
                    "options": {
                        "1": {
                            "text": "I'll keep an eye out for those.",
                            "next": "default"
                        }
                    }
                },
                "about": {
                    "text": "Been a smith all my life. Learned from my father, who learned from his. I've seen kingdoms rise and fall, but the forge remains. As long as there are warriors who need weapons, I'll be here.",
                    "options": {
                        "1": {
                            "text": "How have you survived the hollowing?",
                            "next": "survived"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "survived": {
                    "text": "Purpose, friend. Those who hollow are those who've lost their purpose. As long as I have my hammer and anvil, I have a reason to keep going. Find your purpose, and you'll never hollow.",
                    "options": {
                        "1": {
                            "text": "That's profound wisdom.",
                            "next": "default",
                            "relationship": 5
                        }
                    }
                },
                "history": {
                    "text": "Highcastle was once the jewel of Ardenvale. When the First Flame began to fade, everything changed. The corruption spread, people hollowed, and darkness crept in. But we endure. We always do.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the First Flame.",
                            "next": "first_flame"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "first_flame": {
                    "text": "The First Flame is what brought light and disparity to our world. Heat and cold, life and death, light and dark... all because of the Flame. Now it fades, and the balance tips toward darkness. Some seek to rekindle it, others to usher in an Age of Dark. Me? I just forge.",
                    "options": {
                        "1": {
                            "text": "Can the Flame be rekindled?",
                            "next": "rekindle"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "rekindle": {
                    "text": "The old legends say it can, but at a cost. Great souls must be sacrificed to feed the Flame. The King... they say he sought another way, and look where that got us. But who knows? Maybe you'll find answers where others failed.",
                    "options": {
                        "1": {
                            "text": "I'll discover the truth.",
                            "next": "default"
                        }
                    }
                },
                "quest": {
                    "text": "As a matter of fact, I do. My old forge has run cold without proper ember. If you could venture to the Ashen Woods and bring back some ember essence, I could craft you something special.",
                    "options": {
                        "1": {
                            "text": "I'll find this ember essence for you.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "That sounds too dangerous.",
                            "next": "quest_decline"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Excellent! Look for it near what they call Ember Lake, deep in the Ashen Woods. The essence glows like a captured sunset. Careful though, the woods have grown wild and hostile since the Flame began to fade.",
                    "options": {
                        "1": {
                            "text": "I'll be careful.",
                            "next": "default",
                            "quest_progress": {"start": "ember_quest"}
                        }
                    }
                },
                "quest_decline": {
                    "text": "Fair enough. It's no small task. The offer stands if you change your mind.",
                    "options": {
                        "1": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_complete": {
                    "text": "By the Flame, you actually found it! This ember essence is perfect. Give me some time, and I'll forge you something worthy of your courage.",
                    "options": {
                        "1": {
                            "text": "Thank you, Andre.",
                            "next": "reward"
                        }
                    }
                },
                "reward": {
                    "text": "Here, take this blade. I call it the Flamebrand. The ember essence is forged into its very core. May it serve you well in the darkness ahead.",
                    "options": {
                        "1": {
                            "text": "It's beautiful. Thank you.",
                            "next": "default",
                            "quest_progress": {"complete": "ember_quest"}
                        }
                    }
                }
            },
            quest={
                "id": "ember_quest",
                "name": "The Smith's Request",
                "description": "Andre needs ember essence from the Ashen Woods to rekindle his forge.",
                "objectives": [
                    {"type": "item", "target": "ember_essence", "quantity": 1}
                ],
                "rewards": {
                    "item": "flamebrand",
                    "essence": 200
                }
            },
            shop_inventory=["reinforced_sword", "knight_shield", "ember"]
        )
        
        self.npcs["merchant_ulrich"] = NPC(
            id="merchant_ulrich",
            name="Merchant Ulrich",
            description="A hunched man with a perpetual nervous twitch. His eyes dart about constantly, and his fingers fidget with the hem of his tattered cloak. Despite his appearance, he has somehow managed to maintain a stock of rare goods.",
            dialogue={
                "default": {
                    "text": "Ah, a customer! Rare sight these days. Looking to trade? I've got wares from all corners of Ardenvale, before... well, before everything went to ruin.",
                    "options": {
                        "1": {
                            "text": "Show me what you have for sale.",
                            "next": "shop"
                        },
                        "2": {
                            "text": "Any rumors lately?",
                            "next": "rumors"
                        },
                        "3": {
                            "text": "How do you get your merchandise?",
                            "next": "merchandise"
                        },
                        "4": {
                            "text": "I'm looking for something specific.",
                            "next": "quest_intro"
                        }
                    }
                },
                "shop": {
                    "text": "Take a look, take a look! Fine goods at reasonable prices. Well, reasonable considering the state of the world.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "rumors": {
                    "text": "Rumors? Oh, I hear many things... They say the old king still wanders the Ringed Citadel, hollowed but retaining a fragment of his former self. And in the Ashen Woods, the tree shepherds have gone mad, attacking any who venture too deep.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the king.",
                            "next": "king"
                        },
                        "2": {
                            "text": "What are tree shepherds?",
                            "next": "shepherds"
                        },
                        "3": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "king": {
                    "text": "King Morgaeth was a wise ruler, once. They say he delved too deep into forbidden arts in his quest to save the kingdom from the fading of the Flame. Now he's neither dead nor truly alive... a hollow shell of royalty.",
                    "options": {
                        "1": {
                            "text": "What forbidden arts did he study?",
                            "next": "forbidden_arts"
                        },
                        "2": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        }
                    }
                },
                "forbidden_arts": {
                    "text": "They say he sought to draw power from the Abyss itself. To use darkness to preserve light, if you can imagine such madness. The royal archives might hold more answers, but none dare venture to the Ringed Citadel now.",
                    "options": {
                        "1": {
                            "text": "Interesting. Thank you for the information.",
                            "next": "default",
                            "quest_progress": {"hint": "kings_fall"}
                        }
                    }
                },
                "shepherds": {
                    "text": "Ancient creatures, like walking trees but with awareness. They tended the forests for millennia in peace. The corruption has twisted them, made them violent. A shame. They were magnificent beings.",
                    "options": {
                        "1": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "merchandise": {
                    "text": "Ah, professional secrets! *winks nervously* Let's just say I have... arrangements with certain brave souls who venture where others fear to tread. They bring me goods, I give them essence, everyone profits!",
                    "options": {
                        "1": {
                            "text": "Sounds dangerous.",
                            "next": "dangerous"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dangerous": {
                    "text": "Dangerous? *laughs shakily* My friend, everything is dangerous now. At least my suppliers choose their danger. Most of them return... some of the time.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "quest_intro": {
                    "text": "Something specific? *eyes narrow with interest* I might have what you need, or know where to find it. What are you looking for?",
                    "options": {
                        "1": {
                            "text": "I need access to the Ringed Citadel.",
                            "next": "quest_citadel"
                        },
                        "2": {
                            "text": "Just browsing, actually.",
                            "next": "default"
                        }
                    }
                },
                "quest_citadel": {
                    "text": "*lowers voice* The Citadel? Not many seek to go there willingly. *glances around nervously* I might know of a way, but it will cost you. Not just essence, but a favor.",
                    "options": {
                        "1": {
                            "text": "What kind of favor?",
                            "next": "quest_details"
                        },
                        "2": {
                            "text": "Never mind, too risky.",
                            "next": "default"
                        }
                    }
                },
                "quest_details": {
                    "text": "One of my suppliers ventured into the Blighted Marshes east of here. Never returned. Carried a signet ring I need back. Find it, and I'll give you what you need to enter the Citadel.",
                    "options": {
                        "1": {
                            "text": "I'll find your ring.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Good, good. The marshes are treacherous, but look for a broken cart near the eastern path. That's where my supplier was headed. The ring has a blue stone, can't miss it.",
                    "options": {
                        "1": {
                            "text": "I'll return when I have it.",
                            "next": "default",
                            "quest_progress": {"start": "signet_quest"}
                        }
                    }
                },
                "quest_complete": {
                    "*eyes widen* You found it! And lived to tell the tale! I'm impressed. As promised, here's what you need—a royal seal. It will grant you passage through the outer gates of the Ringed Citadel.",
                    "options": {
                        "1": {
                            "text": "Thank you for your help.",
                            "next": "default",
                            "quest_progress": {"complete": "signet_quest"}
                        }
                    }
                }
            },
            quest={
                "id": "signet_quest",
                "name": "The Merchant's Signet",
                "description": "Find Ulrich's missing signet ring in the Blighted Marshes.",
                "objectives": [
                    {"type": "item", "target": "blue_signet", "quantity": 1}
                ],
                "rewards": {
                    "item": "royal_seal",
                    "essence": 300
                }
            },
            shop_inventory=["estus_shard", "life_gem", "homeward_bone", "green_blossom"]
        )
        
        self.npcs["sister_friede"] = NPC(
            id="sister_friede",
            name="Sister Friede",
            description="A tall, slender woman in white robes that seem untouched by the grime and decay around her. Her face is partially obscured by a hood, but you can see her pale skin and piercing blue eyes. She moves with eerie grace.",
            dialogue={
                "default": {
                    "text": "Ashen One, why do you disturb this sanctuary? This is a place of quiet reflection, not for those who would perpetuate a doomed cycle.",
                    "options": {
                        "1": {
                            "text": "I seek guidance.",
                            "next": "guidance"
                        },
                        "2": {
                            "text": "What cycle do you speak of?",
                            "next": "cycle"
                        },
                        "3": {
                            "text": "Who are you?",
                            "next": "identity"
                        },
                        "4": {
                            "text": "Are you in danger here?",
                            "next": "quest_intro"
                        }
                    }
                },
                "guidance": {
                    "text": "Guidance? *soft laugh* The path ahead is shrouded for all of us. But if you must continue your journey, seek the depths of the Ashen Woods. There lies an ancient tree shepherd who remembers the time before corruption. His wisdom may aid you, if he doesn't kill you first.",
                    "options": {
                        "1": {
                            "text": "Thank you for the information.",
                            "next": "default"
                        },
                        "2": {
                            "text": "Why would he help me?",
                            "next": "help"
                        }
                    }
                },
                "help": {
                    "text": "He wouldn't, not willingly. But in his madness, truths slip out between attempts to end your life. Listen carefully... if you survive long enough to hear anything at all.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "cycle": {
                    "text": "The endless cycle of Light and Dark. For eons, the First Flame has been rekindled when it begins to fade, postponing the Age of Dark that is our birthright. Each rekindling only makes the inevitable collapse more devastating.",
                    "options": {
                        "1": {
                            "text": "You want the Flame to fade?",
                            "next": "fade"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "fade": {
                    "text": "*her eyes narrow slightly* I want what is natural. All fires eventually burn out. Fighting this truth has brought us to this state of perpetual decay. Let it end, and something new may begin.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "identity": {
                    "text": "I am simply a watcher. I've seen kingdoms rise and fall, flames kindle and fade. Now I wait here, in this broken cathedral, observing the final gasps of a dying age.",
                    "options": {
                        "1": {
                            "text": "You speak as if you're ancient.",
                            "next": "ancient"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "ancient": {
                    "text": "*she smiles enigmatically* Time loses meaning when you've witnessed enough cycles. But enough about me. What will you do, Ashen One? Perpetuate this dying world, or help usher in something new?",
                    "options": {
                        "1": {
                            "text": "I'll restore the Flame.",
                            "next": "restore",
                            "relationship": -10
                        },
                        "2": {
                            "text": "Perhaps the Dark should have its time.",
                            "next": "dark",
                            "relationship": 10
                        },
                        "3": {
                            "text": "I haven't decided yet.",
                            "next": "undecided"
                        }
                    }
                },
                "restore": {
                    "text": "*her expression hardens* Then you are no different from the others. Go your way, Ashen One. May you find what you seek... and understand its true cost.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dark": {
                    "text": "*she studies you with new interest* Perhaps there is wisdom in you after all. The Dark is not to be feared, but embraced as part of the natural order. Remember this when your resolve is tested.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "undecided": {
                    "text": "Indecision is... understandable. The weight of such choices is immense. Reflect carefully, Ashen One. Not all is as it seems in Ardenvale.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "quest_intro": {
                    "*she seems surprised by your concern* No, not from the hollowed ones. They avoid this place. But there is a matter that... troubles me. The cathedral's sacred chalice has been stolen, taken to the bell tower by one who has fallen far from grace.",
                    "options": {
                        "1": {
                            "text": "I could retrieve it for you.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "Why is the chalice important?",
                            "next": "chalice_importance"
                        }
                    }
                },
                "chalice_importance": {
                    "text": "It contains old knowledge, symbols of both light and dark in perfect balance. In the wrong hands, this knowledge could upset the natural order, prolong this agonizing age of transition.",
                    "options": {
                        "1": {
                            "text": "I'll retrieve the chalice.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Your offer is... unexpected. The thief is a former deacon, now corrupted beyond recognition. Ascend to the bell tower, but be wary—he will not surrender the chalice willingly.",
                    "options": {
                        "1": {
                            "text": "I'll be careful.",
                            "next": "default",
                            "quest_progress": {"start": "chalice_quest"}
                        }
                    }
                },
                "quest_complete": {
                    "*her eyes widen slightly as you present the chalice* You succeeded where others would have failed. The balance is preserved, for now. Please, take this talisman as a token of my... gratitude. It bears an old symbol of the dark.",
                    "options": {
                        "1": {
                            "text": "Thank you, Sister Friede.",
                            "next": "default",
                            "quest_progress": {"complete": "chalice_quest"},
                            "relationship": 15
                        }
                    }
                }
            },
            quest={
                "id": "chalice_quest",
                "name": "The Sacred Chalice",
                "description": "Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
                "objectives": [
                    {"type": "item", "target": "sacred_chalice", "quantity": 1}
                ],
                "rewards": {
                    "item": "dark_talisman",
                    "essence": 350,
                    "faction": "Children of Dark",
                    "reputation": 15
                }
            },
            faction="Children of Dark"
        )
    
    def load_items(self):
        """Load all item data."""
        # Weapons
        self.items["reinforced_sword"] = Weapon(
            id="reinforced_sword",
            name="Reinforced Longsword",
            description="A sturdy longsword with reinforced steel. Reliable and well-balanced.",
            damage=15,
            damage_type="physical",
            weight=3.0,
            value=200,
            two_handed=False
        )
        
        self.items["knight_sword"] = Weapon(
            id="knight_sword",
            name="Knight's Sword",
            description="A well-crafted sword used by the knights of Highcastle. The blade bears the insignia of the royal guard.",
            damage=18,
            damage_type="physical",
            weight=3.5,
            value=300,
            two_handed=False
        )
        
        self.items["woodsman_axe"] = Weapon(
            id="woodsman_axe",
            name="Woodsman's Axe",
            description="A heavy axe used for chopping wood, now repurposed as a weapon. Slow but powerful.",
            damage=22,
            damage_type="physical",
            weight=4.5,
            value=180,
            two_handed=True
        )
        
        self.items["cathedral_greatsword"] = Weapon(
            id="cathedral_greatsword",
            name="Cathedral Greatsword",
            description="A massive sword wielded by the knights of the cathedral. Holy symbols are etched into the blade.",
            damage=26,
            damage_type="physical",
            weight=6.0,
            value=450,
            two_handed=True,
            special_ability={"name": "Holy Light", "damage": 15, "type": "holy"}
        )
        
        self.items["ember_blade"] = Weapon(
            id="ember_blade",
            name="Ember Blade",
            description="A sword forged in the heart of the Ashen Woods. The blade seems to smolder with inner heat.",
            damage=20,
            damage_type="fire",
            weight=3.0,
            value=500,
            two_handed=False,
            special_ability={"name": "Ignite", "damage": 12, "type": "fire", "duration": 3}
        )
        
        self.items["vordt_mace"] = Weapon(
            id="vordt_mace",
            name="Vordt's Frostmace",
            description="A massive mace once wielded by Vordt, Guardian of the Frost Gate. Crystals of ice form along its surface.",
            damage=30,
            damage_type="physical",
            weight=8.0,
            value=700,
            two_handed=True,
            special_ability={"name": "Frost Strike", "damage": 20, "type": "ice", "slow_effect": True}
        )
        
        self.items["kings_greatsword"] = Weapon(
            id="kings_greatsword",
            name="King's Greatsword",
            description="The royal greatsword of King Morgaeth, now tainted with dark energy. It pulses with corrupted power.",
            damage=35,
            damage_type="physical",
            weight=7.0,
            value=1000,
            two_handed=True,
            special_ability={"name": "Royal Wrath", "damage": 40, "type": "dark", "cooldown": 5}
        )
        
        # Armor
        self.items["knight_helm"] = Armor(
            id="knight_helm",
            name="Knight's Helm",
            description="A standard helmet worn by the knights of Highcastle. Provides good protection but limits visibility.",
            defense=10,
            armor_type="head",
            weight=2.0,
            value=200
        )
        
        self.items["knight_shield"] = Armor(
            id="knight_shield",
            name="Knight's Shield",
            description="A sturdy kite shield bearing the crest of Highcastle. Well-balanced for both defense and mobility.",
            defense=15,
            armor_type="shield",
            weight=3.5,
            value=250
        )
        
        self.items["rusted_shield"] = Armor(
            id="rusted_shield",
            name="Rusted Shield",
            description="A worn shield that has seen better days. Despite the rust, it still offers adequate protection.",
            defense=8,
            armor_type="shield",
            weight=3.0,
            value=100
        )
        
        self.items["cathedral_plate"] = Armor(
            id="cathedral_plate",
            name="Cathedral Plate Armor",
            description="Heavy armor worn by the elite knights of the cathedral. Ornate religious symbols adorn the breastplate.",
            defense=25,
            armor_type="chest",
            weight=8.0,
            value=500,
            resistance={"dark": 15}
        )
        
        self.items["deacon_robes"] = Armor(
            id="deacon_robes",
            name="Deacon's Robes",
            description="Dark robes worn by the deacons of the cathedral. Offers little physical protection but imbued with arcane resistance.",
            defense=5,
            armor_type="chest",
            weight=1.5,
            value=300,
            resistance={"magic": 20, "fire": 10}
        )
        
        self.items["frost_knight_armor"] = Armor(
            id="frost_knight_armor",
            name="Frost Knight Armor",
            description="Armor coated in a permanent layer of frost. Extremely heavy but offers exceptional protection.",
            defense=30,
            armor_type="chest",
            weight=12.0,
            value=800,
            resistance={"fire": 25, "ice": -10}  # Vulnerable to ice
        )
        
        self.items["hollowed_crown"] = Armor(
            id="hollowed_crown",
            name="Hollowed Crown",
            description="The tarnished crown of King Morgaeth. Dark energy swirls within its jewels.",
            defense=12,
            armor_type="head",
            weight=1.0,
            value=1200,
            resistance={"dark": 30, "holy": -25}  # Vulnerable to holy
        )
        
        # Consumables
        self.items["soul_remnant"] = Consumable(
            id="soul_remnant",
            name="Soul Remnant",
            description="A fragment of essence that can be consumed to restore a small amount of health.",
            effect={"healing": 15},
            value=10,
            quantity=1
        )
        
        self.items["life_gem"] = Consumable(
            id="life_gem",
            name="Life Gem",
            description="A crystal that slowly restores health when crushed and consumed.",
            effect={"healing": 30, "over_time": True, "duration": 5},
            value=100,
            quantity=1
        )
        
        self.items["ember"] = Consumable(
            id="ember",
            name="Ember",
            description="A warm ember that temporarily boosts maximum health when consumed.",
            effect={"max_health_boost": 20, "duration": 180},
            value=150,
            quantity=1
        )
        
        self.items["green_blossom"] = Consumable(
            id="green_blossom",
            name="Green Blossom",
            description="A fragrant green herb that temporarily boosts stamina regeneration.",
            effect={"stamina_regen": 20, "duration": 60},
            value=120,
            quantity=1
        )
        
        self.items["estus_shard"] = Item(
            id="estus_shard",
            name="Estus Shard",
            description="A fragment of an Estus Flask. Can be used to increase the number of uses for your Estus Flask.",
            item_type="key",
            value=500,
            usable=True
        )
        
        self.items["homeward_bone"] = Item(
            id="homeward_bone",
            name="Homeward Bone",
            description="A charred bone that carries the scent of home. Use to return to the last rested beacon.",
            item_type="consumable",
            value=150,
            usable=True,
            quantity=1
        )
        
        self.items["dark_residue"] = Item(
            id="dark_residue",
            name="Dark Residue",
            description="A strange, viscous substance that seems to absorb light. Used in certain crafting recipes.",
            item_type="material",
            value=50,
            usable=False,
            quantity=1
        )
        
        self.items["ember_essence"] = Item(
            id="ember_essence",
            name="Ember Essence",
            description="A concentrated form of fire energy. Warm to the touch and glows softly in darkness.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["frost_essence"] = Item(
            id="frost_essence",
            name="Frost Essence",
            description="Crystallized cold energy. The air around it is perpetually chilled.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["blessed_medallion"] = Item(
            id="blessed_medallion",
            name="Blessed Medallion",
            description="A holy symbol that provides protection against the dark. Slowly regenerates health when equipped.",
            item_type="amulet",
            value=300,
            equippable=True,
            stats={"health_regen": 1, "resistance": {"dark": 10}},
            quantity=1
        )
        
        self.items["dark_tome"] = Item(
            id="dark_tome",
            name="Dark Tome",
            description="An ancient book containing forbidden knowledge. The pages seem to whisper when turned.",
            item_type="catalyst",
            value=400,
            equippable=True,
            stats={"spell_boost": 15, "intelligence_scaling": True},
            quantity=1
        )
        
        self.items["royal_signet"] = Item(
            id="royal_signet",
            name="Royal Signet Ring",
            description="The royal signet of King Morgaeth. Grants authority and increases essence gained from defeating enemies.",
            item_type="ring",
            value=800,
            equippable=True,
            stats={"essence_gain": 1.2, "charisma": 5},
            quantity=1
        )
        
    def load_enemies(self):
        """Load all enemy data."""
        # Basic enemies
        self.enemies["wandering_hollow"] = Enemy(
            id="wandering_hollow",
            name="Wandering Hollow",
            description="A hollowed out corpse that wanders aimlessly. It's eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=1,
            hp=50,
            attack=10,
            defense=5,
            attack_patterns=[{"name": "Basic Attack", "damage": 10, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=10
        )
        
        self.enemies["fallen_knight"] = Enemy(
            id="fallen_knight",
            name="Fallen Knight",
            description="A knight in armor that has been hollowed out. Its eyes are dark and lifeless, reflecting the corruption that has consumed it.",
            level=2,
            hp=70,
            attack=15,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 15, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=20
        )
        
        # Add more enemies as needed...
    
    def load_bosses(self):
        """Load all boss data."""
        # Basic bosses
        self.bosses["hollow_citizen"] = Enemy(
            id="hollow_citizen",
            name="Hollow Citizen",
            description="A hollowed out citizen that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=3,
            hp=100,
            attack=20,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 20, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=30
        )
        
        self.bosses["corrupted_guard"] = Enemy(
            id="corrupted_guard",
            name="Corrupted Guard",
            description="A guard in armor that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=4,
            hp=120,
            attack=25,
            defense=15,
            attack_patterns=[{"name": "Basic Attack", "damage": 25, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=40
        )
        
        # Add more bosses as needed...
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
import os
import json
import time
import random
import pickle
import datetime
import platform
import sys
from typing import Dict, List, Optional, Tuple, Union, Any

# Constants
SAVE_DIR = "saves"
AUTOSAVE_FILE = os.path.join(SAVE_DIR, "autosave.sav")
VERSION = "1.0.0"

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# ASCII Art and UI Elements
TITLE_ART = """
  ╔═══════════════════════════════════════════════════════════╗
  ║  ▄████▄   ██▀███   █    ██  ███▄ ▄███▓ ▄▄▄▄    ██▓    ██▓ ║
  ║ ▒██▀ ▀█  ▓██ ▒ ██▒ ██  ▓██▒▓██▒▀█▀ ██▒▓█████▄ ▓██▒   ▓██▒ ║
  ║ ▒▓█    ▄ ▓██ ░▄█ ▒▓██  ▒██░▓██    ▓██░▒██▒ ▄██▒██░   ▒██░ ║
  ║ ▒▓▓▄ ▄██▒▒██▀▀█▄  ▓▓█  ░██░▒██    ▒██ ▒██░█▀  ▒██░   ▒██░ ║
  ║ ▒ ▓███▀ ░░██▓ ▒██▒▒▒█████▓ ▒██▒   ░██▒░▓█  ▀█▓░██████░██████╗
  ║ ░ ░▒ ▒  ░░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ░ ▒░   ░  ░░▒▓███▀▒░ ▒░▓  ░ ▒░▓  ║
  ║   ░  ▒     ░▒ ░ ▒░░░▒░ ░ ░ ░  ░      ░▒░▒   ░ ░ ░ ▒  ░ ░ ▒  ║
  ║ ░          ░░   ░  ░░░ ░ ░ ░      ░    ░    ░   ░ ░    ░ ░  ║
  ║ ░ ░         ░        ░            ░    ░          ░  ░   ░  ║
  ║                           ARDENVALE                        ║
  ╚═══════════════════════════════════════════════════════════╝
                A REALM SHATTERED BY A FADING FLAME
"""

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                      ARDENVALE                            ║
╚═══════════════════════════════════════════════════════════╝
"""

DIVIDER = "═" * 70

# Utility Functions
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
        
        return {
            "player_name": save_data["player"]["name"],
            "player_level": save_data["player"]["level"],
            "location": save_data["player"]["current_location"],
            "timestamp": save_data["timestamp"],
            "version": save_data["version"]
        }
    except Exception as e:
        return {
            "error": str(e),
            "filename": filename
        }

# Game Classes
class Item:
    def __init__(self, id: str, name: str, description: str, item_type: str, value: int = 0, 
                 weight: float = 0.0, stats: Dict = None, usable: bool = False, 
                 equippable: bool = False, quantity: int = 1):
        self.id = id
        self.name = name
        self.description = description
        self.item_type = item_type  # weapon, armor, consumable, key, etc.
        self.value = value
        self.weight = weight
        self.stats = stats or {}
        self.usable = usable
        self.equippable = equippable
        self.quantity = quantity
        self.equipped = False
    
    def use(self, player) -> str:
        """Use the item and return result message."""
        if not self.usable:
            return f"You cannot use the {self.name}."
        
        # Implement item usage logic here
        result = "You used the item, but nothing happened."
        
        # Example: Healing potion
        if self.item_type == "consumable" and "healing" in self.stats:
            heal_amount = self.stats["healing"]
            player.heal(heal_amount)
            result = f"You drink the {self.name} and recover {heal_amount} health."
            self.quantity -= 1
            
        return result
    
    def to_dict(self) -> Dict:
        """Convert item to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "value": self.value,
            "weight": self.weight,
            "stats": self.stats,
            "usable": self.usable,
            "equippable": self.equippable,
            "quantity": self.quantity,
            "equipped": self.equipped
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Create an item from dictionary data."""
        item = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=data["item_type"],
            value=data["value"],
            weight=data["weight"],
            stats=data["stats"],
            usable=data["usable"],
            equippable=data["equippable"],
            quantity=data["quantity"]
        )
        item.equipped = data["equipped"]
        return item

class Weapon(Item):
    def __init__(self, id: str, name: str, description: str, damage: int, 
                 damage_type: str, weight: float, value: int, 
                 special_ability: Dict = None, two_handed: bool = False):
        stats = {
            "damage": damage,
            "damage_type": damage_type,
            "two_handed": two_handed
        }
        if special_ability:
            stats["special_ability"] = special_ability
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="weapon",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )
    
    def get_damage(self) -> int:
        """Calculate the weapon's damage."""
        base_damage = self.stats["damage"]
        return base_damage
    
    def weapon_art(self, player, target) -> str:
        """Use the weapon's special ability."""
        if "special_ability" not in self.stats:
            return "This weapon has no special ability."
        
        ability = self.stats["special_ability"]
        # Implement weapon special ability logic
        
        return f"You use {ability['name']}!"

class Armor(Item):
    def __init__(self, id: str, name: str, description: str, defense: int, 
                 armor_type: str, weight: float, value: int, 
                 resistance: Dict = None):
        stats = {
            "defense": defense,
            "armor_type": armor_type,
        }
        if resistance:
            stats["resistance"] = resistance
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="armor",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )

class Consumable(Item):
    def __init__(self, id: str, name: str, description: str, effect: Dict, 
                 value: int, weight: float = 0.1, quantity: int = 1):
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="consumable",
            value=value,
            weight=weight,
            stats=effect,
            usable=True,
            equippable=False,
            quantity=quantity
        )

class Enemy:
    def __init__(self, id: str, name: str, description: str, level: int, 
                 hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.attack_patterns = attack_patterns or []
        self.loot_table = loot_table or []
        self.essence = essence
        self.weaknesses = weaknesses or []
        self.current_pattern_index = 0
    
    def get_next_attack(self) -> Dict:
        """Get the next attack pattern in sequence."""
        if not self.attack_patterns:
            return {"name": "Basic Attack", "damage": self.attack, "type": "physical"}
        
        pattern = self.attack_patterns[self.current_pattern_index]
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.attack_patterns)
        return pattern
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        # Apply weakness multipliers
        multiplier = 1.0
        if damage_type in self.weaknesses:
            multiplier = 1.5
            
        damage = int(max(1, amount * multiplier - self.defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the enemy is dead."""
        return self.hp <= 0
    
    def drop_loot(self) -> List[Item]:
        """Generate loot drops based on loot table."""
        drops = []
        for loot_entry in self.loot_table:
            if random.random() < loot_entry["chance"]:
                # Create the item from the item database
                item_id = loot_entry["item_id"]
                item = create_item(item_id)
                if item:
                    # Set quantity if specified
                    if "quantity" in loot_entry:
                        item.quantity = random.randint(
                            loot_entry["quantity"]["min"], 
                            loot_entry["quantity"]["max"]
                        )
                    drops.append(item)
        return drops
    
    def to_dict(self) -> Dict:
        """Convert enemy to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "attack_patterns": self.attack_patterns,
            "loot_table": self.loot_table,
            "essence": self.essence,
            "weaknesses": self.weaknesses,
            "current_pattern_index": self.current_pattern_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Enemy':
        """Create an enemy from dictionary data."""
        enemy = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            level=data["level"],
            hp=data["max_hp"],
            attack=data["attack"],
            defense=data["defense"],
            attack_patterns=data["attack_patterns"],
            loot_table=data["loot_table"],
            essence=data["essence"],
            weaknesses=data["weaknesses"]
        )
        enemy.hp = data["hp"]
        enemy.current_pattern_index = data["current_pattern_index"]
        return enemy

class Boss(Enemy):
    def __init__(self, id: str, name: str, title: str, description: str, 
                 level: int, hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None,
                 phases: List[Dict] = None):
        super().__init__(
            id=id,
            name=f"{name}, {title}",
            description=description,
            level=level,
            hp=hp,
            attack=attack,
            defense=defense,
            attack_patterns=attack_patterns,
            loot_table=loot_table,
            essence=essence,
            weaknesses=weaknesses
        )
        self.phases = phases or []
        self.current_phase = 0
        self.phase_triggers = [phase["trigger"] for phase in self.phases] if phases else []
    
    def update_phase(self) -> bool:
        """Check and update boss phase based on HP. Return True if phase changed."""
        if not self.phases:
            return False
            
        # Check if we should transition to the next phase
        hp_percentage = self.hp / self.max_hp * 100
        
        for i, trigger in enumerate(self.phase_triggers):
            if hp_percentage <= trigger and i > self.current_phase:
                self.current_phase = i
                # Apply phase changes
                phase = self.phases[i]
                if "attack_patterns" in phase:
                    self.attack_patterns = phase["attack_patterns"]
                    self.current_pattern_index = 0
                if "attack_boost" in phase:
                    self.attack += phase["attack_boost"]
                if "defense_boost" in phase:
                    self.defense += phase["defense_boost"]
                if "message" in phase:
                    print_slow(phase["message"])
                    
                return True
                
        return False

class Location:
    def __init__(self, id: str, name: str, description: str, 
                 connections: Dict[str, str] = None,
                 enemies: List[str] = None,
                 items: List[str] = None,
                 npcs: List[str] = None,
                 is_beacon: bool = False,
                 map_art: str = None,
                 first_visit_text: str = None,
                 events: Dict = None):
        self.id = id
        self.name = name
        self.description = description
        self.connections = connections or {}  # Direction: location_id
        self.enemies = enemies or []  # List of enemy ids that can spawn here
        self.items = items or []  # List of item ids that can be found here
        self.npcs = npcs or []  # List of NPC ids that can be found here
        self.is_beacon = is_beacon
        self.map_art = map_art
        self.first_visit_text = first_visit_text
        self.events = events or {}  # Event triggers
        self.visited = False
    
    def get_description(self) -> str:
        """Get the location description."""
        return self.description
    
    def get_connections_string(self) -> str:
        """Get a string describing available exits."""
        if not self.connections:
            return "There are no obvious exits."
            
        exits = []
        for direction, _ in self.connections.items():
            exits.append(direction)
        
        return f"Exits: {', '.join(exits)}"
    
    def to_dict(self) -> Dict:
        """Convert location to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connections": self.connections,
            "enemies": self.enemies,
            "items": self.items,
            "npcs": self.npcs,
            "is_beacon": self.is_beacon,
            "map_art": self.map_art,
            "first_visit_text": self.first_visit_text,
            "events": self.events,
            "visited": self.visited
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        """Create a location from dictionary data."""
        location = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            connections=data["connections"],
            enemies=data["enemies"],
            items=data["items"],
            npcs=data["npcs"],
            is_beacon=data["is_beacon"],
            map_art=data["map_art"],
            first_visit_text=data["first_visit_text"],
            events=data["events"]
        )
        location.visited = data["visited"]
        return location

class NPC:
    def __init__(self, id: str, name: str, description: str, 
                 dialogue: Dict[str, Dict] = None,
                 quest: Dict = None,
                 shop_inventory: List[str] = None,
                 faction: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.dialogue = dialogue or {"default": {"text": "...", "options": {}}}
        self.current_dialogue = "default"
        self.quest = quest
        self.shop_inventory = shop_inventory or []
        self.faction = faction
        self.met = False
        self.relationship = 0  # -100 to 100
    
    def get_dialogue(self) -> Dict:
        """Get the current dialogue options."""
        return self.dialogue.get(self.current_dialogue, self.dialogue["default"])
    
    def talk(self) -> str:
        """Start a conversation with the NPC."""
        if not self.met:
            self.met = True
            return f"You meet {self.name} for the first time.\n{self.description}"
        
        return f"{self.name}: {self.get_dialogue()['text']}"
    
    def respond(self, option: str) -> str:
        """Respond to a dialogue option."""
        dialogue = self.get_dialogue()
        
        if option in dialogue["options"]:
            response = dialogue["options"][option]
            
            # Update dialogue state if needed
            if "next" in response:
                self.current_dialogue = response["next"]
            
            # Handle quest progression
            if "quest_progress" in response and self.quest:
                # Implement quest progression logic
                pass
            
            # Handle relationship changes
            if "relationship" in response:
                self.relationship += response["relationship"]
                
            return response["text"]
        
        return "Invalid response."
    
    def to_dict(self) -> Dict:
        """Convert NPC to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dialogue": self.dialogue,
            "current_dialogue": self.current_dialogue,
            "quest": self.quest,
            "shop_inventory": self.shop_inventory,
            "faction": self.faction,
            "met": self.met,
            "relationship": self.relationship
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        """Create an NPC from dictionary data."""
        npc = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            dialogue=data["dialogue"],
            quest=data["quest"],
            shop_inventory=data["shop_inventory"],
            faction=data["faction"]
        )
        npc.current_dialogue = data["current_dialogue"]
        npc.met = data["met"]
        npc.relationship = data["relationship"]
        return npc

class Player:
    def __init__(self, name: str, character_class: str, level: int = 1):
        self.name = name
        self.character_class = character_class
        self.level = level
        self.essence = 0  # Currency
        self.lost_essence = 0  # Lost on death
        self.lost_essence_location = None
        
        # Initialize stats based on class
        if character_class == "Warrior":
            self.max_hp = 100
            self.max_stamina = 80
            self.strength = 14
            self.dexterity = 9
            self.intelligence = 7
            self.faith = 8
            self.vitality = 12
            self.endurance = 10
        elif character_class == "Knight":
            self.max_hp = 90
            self.max_stamina = 90
            self.strength = 12
            self.dexterity = 12
            self.intelligence = 9
            self.faith = 11
            self.vitality = 10
            self.endurance = 11
        elif character_class == "Pyromancer":
            self.max_hp = 80
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 12
            self.faith = 14
            self.vitality = 8
            self.endurance = 9
        elif character_class == "Thief":
            self.max_hp = 75
            self.max_stamina = 100
            self.strength = 9
            self.dexterity = 14
            self.intelligence = 10
            self.faith = 8
            self.vitality = 9
            self.endurance = 14
        else:  # Default
            self.max_hp = 85
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 10
            self.faith = 10
            self.vitality = 10
            self.endurance = 10
        
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.inventory = []
        self.equipment = {
            "weapon": None,
            "shield": None,
            "armor": None,
            "ring1": None,
            "ring2": None,
            "amulet": None
        }
        self.estus_flask = {
            "current": 3,
            "max": 3
        }
        self.current_location = "highcastle_entrance"
        self.quests = {}
        self.discovered_locations = set()
        self.killed_enemies = {}
        self.stance = "balanced"  # balanced, aggressive, defensive
    
    def heal(self, amount: int) -> int:
        """Heal the player and return amount healed."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def restore_stamina(self, amount: int) -> int:
        """Restore stamina and return amount restored."""
        old_stamina = self.stamina
        self.stamina = min(self.max_stamina, self.stamina + amount)
        return self.stamina - old_stamina
    
    def use_estus(self) -> bool:
        """Use an estus flask charge to heal."""
        if self.estus_flask["current"] <= 0:
            return False
        
        self.estus_flask["current"] -= 1
        heal_amount = int(self.max_hp * 0.4)  # Heal 40% of max HP
        self.heal(heal_amount)
        return True
    
    def rest_at_beacon(self):
        """Rest at a beacon to restore HP, stamina, and estus."""
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.estus_flask["current"] = self.estus_flask["max"]
    
    def add_item(self, item: Item) -> bool:
        """Add an item to inventory. Return True if successful."""
        # Check if the item is stackable and exists in inventory
        if item.quantity > 1:
            for inv_item in self.inventory:
                if inv_item.id == item.id:
                    inv_item.quantity += item.quantity
                    return True
                    
        self.inventory.append(item)
        return True
    
    def remove_item(self, item: Item) -> bool:
        """Remove an item from inventory. Return True if successful."""
        for i, inv_item in enumerate(self.inventory):
            if inv_item.id == item.id:
                if inv_item.quantity > 1:
                    inv_item.quantity -= 1
                    return True
                else:
                    self.inventory.pop(i)
                    return True
        return False
    
    def equip_item(self, item: Item) -> str:
        """Equip an item. Return result message."""
        if not item.equippable:
            return f"You cannot equip {item.name}."
            
        # Determine equipment slot
        slot = None
        if item.item_type == "weapon":
            slot = "weapon"
        elif item.item_type == "shield":
            slot = "shield"
        elif item.item_type == "armor":
            slot = "armor"
        elif item.item_type == "ring":
            # Check if ring slots are available
            if self.equipment["ring1"] is None:
                slot = "ring1"
            elif self.equipment["ring2"] is None:
                slot = "ring2"
            else:
                return "You cannot equip more rings."
        elif item.item_type == "amulet":
            slot = "amulet"
        else:
            return f"Cannot equip {item.name}."
            
        # Unequip current item in that slot if any
        if self.equipment[slot] is not None:
            self.equipment[slot].equipped = False
            
        # Equip new item
        self.equipment[slot] = item
        item.equipped = True
        
        return f"You equipped {item.name}."
    
    def unequip_item(self, slot: str) -> str:
        """Unequip an item from specified slot. Return result message."""
        if slot not in self.equipment or self.equipment[slot] is None:
            return f"Nothing equipped in {slot}."
            
        item = self.equipment[slot]
        item.equipped = False
        self.equipment[slot] = None
        
        return f"You unequipped {item.name}."
    
    def get_attack_power(self) -> int:
        """Calculate the player's attack power."""
        base_attack = self.strength // 2
        
        if self.equipment["weapon"]:
            weapon_damage = self.equipment["weapon"].get_damage()
            # Apply stat scaling based on weapon type
            weapon_stats = self.equipment["weapon"].stats
            if "scaling" in weapon_stats:
                if weapon_stats["scaling"] == "strength":
                    scaling_bonus = self.strength // 3
                elif weapon_stats["scaling"] == "dexterity":
                    scaling_bonus = self.dexterity // 3
                else:
                    scaling_bonus = 0
                weapon_damage += scaling_bonus
            
            base_attack += weapon_damage
        
        # Apply stance modifiers
        if self.stance == "aggressive":
            base_attack = int(base_attack * 1.2)  # 20% more damage
        elif self.stance == "defensive":
            base_attack = int(base_attack * 0.8)  # 20% less damage
            
        return base_attack
    
    def get_defense(self) -> int:
        """Calculate the player's defense value."""
        base_defense = self.vitality // 2
        
        if self.equipment["armor"]:
            base_defense += self.equipment["armor"].stats["defense"]
            
        if self.equipment["shield"] and self.stance != "aggressive":
            base_defense += self.equipment["shield"].stats["defense"]
        
        # Apply stance modifiers
        if self.stance == "defensive":
            base_defense = int(base_defense * 1.2)  # 20% more defense
        elif self.stance == "aggressive":
            base_defense = int(base_defense * 0.8)  # 20% less defense
            
        return base_defense
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        defense = self.get_defense()
        
        # Apply resistances from equipment
        resistance_mult = 1.0
        for slot, item in self.equipment.items():
            if item and "resistance" in item.stats and damage_type in item.stats["resistance"]:
                resistance_mult -= item.stats["resistance"][damage_type] / 100.0
        
        # Ensure resistance multiplier is at least 0.2 (80% damage reduction max)
        resistance_mult = max(0.2, resistance_mult)
        
        # Calculate final damage
        damage = int(max(1, amount * resistance_mult - defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the player is dead."""
        return self.hp <= 0
    
    def die(self):
        """Handle player death."""
        # Drop essence at current location
        self.lost_essence = self.essence
        self.lost_essence_location = self.current_location
        self.essence = 0
        
        # Respawn at last beacon
        # This would be implemented in the game loop logic
    
    def recover_lost_essence(self):
        """Recover lost essence."""
        if self.lost_essence > 0:
            self.essence += self.lost_essence
            self.lost_essence = 0
            self.lost_essence_location = None
            return True
        return False
    
    def level_up(self, stat: str) -> bool:
        """Level up a stat. Return True if successful."""
        cost = self.calculate_level_cost()
        
        if self.essence < cost:
            return False
            
        self.essence -= cost
        self.level += 1
        
        # Increase the chosen stat
        if stat == "strength":
            self.strength += 1
        elif stat == "dexterity":
            self.dexterity += 1
        elif stat == "intelligence":
            self.intelligence += 1
        elif stat == "faith":
            self.faith += 1
        elif stat == "vitality":
            self.vitality += 1
            self.max_hp += 5
            self.hp += 5
        elif stat == "endurance":
            self.endurance += 1
            self.max_stamina += 5
            self.stamina += 5
        
        return True
    
    def calculate_level_cost(self) -> int:
        """Calculate the essence cost for the next level."""
        return int(100 * (1.1 ** (self.level - 1)))
    
    def use_item(self, item_index: int) -> str:
        """Use an item from inventory by index."""
        if item_index < 0 or item_index >= len(self.inventory):
            return "Invalid item index."
            
        item = self.inventory[item_index]
        
        if not item.usable:
            return f"You cannot use {item.name}."
            
        result = item.use(self)
        
        # Remove item if quantity reaches 0
        if item.quantity <= 0:
            self.inventory.pop(item_index)
            
        return result
    
    def change_stance(self, new_stance: str) -> str:
        """Change combat stance. Return result message."""
        valid_stances = ["balanced", "aggressive", "defensive"]
        
        if new_stance not in valid_stances:
            return f"Invalid stance. Choose from: {', '.join(valid_stances)}"
            
        old_stance = self.stance
        self.stance = new_stance
        
        return f"Changed stance from {old_stance} to {new_stance}."
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for saving."""
        return {
            "name": self.name,
            "character_class": self.character_class,
            "level": self.level,
            "essence": self.essence,
            "lost_essence": self.lost_essence,
            "lost_essence_location": self.lost_essence_location,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "max_stamina": self.max_stamina,
            "stamina": self.stamina,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "faith": self.faith,
            "vitality": self.vitality,
            "endurance": self.endurance,
            "inventory": [item.to_dict() for item in self.inventory],
            "equipment": {slot: (item.to_dict() if item else None) for slot, item in self.equipment.items()},
            "estus_flask": self.estus_flask,
            "current_location": self.current_location,
            "quests": self.quests,
            "discovered_locations": list(self.discovered_locations),
            "killed_enemies": self.killed_enemies,
            "stance": self.stance
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create a player from dictionary data."""
        player = cls(
            name=data["name"],
            character_class=data["character_class"],
            level=data["level"]
        )
        player.essence = data["essence"]
        player.lost_essence = data["lost_essence"]
        player.lost_essence_location = data["lost_essence_location"]
        player.max_hp = data["max_hp"]
        player.hp = data["hp"]
        player.max_stamina = data["max_stamina"]
        player.stamina = data["stamina"]
        player.strength = data["strength"]
        player.dexterity = data["dexterity"]
        player.intelligence = data["intelligence"]
        player.faith = data["faith"]
        player.vitality = data["vitality"]
        player.endurance = data["endurance"]
        
        # Reconstruct inventory
        player.inventory = []
        for item_data in data["inventory"]:
            if item_data["item_type"] == "weapon":
                item = Weapon(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    damage=item_data["stats"]["damage"],
                    damage_type=item_data["stats"]["damage_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    special_ability=item_data["stats"].get("special_ability"),
                    two_handed=item_data["stats"].get("two_handed", False)
                )
            elif item_data["item_type"] == "armor":
                item = Armor(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    defense=item_data["stats"]["defense"],
                    armor_type=item_data["stats"]["armor_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    resistance=item_data["stats"].get("resistance")
                )
            elif item_data["item_type"] == "consumable":
                item = Consumable(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    effect=item_data["stats"],
                    value=item_data["value"],
                    weight=item_data["weight"],
                    quantity=item_data["quantity"]
                )
            else:
                item = Item.from_dict(item_data)
                
            item.quantity = item_data["quantity"]
            item.equipped = item_data["equipped"]
            player.inventory.append(item)
        
        # Reconstruct equipment
        player.equipment = {slot: None for slot in player.equipment.keys()}
        for slot, item_data in data["equipment"].items():
            if item_data:
                for item in player.inventory:
                    if item.id == item_data["id"]:
                        player.equipment[slot] = item
                        break
                        
        player.estus_flask = data["estus_flask"]
        player.current_location = data["current_location"]
        player.quests = data["quests"]
        player.discovered_locations = set(data["discovered_locations"])
        player.killed_enemies = data["killed_enemies"]
        player.stance = data["stance"]
        
        return player

class World:
    def __init__(self):
        self.locations = {}
        self.npcs = {}
        self.items = {}
        self.enemies = {}
        self.bosses = {}
        self.quests = {}
        self.active_events = set()
        self.game_state = {}
        
        # Initialize world components
        self.initialize_world()
    
    def initialize_world(self):
        """Initialize and load all world data."""
        self.load_locations()
        self.load_npcs()
        self.load_items()
        self.load_enemies()
        self.load_bosses()
        self.load_quests()
    
    def load_locations(self):
        """Load all location data."""
        # Highcastle Region
        self.locations["highcastle_entrance"] = Location(
            id="highcastle_entrance",
            name="Highcastle Gate",
            description="The towering gates of Highcastle stand before you, worn by time but still majestic. The once-bustling gatehouse is now quiet, with only a few guards maintaining their eternal vigil.",
            connections={
                "north": "highcastle_plaza",
                "east": "eastern_road",
                "west": "western_path"
            },
            enemies=["wandering_hollow", "fallen_knight"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Gate
       v S       o - You
  
  #################
  #####.....######
  ####...o...#####
  ###.........####
  ##.....+.....###
  #...............
  #...............
            """,
            first_visit_text="You arrive at the once-grand entrance to Highcastle, the last bastion of humanity in these dark times. The walls, though weathered, still stand tall against the encroaching darkness that has consumed much of Ardenvale."
        )
        
        self.locations["highcastle_plaza"] = Location(
            id="highcastle_plaza",
            name="Highcastle Central Plaza",
            description="The central plaza of Highcastle is a shadow of its former glory. Cracked fountains and weathered statues are silent witnesses to a time of prosperity long gone. A few desperate souls still wander here, clinging to routines of a life that no longer exists.",
            connections={
                "north": "highcastle_cathedral",
                "east": "eastern_district",
                "west": "western_district",
                "south": "highcastle_entrance"
            },
            enemies=["hollow_citizen", "corrupted_guard"],
            npcs=["andre_smith", "merchant_ulrich"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ###+######+####
  #...........+.#
  #.....o.......#
  #...#...#...#.#
  #.............#
  #...#...#...#.#
  ###....+....###
            """
        )
        
        self.locations["highcastle_cathedral"] = Location(
            id="highcastle_cathedral",
            name="Cathedral of the Fading Light",
            description="This once-magnificent cathedral now stands in partial ruin. Shafts of light pierce through holes in the ceiling, illuminating dust-covered pews and crumbling statues of forgotten deities. Despite its state, there is still an aura of reverence here.",
            connections={
                "south": "highcastle_plaza",
                "east": "cathedral_tower"
            },
            enemies=["cathedral_knight", "deacon_of_the_deep"],
            npcs=["sister_friede"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ########+######
  #..#.......#..#
  #...........+.#
  #.............#
  #....o........#
  #.....###.....#
  ##....+....####
            """
        )
        
        # Ashen Woods Region
        self.locations["western_path"] = Location(
            id="western_path",
            name="Western Path",
            description="A winding path leads westward from Highcastle. Once a well-traveled trade route, it is now overgrown and dangerous. The trees along the path seem to lean inward, as if watching passersby with malicious intent.",
            connections={
                "east": "highcastle_entrance",
                "west": "ashen_woods_entrance"
            },
            enemies=["wild_beast", "hollow_woodsman"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     % - Trees
       |         ~ - Water
       v S       o - You
  
  %%%%%%%%%%%    
  %%%..........
  %%%...o......
  %%%...........
  %%%...........
  %%%.......%%%%
  %%%%%%%%%%%    
            """
        )
        
        self.locations["ashen_woods_entrance"] = Location(
            id="ashen_woods_entrance",
            name="Ashen Woods Entrance",
            description="The entrance to the Ashen Woods is marked by a sudden change in the landscape. The trees here are grey and lifeless, their bark turned to ash. Wisps of smoke rise from the ground, though there is no fire to be seen.",
            connections={
                "east": "western_path",
                "west": "ashen_woods_clearing"
            },
            enemies=["ember_wolf", "ashen_treant"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         % - Trees
  W <----> E     ^ - Ash trees
       |         ~ - Water
       v S       o - You
  
  ^^^^^^^^^^^^^^
  ^^.....^^^.^^^
  ^.......o...^^
  ^............^
  ^^^..........^
  ^^^^^^^^^^^^^^
  ^^^^^^^^^^^^^^
            """
        )
        
        # Add more locations as needed...
    
    def load_npcs(self):
        """Load all NPC data."""
        self.npcs["andre_smith"] = NPC(
            id="andre_smith",
            name="Andre the Smith",
            description="A muscular blacksmith with arms like tree trunks. Despite the dark times, his eyes still hold a passionate fire for his craft. His hammer strikes rhythmically in the background.",
            dialogue={
                "default": {
                    "text": "Need something forged? Or perhaps an upgrade to that weapon of yours?",
                    "options": {
                        "1": {
                            "text": "I'd like to upgrade my weapon.",
                            "next": "upgrade"
                        },
                        "2": {
                            "text": "Tell me about yourself.",
                            "next": "about"
                        },
                        "3": {
                            "text": "What happened to this place?",
                            "next": "history"
                        },
                        "4": {
                            "text": "Do you have any work for me?",
                            "next": "quest"
                        }
                    }
                },
                "upgrade": {
                    "text": "Ah, let me see what you've got. I can work with most materials, given enough time and the right components.",
                    "options": {
                        "1": {
                            "text": "What materials do you need?",
                            "next": "materials"
                        },
                        "2": {
                            "text": "Actually, let's talk about something else.",
                            "next": "default"
                        }
                    }
                },
                "materials": {
                    "text": "For basic reinforcement, I need titanite shards. For special weapons, I might need ember essence from the Ashen Woods, or perhaps something more exotic. Bring me materials, and I'll see what I can do.",
                    "options": {
                        "1": {
                            "text": "I'll keep an eye out for those.",
                            "next": "default"
                        }
                    }
                },
                "about": {
                    "text": "Been a smith all my life. Learned from my father, who learned from his. I've seen kingdoms rise and fall, but the forge remains. As long as there are warriors who need weapons, I'll be here.",
                    "options": {
                        "1": {
                            "text": "How have you survived the hollowing?",
                            "next": "survived"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "survived": {
                    "text": "Purpose, friend. Those who hollow are those who've lost their purpose. As long as I have my hammer and anvil, I have a reason to keep going. Find your purpose, and you'll never hollow.",
                    "options": {
                        "1": {
                            "text": "That's profound wisdom.",
                            "next": "default",
                            "relationship": 5
                        }
                    }
                },
                "history": {
                    "text": "Highcastle was once the jewel of Ardenvale. When the First Flame began to fade, everything changed. The corruption spread, people hollowed, and darkness crept in. But we endure. We always do.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the First Flame.",
                            "next": "first_flame"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "first_flame": {
                    "text": "The First Flame is what brought light and disparity to our world. Heat and cold, life and death, light and dark... all because of the Flame. Now it fades, and the balance tips toward darkness. Some seek to rekindle it, others to usher in an Age of Dark. Me? I just forge.",
                    "options": {
                        "1": {
                            "text": "Can the Flame be rekindled?",
                            "next": "rekindle"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "rekindle": {
                    "text": "The old legends say it can, but at a cost. Great souls must be sacrificed to feed the Flame. The King... they say he sought another way, and look where that got us. But who knows? Maybe you'll find answers where others failed.",
                    "options": {
                        "1": {
                            "text": "I'll discover the truth.",
                            "next": "default"
                        }
                    }
                },
                "quest": {
                    "text": "As a matter of fact, I do. My old forge has run cold without proper ember. If you could venture to the Ashen Woods and bring back some ember essence, I could craft you something special.",
                    "options": {
                        "1": {
                            "text": "I'll find this ember essence for you.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "That sounds too dangerous.",
                            "next": "quest_decline"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Excellent! Look for it near what they call Ember Lake, deep in the Ashen Woods. The essence glows like a captured sunset. Careful though, the woods have grown wild and hostile since the Flame began to fade.",
                    "options": {
                        "1": {
                            "text": "I'll be careful.",
                            "next": "default",
                            "quest_progress": {"start": "ember_quest"}
                        }
                    }
                },
                "quest_decline": {
                    "text": "Fair enough. It's no small task. The offer stands if you change your mind.",
                    "options": {
                        "1": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_complete": {
                    "text": "By the Flame, you actually found it! This ember essence is perfect. Give me some time, and I'll forge you something worthy of your courage.",
                    "options": {
                        "1": {
                            "text": "Thank you, Andre.",
                            "next": "reward"
                        }
                    }
                },
                "reward": {
                    "text": "Here, take this blade. I call it the Flamebrand. The ember essence is forged into its very core. May it serve you well in the darkness ahead.",
                    "options": {
                        "1": {
                            "text": "It's beautiful. Thank you.",
                            "next": "default",
                            "quest_progress": {"complete": "ember_quest"}
                        }
                    }
                }
            },
            quest={
                "id": "ember_quest",
                "name": "The Smith's Request",
                "description": "Andre needs ember essence from the Ashen Woods to rekindle his forge.",
                "objectives": [
                    {"type": "item", "target": "ember_essence", "quantity": 1}
                ],
                "rewards": {
                    "item": "flamebrand",
                    "essence": 200
                }
            },
            shop_inventory=["reinforced_sword", "knight_shield", "ember"]
        )
        
        self.npcs["merchant_ulrich"] = NPC(
            id="merchant_ulrich",
            name="Merchant Ulrich",
            description="A hunched man with a perpetual nervous twitch. His eyes dart about constantly, and his fingers fidget with the hem of his tattered cloak. Despite his appearance, he has somehow managed to maintain a stock of rare goods.",
            dialogue={
                "default": {
                    "text": "Ah, a customer! Rare sight these days. Looking to trade? I've got wares from all corners of Ardenvale, before... well, before everything went to ruin.",
                    "options": {
                        "1": {
                            "text": "Show me what you have for sale.",
                            "next": "shop"
                        },
                        "2": {
                            "text": "Any rumors lately?",
                            "next": "rumors"
                        },
                        "3": {
                            "text": "How do you get your merchandise?",
                            "next": "merchandise"
                        },
                        "4": {
                            "text": "I'm looking for something specific.",
                            "next": "quest_intro"
                        }
                    }
                },
                "shop": {
                    "text": "Take a look, take a look! Fine goods at reasonable prices. Well, reasonable considering the state of the world.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "rumors": {
                    "text": "Rumors? Oh, I hear many things... They say the old king still wanders the Ringed Citadel, hollowed but retaining a fragment of his former self. And in the Ashen Woods, the tree shepherds have gone mad, attacking any who venture too deep.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the king.",
                            "next": "king"
                        },
                        "2": {
                            "text": "What are tree shepherds?",
                            "next": "shepherds"
                        },
                        "3": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "king": {
                    "text": "King Morgaeth was a wise ruler, once. They say he delved too deep into forbidden arts in his quest to save the kingdom from the fading of the Flame. Now he's neither dead nor truly alive... a hollow shell of royalty.",
                    "options": {
                        "1": {
                            "text": "What forbidden arts did he study?",
                            "next": "forbidden_arts"
                        },
                        "2": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        }
                    }
                },
                "forbidden_arts": {
                    "text": "They say he sought to draw power from the Abyss itself. To use darkness to preserve light, if you can imagine such madness. The royal archives might hold more answers, but none dare venture to the Ringed Citadel now.",
                    "options": {
                        "1": {
                            "text": "Interesting. Thank you for the information.",
                            "next": "default",
                            "quest_progress": {"hint": "kings_fall"}
                        }
                    }
                },
                "shepherds": {
                    "text": "Ancient creatures, like walking trees but with awareness. They tended the forests for millennia in peace. The corruption has twisted them, made them violent. A shame. They were magnificent beings.",
                    "options": {
                        "1": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "merchandise": {
                    "text": "Ah, professional secrets! *winks nervously* Let's just say I have... arrangements with certain brave souls who venture where others fear to tread. They bring me goods, I give them essence, everyone profits!",
                    "options": {
                        "1": {
                            "text": "Sounds dangerous.",
                            "next": "dangerous"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dangerous": {
                    "text": "Dangerous? *laughs shakily* My friend, everything is dangerous now. At least my suppliers choose their danger. Most of them return... some of the time.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "quest_intro": {
                    "text": "Something specific? *eyes narrow with interest* I might have what you need, or know where to find it. What are you looking for?",
                    "options": {
                        "1": {
                            "text": "I need access to the Ringed Citadel.",
                            "next": "quest_citadel"
                        },
                        "2": {
                            "text": "Just browsing, actually.",
                            "next": "default"
                        }
                    }
                },
                "quest_citadel": {
                    "text": "*lowers voice* The Citadel? Not many seek to go there willingly. *glances around nervously* I might know of a way, but it will cost you. Not just essence, but a favor.",
                    "options": {
                        "1": {
                            "text": "What kind of favor?",
                            "next": "quest_details"
                        },
                        "2": {
                            "text": "Never mind, too risky.",
                            "next": "default"
                        }
                    }
                },
                "quest_details": {
                    "text": "One of my suppliers ventured into the Blighted Marshes east of here. Never returned. Carried a signet ring I need back. Find it, and I'll give you what you need to enter the Citadel.",
                    "options": {
                        "1": {
                            "text": "I'll find your ring.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Good, good. The marshes are treacherous, but look for a broken cart near the eastern path. That's where my supplier was headed. The ring has a blue stone, can't miss it.",
                    "options": {
                        "1": {
                            "text": "I'll return when I have it.",
                            "next": "default",
                            "quest_progress": {"start": "signet_quest"}
                        }
                    }
                },
                "quest_complete": {
                    "*eyes widen* You found it! And lived to tell the tale! I'm impressed. As promised, here's what you need—a royal seal. It will grant you passage through the outer gates of the Ringed Citadel.",
                    "options": {
                        "1": {
                            "text": "Thank you for your help.",
                            "next": "default",
                            "quest_progress": {"complete": "signet_quest"}
                        }
                    }
                }
            },
            quest={
                "id": "signet_quest",
                "name": "The Merchant's Signet",
                "description": "Find Ulrich's missing signet ring in the Blighted Marshes.",
                "objectives": [
                    {"type": "item", "target": "blue_signet", "quantity": 1}
                ],
                "rewards": {
                    "item": "royal_seal",
                    "essence": 300
                }
            },
            shop_inventory=["estus_shard", "life_gem", "homeward_bone", "green_blossom"]
        )
        
        self.npcs["sister_friede"] = NPC(
            id="sister_friede",
            name="Sister Friede",
            description="A tall, slender woman in white robes that seem untouched by the grime and decay around her. Her face is partially obscured by a hood, but you can see her pale skin and piercing blue eyes. She moves with eerie grace.",
            dialogue={
                "default": {
                    "text": "Ashen One, why do you disturb this sanctuary? This is a place of quiet reflection, not for those who would perpetuate a doomed cycle.",
                    "options": {
                        "1": {
                            "text": "I seek guidance.",
                            "next": "guidance"
                        },
                        "2": {
                            "text": "What cycle do you speak of?",
                            "next": "cycle"
                        },
                        "3": {
                            "text": "Who are you?",
                            "next": "identity"
                        },
                        "4": {
                            "text": "Are you in danger here?",
                            "next": "quest_intro"
                        }
                    }
                },
                "guidance": {
                    "text": "Guidance? *soft laugh* The path ahead is shrouded for all of us. But if you must continue your journey, seek the depths of the Ashen Woods. There lies an ancient tree shepherd who remembers the time before corruption. His wisdom may aid you, if he doesn't kill you first.",
                    "options": {
                        "1": {
                            "text": "Thank you for the information.",
                            "next": "default"
                        },
                        "2": {
                            "text": "Why would he help me?",
                            "next": "help"
                        }
                    }
                },
                "help": {
                    "text": "He wouldn't, not willingly. But in his madness, truths slip out between attempts to end your life. Listen carefully... if you survive long enough to hear anything at all.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "cycle": {
                    "text": "The endless cycle of Light and Dark. For eons, the First Flame has been rekindled when it begins to fade, postponing the Age of Dark that is our birthright. Each rekindling only makes the inevitable collapse more devastating.",
                    "options": {
                        "1": {
                            "text": "You want the Flame to fade?",
                            "next": "fade"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "fade": {
                    "text": "*her eyes narrow slightly* I want what is natural. All fires eventually burn out. Fighting this truth has brought us to this state of perpetual decay. Let it end, and something new may begin.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "identity": {
                    "text": "I am simply a watcher. I've seen kingdoms rise and fall, flames kindle and fade. Now I wait here, in this broken cathedral, observing the final gasps of a dying age.",
                    "options": {
                        "1": {
                            "text": "You speak as if you're ancient.",
                            "next": "ancient"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "ancient": {
                    "text": "*she smiles enigmatically* Time loses meaning when you've witnessed enough cycles. But enough about me. What will you do, Ashen One? Perpetuate this dying world, or help usher in something new?",
                    "options": {
                        "1": {
                            "text": "I'll restore the Flame.",
                            "next": "restore",
                            "relationship": -10
                        },
                        "2": {
                            "text": "Perhaps the Dark should have its time.",
                            "next": "dark",
                            "relationship": 10
                        },
                        "3": {
                            "text": "I haven't decided yet.",
                            "next": "undecided"
                        }
                    }
                },
                "restore": {
                    "text": "*her expression hardens* Then you are no different from the others. Go your way, Ashen One. May you find what you seek... and understand its true cost.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dark": {
                    "text": "*she studies you with new interest* Perhaps there is wisdom in you after all. The Dark is not to be feared, but embraced as part of the natural order. Remember this when your resolve is tested.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "undecided": {
                    "text": "Indecision is... understandable. The weight of such choices is immense. Reflect carefully, Ashen One. Not all is as it seems in Ardenvale.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "quest_intro": {
                    "*she seems surprised by your concern* No, not from the hollowed ones. They avoid this place. But there is a matter that... troubles me. The cathedral's sacred chalice has been stolen, taken to the bell tower by one who has fallen far from grace.",
                    "options": {
                        "1": {
                            "text": "I could retrieve it for you.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "Why is the chalice important?",
                            "next": "chalice_importance"
                        }
                    }
                },
                "chalice_importance": {
                    "text": "It contains old knowledge, symbols of both light and dark in perfect balance. In the wrong hands, this knowledge could upset the natural order, prolong this agonizing age of transition.",
                    "options": {
                        "1": {
                            "text": "I'll retrieve the chalice.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Your offer is... unexpected. The thief is a former deacon, now corrupted beyond recognition. Ascend to the bell tower, but be wary—he will not surrender the chalice willingly.",
                    "options": {
                        "1": {
                            "text": "I'll be careful.",
                            "next": "default",
                            "quest_progress": {"start": "chalice_quest"}
                        }
                    }
                },
                "quest_complete": {
                    "*her eyes widen slightly as you present the chalice* You succeeded where others would have failed. The balance is preserved, for now. Please, take this talisman as a token of my... gratitude. It bears an old symbol of the dark.",
                    "options": {
                        "1": {
                            "text": "Thank you, Sister Friede.",
                            "next": "default",
                            "quest_progress": {"complete": "chalice_quest"},
                            "relationship": 15
                        }
                    }
                }
            },
            quest={
                "id": "chalice_quest",
                "name": "The Sacred Chalice",
                "description": "Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
                "objectives": [
                    {"type": "item", "target": "sacred_chalice", "quantity": 1}
                ],
                "rewards": {
                    "item": "dark_talisman",
                    "essence": 350,
                    "faction": "Children of Dark",
                    "reputation": 15
                }
            },
            faction="Children of Dark"
        )
    
    def load_items(self):
        """Load all item data."""
        # Weapons
        self.items["reinforced_sword"] = Weapon(
            id="reinforced_sword",
            name="Reinforced Longsword",
            description="A sturdy longsword with reinforced steel. Reliable and well-balanced.",
            damage=15,
            damage_type="physical",
            weight=3.0,
            value=200,
            two_handed=False
        )
        
        self.items["knight_sword"] = Weapon(
            id="knight_sword",
            name="Knight's Sword",
            description="A well-crafted sword used by the knights of Highcastle. The blade bears the insignia of the royal guard.",
            damage=18,
            damage_type="physical",
            weight=3.5,
            value=300,
            two_handed=False
        )
        
        self.items["woodsman_axe"] = Weapon(
            id="woodsman_axe",
            name="Woodsman's Axe",
            description="A heavy axe used for chopping wood, now repurposed as a weapon. Slow but powerful.",
            damage=22,
            damage_type="physical",
            weight=4.5,
            value=180,
            two_handed=True
        )
        
        self.items["cathedral_greatsword"] = Weapon(
            id="cathedral_greatsword",
            name="Cathedral Greatsword",
            description="A massive sword wielded by the knights of the cathedral. Holy symbols are etched into the blade.",
            damage=26,
            damage_type="physical",
            weight=6.0,
            value=450,
            two_handed=True,
            special_ability={"name": "Holy Light", "damage": 15, "type": "holy"}
        )
        
        self.items["ember_blade"] = Weapon(
            id="ember_blade",
            name="Ember Blade",
            description="A sword forged in the heart of the Ashen Woods. The blade seems to smolder with inner heat.",
            damage=20,
            damage_type="fire",
            weight=3.0,
            value=500,
            two_handed=False,
            special_ability={"name": "Ignite", "damage": 12, "type": "fire", "duration": 3}
        )
        
        self.items["vordt_mace"] = Weapon(
            id="vordt_mace",
            name="Vordt's Frostmace",
            description="A massive mace once wielded by Vordt, Guardian of the Frost Gate. Crystals of ice form along its surface.",
            damage=30,
            damage_type="physical",
            weight=8.0,
            value=700,
            two_handed=True,
            special_ability={"name": "Frost Strike", "damage": 20, "type": "ice", "slow_effect": True}
        )
        
        self.items["kings_greatsword"] = Weapon(
            id="kings_greatsword",
            name="King's Greatsword",
            description="The royal greatsword of King Morgaeth, now tainted with dark energy. It pulses with corrupted power.",
            damage=35,
            damage_type="physical",
            weight=7.0,
            value=1000,
            two_handed=True,
            special_ability={"name": "Royal Wrath", "damage": 40, "type": "dark", "cooldown": 5}
        )
        
        # Armor
        self.items["knight_helm"] = Armor(
            id="knight_helm",
            name="Knight's Helm",
            description="A standard helmet worn by the knights of Highcastle. Provides good protection but limits visibility.",
            defense=10,
            armor_type="head",
            weight=2.0,
            value=200
        )
        
        self.items["knight_shield"] = Armor(
            id="knight_shield",
            name="Knight's Shield",
            description="A sturdy kite shield bearing the crest of Highcastle. Well-balanced for both defense and mobility.",
            defense=15,
            armor_type="shield",
            weight=3.5,
            value=250
        )
        
        self.items["rusted_shield"] = Armor(
            id="rusted_shield",
            name="Rusted Shield",
            description="A worn shield that has seen better days. Despite the rust, it still offers adequate protection.",
            defense=8,
            armor_type="shield",
            weight=3.0,
            value=100
        )
        
        self.items["cathedral_plate"] = Armor(
            id="cathedral_plate",
            name="Cathedral Plate Armor",
            description="Heavy armor worn by the elite knights of the cathedral. Ornate religious symbols adorn the breastplate.",
            defense=25,
            armor_type="chest",
            weight=8.0,
            value=500,
            resistance={"dark": 15}
        )
        
        self.items["deacon_robes"] = Armor(
            id="deacon_robes",
            name="Deacon's Robes",
            description="Dark robes worn by the deacons of the cathedral. Offers little physical protection but imbued with arcane resistance.",
            defense=5,
            armor_type="chest",
            weight=1.5,
            value=300,
            resistance={"magic": 20, "fire": 10}
        )
        
        self.items["frost_knight_armor"] = Armor(
            id="frost_knight_armor",
            name="Frost Knight Armor",
            description="Armor coated in a permanent layer of frost. Extremely heavy but offers exceptional protection.",
            defense=30,
            armor_type="chest",
            weight=12.0,
            value=800,
            resistance={"fire": 25, "ice": -10}  # Vulnerable to ice
        )
        
        self.items["hollowed_crown"] = Armor(
            id="hollowed_crown",
            name="Hollowed Crown",
            description="The tarnished crown of King Morgaeth. Dark energy swirls within its jewels.",
            defense=12,
            armor_type="head",
            weight=1.0,
            value=1200,
            resistance={"dark": 30, "holy": -25}  # Vulnerable to holy
        )
        
        # Consumables
        self.items["soul_remnant"] = Consumable(
            id="soul_remnant",
            name="Soul Remnant",
            description="A fragment of essence that can be consumed to restore a small amount of health.",
            effect={"healing": 15},
            value=10,
            quantity=1
        )
        
        self.items["life_gem"] = Consumable(
            id="life_gem",
            name="Life Gem",
            description="A crystal that slowly restores health when crushed and consumed.",
            effect={"healing": 30, "over_time": True, "duration": 5},
            value=100,
            quantity=1
        )
        
        self.items["ember"] = Consumable(
            id="ember",
            name="Ember",
            description="A warm ember that temporarily boosts maximum health when consumed.",
            effect={"max_health_boost": 20, "duration": 180},
            value=150,
            quantity=1
        )
        
        self.items["green_blossom"] = Consumable(
            id="green_blossom",
            name="Green Blossom",
            description="A fragrant green herb that temporarily boosts stamina regeneration.",
            effect={"stamina_regen": 20, "duration": 60},
            value=120,
            quantity=1
        )
        
        self.items["estus_shard"] = Item(
            id="estus_shard",
            name="Estus Shard",
            description="A fragment of an Estus Flask. Can be used to increase the number of uses for your Estus Flask.",
            item_type="key",
            value=500,
            usable=True
        )
        
        self.items["homeward_bone"] = Item(
            id="homeward_bone",
            name="Homeward Bone",
            description="A charred bone that carries the scent of home. Use to return to the last rested beacon.",
            item_type="consumable",
            value=150,
            usable=True,
            quantity=1
        )
        
        self.items["dark_residue"] = Item(
            id="dark_residue",
            name="Dark Residue",
            description="A strange, viscous substance that seems to absorb light. Used in certain crafting recipes.",
            item_type="material",
            value=50,
            usable=False,
            quantity=1
        )
        
        self.items["ember_essence"] = Item(
            id="ember_essence",
            name="Ember Essence",
            description="A concentrated form of fire energy. Warm to the touch and glows softly in darkness.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["frost_essence"] = Item(
            id="frost_essence",
            name="Frost Essence",
            description="Crystallized cold energy. The air around it is perpetually chilled.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["blessed_medallion"] = Item(
            id="blessed_medallion",
            name="Blessed Medallion",
            description="A holy symbol that provides protection against the dark. Slowly regenerates health when equipped.",
            item_type="amulet",
            value=300,
            equippable=True,
            stats={"health_regen": 1, "resistance": {"dark": 10}},
            quantity=1
        )
        
        self.items["dark_tome"] = Item(
            id="dark_tome",
            name="Dark Tome",
            description="An ancient book containing forbidden knowledge. The pages seem to whisper when turned.",
            item_type="catalyst",
            value=400,
            equippable=True,
            stats={"spell_boost": 15, "intelligence_scaling": True},
            quantity=1
        )
        
        self.items["royal_signet"] = Item(
            id="royal_signet",
            name="Royal Signet Ring",
            description="The royal signet of King Morgaeth. Grants authority and increases essence gained from defeating enemies.",
            item_type="ring",
            value=800,
            equippable=True,
            stats={"essence_gain": 1.2, "charisma": 5},
            quantity=1
        )
        
    def load_enemies(self):
        """Load all enemy data."""
        # Basic enemies
        self.enemies["wandering_hollow"] = Enemy(
            id="wandering_hollow",
            name="Wandering Hollow",
            description="A hollowed out corpse that wanders aimlessly. It's eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=1,
            hp=50,
            attack=10,
            defense=5,
            attack_patterns=[{"name": "Basic Attack", "damage": 10, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=10
        )
        
        self.enemies["fallen_knight"] = Enemy(
            id="fallen_knight",
            name="Fallen Knight",
            description="A knight in armor that has been hollowed out. Its eyes are dark and lifeless, reflecting the corruption that has consumed it.",
            level=2,
            hp=70,
            attack=15,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 15, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=20
        )
        
        # Add more enemies as needed...
    
    def load_bosses(self):
        """Load all boss data."""
        # Basic bosses
        self.bosses["hollow_citizen"] = Enemy(
            id="hollow_citizen",
            name="Hollow Citizen",
            description="A hollowed out citizen that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=3,
            hp=100,
            attack=20,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 20, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=30
        )
        
        self.bosses["corrupted_guard"] = Enemy(
            id="corrupted_guard",
            name="Corrupted Guard",
            description="A guard in armor that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=4,
            hp=120,
            attack=25,
            defense=15,
            attack_patterns=[{"name": "Basic Attack", "damage": 25, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=40
        )
        
        # Add more bosses as needed...
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
import os
import json
import time
import random
import pickle
import datetime
import platform
import sys
from typing import Dict, List, Optional, Tuple, Union, Any

# Constants
SAVE_DIR = "saves"
AUTOSAVE_FILE = os.path.join(SAVE_DIR, "autosave.sav")
VERSION = "1.0.0"

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# ASCII Art and UI Elements
TITLE_ART = """
  ╔═══════════════════════════════════════════════════════════╗
  ║  ▄████▄   ██▀███   █    ██  ███▄ ▄███▓ ▄▄▄▄    ██▓    ██▓ ║
  ║ ▒██▀ ▀█  ▓██ ▒ ██▒ ██  ▓██▒▓██▒▀█▀ ██▒▓█████▄ ▓██▒   ▓██▒ ║
  ║ ▒▓█    ▄ ▓██ ░▄█ ▒▓██  ▒██░▓██    ▓██░▒██▒ ▄██▒██░   ▒██░ ║
  ║ ▒▓▓▄ ▄██▒▒██▀▀█▄  ▓▓█  ░██░▒██    ▒██ ▒██░█▀  ▒██░   ▒██░ ║
  ║ ▒ ▓███▀ ░░██▓ ▒██▒▒▒█████▓ ▒██▒   ░██▒░▓█  ▀█▓░██████░██████╗
  ║ ░ ░▒ ▒  ░░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ░ ▒░   ░  ░░▒▓███▀▒░ ▒░▓  ░ ▒░▓  ║
  ║   ░  ▒     ░▒ ░ ▒░░░▒░ ░ ░ ░  ░      ░▒░▒   ░ ░ ░ ▒  ░ ░ ▒  ║
  ║ ░          ░░   ░  ░░░ ░ ░ ░      ░    ░    ░   ░ ░    ░ ░  ║
  ║ ░ ░         ░        ░            ░    ░          ░  ░   ░  ║
  ║                           ARDENVALE                        ║
  ╚═══════════════════════════════════════════════════════════╝
                A REALM SHATTERED BY A FADING FLAME
"""

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                      ARDENVALE                            ║
╚═══════════════════════════════════════════════════════════╝
"""

DIVIDER = "═" * 70

# Utility Functions
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
        
        return {
            "player_name": save_data["player"]["name"],
            "player_level": save_data["player"]["level"],
            "location": save_data["player"]["current_location"],
            "timestamp": save_data["timestamp"],
            "version": save_data["version"]
        }
    except Exception as e:
        return {
            "error": str(e),
            "filename": filename
        }

# Game Classes
class Item:
    def __init__(self, id: str, name: str, description: str, item_type: str, value: int = 0, 
                 weight: float = 0.0, stats: Dict = None, usable: bool = False, 
                 equippable: bool = False, quantity: int = 1):
        self.id = id
        self.name = name
        self.description = description
        self.item_type = item_type  # weapon, armor, consumable, key, etc.
        self.value = value
        self.weight = weight
        self.stats = stats or {}
        self.usable = usable
        self.equippable = equippable
        self.quantity = quantity
        self.equipped = False
    
    def use(self, player) -> str:
        """Use the item and return result message."""
        if not self.usable:
            return f"You cannot use the {self.name}."
        
        # Implement item usage logic here
        result = "You used the item, but nothing happened."
        
        # Example: Healing potion
        if self.item_type == "consumable" and "healing" in self.stats:
            heal_amount = self.stats["healing"]
            player.heal(heal_amount)
            result = f"You drink the {self.name} and recover {heal_amount} health."
            self.quantity -= 1
            
        return result
    
    def to_dict(self) -> Dict:
        """Convert item to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "value": self.value,
            "weight": self.weight,
            "stats": self.stats,
            "usable": self.usable,
            "equippable": self.equippable,
            "quantity": self.quantity,
            "equipped": self.equipped
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Create an item from dictionary data."""
        item = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=data["item_type"],
            value=data["value"],
            weight=data["weight"],
            stats=data["stats"],
            usable=data["usable"],
            equippable=data["equippable"],
            quantity=data["quantity"]
        )
        item.equipped = data["equipped"]
        return item

class Weapon(Item):
    def __init__(self, id: str, name: str, description: str, damage: int, 
                 damage_type: str, weight: float, value: int, 
                 special_ability: Dict = None, two_handed: bool = False):
        stats = {
            "damage": damage,
            "damage_type": damage_type,
            "two_handed": two_handed
        }
        if special_ability:
            stats["special_ability"] = special_ability
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="weapon",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )
    
    def get_damage(self) -> int:
        """Calculate the weapon's damage."""
        base_damage = self.stats["damage"]
        return base_damage
    
    def weapon_art(self, player, target) -> str:
        """Use the weapon's special ability."""
        if "special_ability" not in self.stats:
            return "This weapon has no special ability."
        
        ability = self.stats["special_ability"]
        # Implement weapon special ability logic
        
        return f"You use {ability['name']}!"

class Armor(Item):
    def __init__(self, id: str, name: str, description: str, defense: int, 
                 armor_type: str, weight: float, value: int, 
                 resistance: Dict = None):
        stats = {
            "defense": defense,
            "armor_type": armor_type,
        }
        if resistance:
            stats["resistance"] = resistance
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="armor",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )

class Consumable(Item):
    def __init__(self, id: str, name: str, description: str, effect: Dict, 
                 value: int, weight: float = 0.1, quantity: int = 1):
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="consumable",
            value=value,
            weight=weight,
            stats=effect,
            usable=True,
            equippable=False,
            quantity=quantity
        )

class Enemy:
    def __init__(self, id: str, name: str, description: str, level: int, 
                 hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.attack_patterns = attack_patterns or []
        self.loot_table = loot_table or []
        self.essence = essence
        self.weaknesses = weaknesses or []
        self.current_pattern_index = 0
    
    def get_next_attack(self) -> Dict:
        """Get the next attack pattern in sequence."""
        if not self.attack_patterns:
            return {"name": "Basic Attack", "damage": self.attack, "type": "physical"}
        
        pattern = self.attack_patterns[self.current_pattern_index]
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.attack_patterns)
        return pattern
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        # Apply weakness multipliers
        multiplier = 1.0
        if damage_type in self.weaknesses:
            multiplier = 1.5
            
        damage = int(max(1, amount * multiplier - self.defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the enemy is dead."""
        return self.hp <= 0
    
    def drop_loot(self) -> List[Item]:
        """Generate loot drops based on loot table."""
        drops = []
        for loot_entry in self.loot_table:
            if random.random() < loot_entry["chance"]:
                # Create the item from the item database
                item_id = loot_entry["item_id"]
                item = create_item(item_id)
                if item:
                    # Set quantity if specified
                    if "quantity" in loot_entry:
                        item.quantity = random.randint(
                            loot_entry["quantity"]["min"], 
                            loot_entry["quantity"]["max"]
                        )
                    drops.append(item)
        return drops
    
    def to_dict(self) -> Dict:
        """Convert enemy to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "attack_patterns": self.attack_patterns,
            "loot_table": self.loot_table,
            "essence": self.essence,
            "weaknesses": self.weaknesses,
            "current_pattern_index": self.current_pattern_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Enemy':
        """Create an enemy from dictionary data."""
        enemy = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            level=data["level"],
            hp=data["max_hp"],
            attack=data["attack"],
            defense=data["defense"],
            attack_patterns=data["attack_patterns"],
            loot_table=data["loot_table"],
            essence=data["essence"],
            weaknesses=data["weaknesses"]
        )
        enemy.hp = data["hp"]
        enemy.current_pattern_index = data["current_pattern_index"]
        return enemy

class Boss(Enemy):
    def __init__(self, id: str, name: str, title: str, description: str, 
                 level: int, hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None,
                 phases: List[Dict] = None):
        super().__init__(
            id=id,
            name=f"{name}, {title}",
            description=description,
            level=level,
            hp=hp,
            attack=attack,
            defense=defense,
            attack_patterns=attack_patterns,
            loot_table=loot_table,
            essence=essence,
            weaknesses=weaknesses
        )
        self.phases = phases or []
        self.current_phase = 0
        self.phase_triggers = [phase["trigger"] for phase in self.phases] if phases else []
    
    def update_phase(self) -> bool:
        """Check and update boss phase based on HP. Return True if phase changed."""
        if not self.phases:
            return False
            
        # Check if we should transition to the next phase
        hp_percentage = self.hp / self.max_hp * 100
        
        for i, trigger in enumerate(self.phase_triggers):
            if hp_percentage <= trigger and i > self.current_phase:
                self.current_phase = i
                # Apply phase changes
                phase = self.phases[i]
                if "attack_patterns" in phase:
                    self.attack_patterns = phase["attack_patterns"]
                    self.current_pattern_index = 0
                if "attack_boost" in phase:
                    self.attack += phase["attack_boost"]
                if "defense_boost" in phase:
                    self.defense += phase["defense_boost"]
                if "message" in phase:
                    print_slow(phase["message"])
                    
                return True
                
        return False

class Location:
    def __init__(self, id: str, name: str, description: str, 
                 connections: Dict[str, str] = None,
                 enemies: List[str] = None,
                 items: List[str] = None,
                 npcs: List[str] = None,
                 is_beacon: bool = False,
                 map_art: str = None,
                 first_visit_text: str = None,
                 events: Dict = None):
        self.id = id
        self.name = name
        self.description = description
        self.connections = connections or {}  # Direction: location_id
        self.enemies = enemies or []  # List of enemy ids that can spawn here
        self.items = items or []  # List of item ids that can be found here
        self.npcs = npcs or []  # List of NPC ids that can be found here
        self.is_beacon = is_beacon
        self.map_art = map_art
        self.first_visit_text = first_visit_text
        self.events = events or {}  # Event triggers
        self.visited = False
    
    def get_description(self) -> str:
        """Get the location description."""
        return self.description
    
    def get_connections_string(self) -> str:
        """Get a string describing available exits."""
        if not self.connections:
            return "There are no obvious exits."
            
        exits = []
        for direction, _ in self.connections.items():
            exits.append(direction)
        
        return f"Exits: {', '.join(exits)}"
    
    def to_dict(self) -> Dict:
        """Convert location to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connections": self.connections,
            "enemies": self.enemies,
            "items": self.items,
            "npcs": self.npcs,
            "is_beacon": self.is_beacon,
            "map_art": self.map_art,
            "first_visit_text": self.first_visit_text,
            "events": self.events,
            "visited": self.visited
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        """Create a location from dictionary data."""
        location = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            connections=data["connections"],
            enemies=data["enemies"],
            items=data["items"],
            npcs=data["npcs"],
            is_beacon=data["is_beacon"],
            map_art=data["map_art"],
            first_visit_text=data["first_visit_text"],
            events=data["events"]
        )
        location.visited = data["visited"]
        return location

class NPC:
    def __init__(self, id: str, name: str, description: str, 
                 dialogue: Dict[str, Dict] = None,
                 quest: Dict = None,
                 shop_inventory: List[str] = None,
                 faction: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.dialogue = dialogue or {"default": {"text": "...", "options": {}}}
        self.current_dialogue = "default"
        self.quest = quest
        self.shop_inventory = shop_inventory or []
        self.faction = faction
        self.met = False
        self.relationship = 0  # -100 to 100
    
    def get_dialogue(self) -> Dict:
        """Get the current dialogue options."""
        return self.dialogue.get(self.current_dialogue, self.dialogue["default"])
    
    def talk(self) -> str:
        """Start a conversation with the NPC."""
        if not self.met:
            self.met = True
            return f"You meet {self.name} for the first time.\n{self.description}"
        
        return f"{self.name}: {self.get_dialogue()['text']}"
    
    def respond(self, option: str) -> str:
        """Respond to a dialogue option."""
        dialogue = self.get_dialogue()
        
        if option in dialogue["options"]:
            response = dialogue["options"][option]
            
            # Update dialogue state if needed
            if "next" in response:
                self.current_dialogue = response["next"]
            
            # Handle quest progression
            if "quest_progress" in response and self.quest:
                # Implement quest progression logic
                pass
            
            # Handle relationship changes
            if "relationship" in response:
                self.relationship += response["relationship"]
                
            return response["text"]
        
        return "Invalid response."
    
    def to_dict(self) -> Dict:
        """Convert NPC to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dialogue": self.dialogue,
            "current_dialogue": self.current_dialogue,
            "quest": self.quest,
            "shop_inventory": self.shop_inventory,
            "faction": self.faction,
            "met": self.met,
            "relationship": self.relationship
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        """Create an NPC from dictionary data."""
        npc = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            dialogue=data["dialogue"],
            quest=data["quest"],
            shop_inventory=data["shop_inventory"],
            faction=data["faction"]
        )
        npc.current_dialogue = data["current_dialogue"]
        npc.met = data["met"]
        npc.relationship = data["relationship"]
        return npc

class Player:
    def __init__(self, name: str, character_class: str, level: int = 1):
        self.name = name
        self.character_class = character_class
        self.level = level
        self.essence = 0  # Currency
        self.lost_essence = 0  # Lost on death
        self.lost_essence_location = None
        
        # Initialize stats based on class
        if character_class == "Warrior":
            self.max_hp = 100
            self.max_stamina = 80
            self.strength = 14
            self.dexterity = 9
            self.intelligence = 7
            self.faith = 8
            self.vitality = 12
            self.endurance = 10
        elif character_class == "Knight":
            self.max_hp = 90
            self.max_stamina = 90
            self.strength = 12
            self.dexterity = 12
            self.intelligence = 9
            self.faith = 11
            self.vitality = 10
            self.endurance = 11
        elif character_class == "Pyromancer":
            self.max_hp = 80
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 12
            self.faith = 14
            self.vitality = 8
            self.endurance = 9
        elif character_class == "Thief":
            self.max_hp = 75
            self.max_stamina = 100
            self.strength = 9
            self.dexterity = 14
            self.intelligence = 10
            self.faith = 8
            self.vitality = 9
            self.endurance = 14
        else:  # Default
            self.max_hp = 85
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 10
            self.faith = 10
            self.vitality = 10
            self.endurance = 10
        
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.inventory = []
        self.equipment = {
            "weapon": None,
            "shield": None,
            "armor": None,
            "ring1": None,
            "ring2": None,
            "amulet": None
        }
        self.estus_flask = {
            "current": 3,
            "max": 3
        }
        self.current_location = "highcastle_entrance"
        self.quests = {}
        self.discovered_locations = set()
        self.killed_enemies = {}
        self.stance = "balanced"  # balanced, aggressive, defensive
    
    def heal(self, amount: int) -> int:
        """Heal the player and return amount healed."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def restore_stamina(self, amount: int) -> int:
        """Restore stamina and return amount restored."""
        old_stamina = self.stamina
        self.stamina = min(self.max_stamina, self.stamina + amount)
        return self.stamina - old_stamina
    
    def use_estus(self) -> bool:
        """Use an estus flask charge to heal."""
        if self.estus_flask["current"] <= 0:
            return False
        
        self.estus_flask["current"] -= 1
        heal_amount = int(self.max_hp * 0.4)  # Heal 40% of max HP
        self.heal(heal_amount)
        return True
    
    def rest_at_beacon(self):
        """Rest at a beacon to restore HP, stamina, and estus."""
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.estus_flask["current"] = self.estus_flask["max"]
    
    def add_item(self, item: Item) -> bool:
        """Add an item to inventory. Return True if successful."""
        # Check if the item is stackable and exists in inventory
        if item.quantity > 1:
            for inv_item in self.inventory:
                if inv_item.id == item.id:
                    inv_item.quantity += item.quantity
                    return True
                    
        self.inventory.append(item)
        return True
    
    def remove_item(self, item: Item) -> bool:
        """Remove an item from inventory. Return True if successful."""
        for i, inv_item in enumerate(self.inventory):
            if inv_item.id == item.id:
                if inv_item.quantity > 1:
                    inv_item.quantity -= 1
                    return True
                else:
                    self.inventory.pop(i)
                    return True
        return False
    
    def equip_item(self, item: Item) -> str:
        """Equip an item. Return result message."""
        if not item.equippable:
            return f"You cannot equip {item.name}."
            
        # Determine equipment slot
        slot = None
        if item.item_type == "weapon":
            slot = "weapon"
        elif item.item_type == "shield":
            slot = "shield"
        elif item.item_type == "armor":
            slot = "armor"
        elif item.item_type == "ring":
            # Check if ring slots are available
            if self.equipment["ring1"] is None:
                slot = "ring1"
            elif self.equipment["ring2"] is None:
                slot = "ring2"
            else:
                return "You cannot equip more rings."
        elif item.item_type == "amulet":
            slot = "amulet"
        else:
            return f"Cannot equip {item.name}."
            
        # Unequip current item in that slot if any
        if self.equipment[slot] is not None:
            self.equipment[slot].equipped = False
            
        # Equip new item
        self.equipment[slot] = item
        item.equipped = True
        
        return f"You equipped {item.name}."
    
    def unequip_item(self, slot: str) -> str:
        """Unequip an item from specified slot. Return result message."""
        if slot not in self.equipment or self.equipment[slot] is None:
            return f"Nothing equipped in {slot}."
            
        item = self.equipment[slot]
        item.equipped = False
        self.equipment[slot] = None
        
        return f"You unequipped {item.name}."
    
    def get_attack_power(self) -> int:
        """Calculate the player's attack power."""
        base_attack = self.strength // 2
        
        if self.equipment["weapon"]:
            weapon_damage = self.equipment["weapon"].get_damage()
            # Apply stat scaling based on weapon type
            weapon_stats = self.equipment["weapon"].stats
            if "scaling" in weapon_stats:
                if weapon_stats["scaling"] == "strength":
                    scaling_bonus = self.strength // 3
                elif weapon_stats["scaling"] == "dexterity":
                    scaling_bonus = self.dexterity // 3
                else:
                    scaling_bonus = 0
                weapon_damage += scaling_bonus
            
            base_attack += weapon_damage
        
        # Apply stance modifiers
        if self.stance == "aggressive":
            base_attack = int(base_attack * 1.2)  # 20% more damage
        elif self.stance == "defensive":
            base_attack = int(base_attack * 0.8)  # 20% less damage
            
        return base_attack
    
    def get_defense(self) -> int:
        """Calculate the player's defense value."""
        base_defense = self.vitality // 2
        
        if self.equipment["armor"]:
            base_defense += self.equipment["armor"].stats["defense"]
            
        if self.equipment["shield"] and self.stance != "aggressive":
            base_defense += self.equipment["shield"].stats["defense"]
        
        # Apply stance modifiers
        if self.stance == "defensive":
            base_defense = int(base_defense * 1.2)  # 20% more defense
        elif self.stance == "aggressive":
            base_defense = int(base_defense * 0.8)  # 20% less defense
            
        return base_defense
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        defense = self.get_defense()
        
        # Apply resistances from equipment
        resistance_mult = 1.0
        for slot, item in self.equipment.items():
            if item and "resistance" in item.stats and damage_type in item.stats["resistance"]:
                resistance_mult -= item.stats["resistance"][damage_type] / 100.0
        
        # Ensure resistance multiplier is at least 0.2 (80% damage reduction max)
        resistance_mult = max(0.2, resistance_mult)
        
        # Calculate final damage
        damage = int(max(1, amount * resistance_mult - defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the player is dead."""
        return self.hp <= 0
    
    def die(self):
        """Handle player death."""
        # Drop essence at current location
        self.lost_essence = self.essence
        self.lost_essence_location = self.current_location
        self.essence = 0
        
        # Respawn at last beacon
        # This would be implemented in the game loop logic
    
    def recover_lost_essence(self):
        """Recover lost essence."""
        if self.lost_essence > 0:
            self.essence += self.lost_essence
            self.lost_essence = 0
            self.lost_essence_location = None
            return True
        return False
    
    def level_up(self, stat: str) -> bool:
        """Level up a stat. Return True if successful."""
        cost = self.calculate_level_cost()
        
        if self.essence < cost:
            return False
            
        self.essence -= cost
        self.level += 1
        
        # Increase the chosen stat
        if stat == "strength":
            self.strength += 1
        elif stat == "dexterity":
            self.dexterity += 1
        elif stat == "intelligence":
            self.intelligence += 1
        elif stat == "faith":
            self.faith += 1
        elif stat == "vitality":
            self.vitality += 1
            self.max_hp += 5
            self.hp += 5
        elif stat == "endurance":
            self.endurance += 1
            self.max_stamina += 5
            self.stamina += 5
        
        return True
    
    def calculate_level_cost(self) -> int:
        """Calculate the essence cost for the next level."""
        return int(100 * (1.1 ** (self.level - 1)))
    
    def use_item(self, item_index: int) -> str:
        """Use an item from inventory by index."""
        if item_index < 0 or item_index >= len(self.inventory):
            return "Invalid item index."
            
        item = self.inventory[item_index]
        
        if not item.usable:
            return f"You cannot use {item.name}."
            
        result = item.use(self)
        
        # Remove item if quantity reaches 0
        if item.quantity <= 0:
            self.inventory.pop(item_index)
            
        return result
    
    def change_stance(self, new_stance: str) -> str:
        """Change combat stance. Return result message."""
        valid_stances = ["balanced", "aggressive", "defensive"]
        
        if new_stance not in valid_stances:
            return f"Invalid stance. Choose from: {', '.join(valid_stances)}"
            
        old_stance = self.stance
        self.stance = new_stance
        
        return f"Changed stance from {old_stance} to {new_stance}."
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for saving."""
        return {
            "name": self.name,
            "character_class": self.character_class,
            "level": self.level,
            "essence": self.essence,
            "lost_essence": self.lost_essence,
            "lost_essence_location": self.lost_essence_location,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "max_stamina": self.max_stamina,
            "stamina": self.stamina,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "faith": self.faith,
            "vitality": self.vitality,
            "endurance": self.endurance,
            "inventory": [item.to_dict() for item in self.inventory],
            "equipment": {slot: (item.to_dict() if item else None) for slot, item in self.equipment.items()},
            "estus_flask": self.estus_flask,
            "current_location": self.current_location,
            "quests": self.quests,
            "discovered_locations": list(self.discovered_locations),
            "killed_enemies": self.killed_enemies,
            "stance": self.stance
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create a player from dictionary data."""
        player = cls(
            name=data["name"],
            character_class=data["character_class"],
            level=data["level"]
        )
        player.essence = data["essence"]
        player.lost_essence = data["lost_essence"]
        player.lost_essence_location = data["lost_essence_location"]
        player.max_hp = data["max_hp"]
        player.hp = data["hp"]
        player.max_stamina = data["max_stamina"]
        player.stamina = data["stamina"]
        player.strength = data["strength"]
        player.dexterity = data["dexterity"]
        player.intelligence = data["intelligence"]
        player.faith = data["faith"]
        player.vitality = data["vitality"]
        player.endurance = data["endurance"]
        
        # Reconstruct inventory
        player.inventory = []
        for item_data in data["inventory"]:
            if item_data["item_type"] == "weapon":
                item = Weapon(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    damage=item_data["stats"]["damage"],
                    damage_type=item_data["stats"]["damage_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    special_ability=item_data["stats"].get("special_ability"),
                    two_handed=item_data["stats"].get("two_handed", False)
                )
            elif item_data["item_type"] == "armor":
                item = Armor(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    defense=item_data["stats"]["defense"],
                    armor_type=item_data["stats"]["armor_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    resistance=item_data["stats"].get("resistance")
                )
            elif item_data["item_type"] == "consumable":
                item = Consumable(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    effect=item_data["stats"],
                    value=item_data["value"],
                    weight=item_data["weight"],
                    quantity=item_data["quantity"]
                )
            else:
                item = Item.from_dict(item_data)
                
            item.quantity = item_data["quantity"]
            item.equipped = item_data["equipped"]
            player.inventory.append(item)
        
        # Reconstruct equipment
        player.equipment = {slot: None for slot in player.equipment.keys()}
        for slot, item_data in data["equipment"].items():
            if item_data:
                for item in player.inventory:
                    if item.id == item_data["id"]:
                        player.equipment[slot] = item
                        break
                        
        player.estus_flask = data["estus_flask"]
        player.current_location = data["current_location"]
        player.quests = data["quests"]
        player.discovered_locations = set(data["discovered_locations"])
        player.killed_enemies = data["killed_enemies"]
        player.stance = data["stance"]
        
        return player

class World:
    def __init__(self):
        self.locations = {}
        self.npcs = {}
        self.items = {}
        self.enemies = {}
        self.bosses = {}
        self.quests = {}
        self.active_events = set()
        self.game_state = {}
        
        # Initialize world components
        self.initialize_world()
    
    def initialize_world(self):
        """Initialize and load all world data."""
        self.load_locations()
        self.load_npcs()
        self.load_items()
        self.load_enemies()
        self.load_bosses()
        self.load_quests()
    
    def load_locations(self):
        """Load all location data."""
        # Highcastle Region
        self.locations["highcastle_entrance"] = Location(
            id="highcastle_entrance",
            name="Highcastle Gate",
            description="The towering gates of Highcastle stand before you, worn by time but still majestic. The once-bustling gatehouse is now quiet, with only a few guards maintaining their eternal vigil.",
            connections={
                "north": "highcastle_plaza",
                "east": "eastern_road",
                "west": "western_path"
            },
            enemies=["wandering_hollow", "fallen_knight"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Gate
       v S       o - You
  
  #################
  #####.....######
  ####...o...#####
  ###.........####
  ##.....+.....###
  #...............
  #...............
            """,
            first_visit_text="You arrive at the once-grand entrance to Highcastle, the last bastion of humanity in these dark times. The walls, though weathered, still stand tall against the encroaching darkness that has consumed much of Ardenvale."
        )
        
        self.locations["highcastle_plaza"] = Location(
            id="highcastle_plaza",
            name="Highcastle Central Plaza",
            description="The central plaza of Highcastle is a shadow of its former glory. Cracked fountains and weathered statues are silent witnesses to a time of prosperity long gone. A few desperate souls still wander here, clinging to routines of a life that no longer exists.",
            connections={
                "north": "highcastle_cathedral",
                "east": "eastern_district",
                "west": "western_district",
                "south": "highcastle_entrance"
            },
            enemies=["hollow_citizen", "corrupted_guard"],
            npcs=["andre_smith", "merchant_ulrich"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ###+######+####
  #...........+.#
  #.....o.......#
  #...#...#...#.#
  #.............#
  #...#...#...#.#
  ###....+....###
            """
        )
        
        self.locations["highcastle_cathedral"] = Location(
            id="highcastle_cathedral",
            name="Cathedral of the Fading Light",
            description="This once-magnificent cathedral now stands in partial ruin. Shafts of light pierce through holes in the ceiling, illuminating dust-covered pews and crumbling statues of forgotten deities. Despite its state, there is still an aura of reverence here.",
            connections={
                "south": "highcastle_plaza",
                "east": "cathedral_tower"
            },
            enemies=["cathedral_knight", "deacon_of_the_deep"],
            npcs=["sister_friede"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ########+######
  #..#.......#..#
  #...........+.#
  #.............#
  #....o........#
  #.....###.....#
  ##....+....####
            """
        )
        
        # Ashen Woods Region
        self.locations["western_path"] = Location(
            id="western_path",
            name="Western Path",
            description="A winding path leads westward from Highcastle. Once a well-traveled trade route, it is now overgrown and dangerous. The trees along the path seem to lean inward, as if watching passersby with malicious intent.",
            connections={
                "east": "highcastle_entrance",
                "west": "ashen_woods_entrance"
            },
            enemies=["wild_beast", "hollow_woodsman"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     % - Trees
       |         ~ - Water
       v S       o - You
  
  %%%%%%%%%%%    
  %%%..........
  %%%...o......
  %%%...........
  %%%...........
  %%%.......%%%%
  %%%%%%%%%%%    
            """
        )
        
        self.locations["ashen_woods_entrance"] = Location(
            id="ashen_woods_entrance",
            name="Ashen Woods Entrance",
            description="The entrance to the Ashen Woods is marked by a sudden change in the landscape. The trees here are grey and lifeless, their bark turned to ash. Wisps of smoke rise from the ground, though there is no fire to be seen.",
            connections={
                "east": "western_path",
                "west": "ashen_woods_clearing"
            },
            enemies=["ember_wolf", "ashen_treant"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         % - Trees
  W <----> E     ^ - Ash trees
       |         ~ - Water
       v S       o - You
  
  ^^^^^^^^^^^^^^
  ^^.....^^^.^^^
  ^.......o...^^
  ^............^
  ^^^..........^
  ^^^^^^^^^^^^^^
  ^^^^^^^^^^^^^^
            """
        )
        
        # Add more locations as needed...
    
    def load_npcs(self):
        """Load all NPC data."""
        self.npcs["andre_smith"] = NPC(
            id="andre_smith",
            name="Andre the Smith",
            description="A muscular blacksmith with arms like tree trunks. Despite the dark times, his eyes still hold a passionate fire for his craft. His hammer strikes rhythmically in the background.",
            dialogue={
                "default": {
                    "text": "Need something forged? Or perhaps an upgrade to that weapon of yours?",
                    "options": {
                        "1": {
                            "text": "I'd like to upgrade my weapon.",
                            "next": "upgrade"
                        },
                        "2": {
                            "text": "Tell me about yourself.",
                            "next": "about"
                        },
                        "3": {
                            "text": "What happened to this place?",
                            "next": "history"
                        },
                        "4": {
                            "text": "Do you have any work for me?",
                            "next": "quest"
                        }
                    }
                },
                "upgrade": {
                    "text": "Ah, let me see what you've got. I can work with most materials, given enough time and the right components.",
                    "options": {
                        "1": {
                            "text": "What materials do you need?",
                            "next": "materials"
                        },
                        "2": {
                            "text": "Actually, let's talk about something else.",
                            "next": "default"
                        }
                    }
                },
                "materials": {
                    "text": "For basic reinforcement, I need titanite shards. For special weapons, I might need ember essence from the Ashen Woods, or perhaps something more exotic. Bring me materials, and I'll see what I can do.",
                    "options": {
                        "1": {
                            "text": "I'll keep an eye out for those.",
                            "next": "default"
                        }
                    }
                },
                "about": {
                    "text": "Been a smith all my life. Learned from my father, who learned from his. I've seen kingdoms rise and fall, but the forge remains. As long as there are warriors who need weapons, I'll be here.",
                    "options": {
                        "1": {
                            "text": "How have you survived the hollowing?",
                            "next": "survived"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "survived": {
                    "text": "Purpose, friend. Those who hollow are those who've lost their purpose. As long as I have my hammer and anvil, I have a reason to keep going. Find your purpose, and you'll never hollow.",
                    "options": {
                        "1": {
                            "text": "That's profound wisdom.",
                            "next": "default",
                            "relationship": 5
                        }
                    }
                },
                "history": {
                    "text": "Highcastle was once the jewel of Ardenvale. When the First Flame began to fade, everything changed. The corruption spread, people hollowed, and darkness crept in. But we endure. We always do.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the First Flame.",
                            "next": "first_flame"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "first_flame": {
                    "text": "The First Flame is what brought light and disparity to our world. Heat and cold, life and death, light and dark... all because of the Flame. Now it fades, and the balance tips toward darkness. Some seek to rekindle it, others to usher in an Age of Dark. Me? I just forge.",
                    "options": {
                        "1": {
                            "text": "Can the Flame be rekindled?",
                            "next": "rekindle"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "rekindle": {
                    "text": "The old legends say it can, but at a cost. Great souls must be sacrificed to feed the Flame. The King... they say he sought another way, and look where that got us. But who knows? Maybe you'll find answers where others failed.",
                    "options": {
                        "1": {
                            "text": "I'll discover the truth.",
                            "next": "default"
                        }
                    }
                },
                "quest": {
                    "text": "As a matter of fact, I do. My old forge has run cold without proper ember. If you could venture to the Ashen Woods and bring back some ember essence, I could craft you something special.",
                    "options": {
                        "1": {
                            "text": "I'll find this ember essence for you.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "That sounds too dangerous.",
                            "next": "quest_decline"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Excellent! Look for it near what they call Ember Lake, deep in the Ashen Woods. The essence glows like a captured sunset. Careful though, the woods have grown wild and hostile since the Flame began to fade.",
                    "options": {
                        "1": {
                            "text": "I'll be careful.",
                            "next": "default",
                            "quest_progress": {"start": "ember_quest"}
                        }
                    }
                },
                "quest_decline": {
                    "text": "Fair enough. It's no small task. The offer stands if you change your mind.",
                    "options": {
                        "1": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_complete": {
                    "text": "By the Flame, you actually found it! This ember essence is perfect. Give me some time, and I'll forge you something worthy of your courage.",
                    "options": {
                        "1": {
                            "text": "Thank you, Andre.",
                            "next": "reward"
                        }
                    }
                },
                "reward": {
                    "text": "Here, take this blade. I call it the Flamebrand. The ember essence is forged into its very core. May it serve you well in the darkness ahead.",
                    "options": {
                        "1": {
                            "text": "It's beautiful. Thank you.",
                            "next": "default",
                            "quest_progress": {"complete": "ember_quest"}
                        }
                    }
                }
            },
            quest={
                "id": "ember_quest",
                "name": "The Smith's Request",
                "description": "Andre needs ember essence from the Ashen Woods to rekindle his forge.",
                "objectives": [
                    {"type": "item", "target": "ember_essence", "quantity": 1}
                ],
                "rewards": {
                    "item": "flamebrand",
                    "essence": 200
                }
            },
            shop_inventory=["reinforced_sword", "knight_shield", "ember"]
        )
        
        self.npcs["merchant_ulrich"] = NPC(
            id="merchant_ulrich",
            name="Merchant Ulrich",
            description="A hunched man with a perpetual nervous twitch. His eyes dart about constantly, and his fingers fidget with the hem of his tattered cloak. Despite his appearance, he has somehow managed to maintain a stock of rare goods.",
            dialogue={
                "default": {
                    "text": "Ah, a customer! Rare sight these days. Looking to trade? I've got wares from all corners of Ardenvale, before... well, before everything went to ruin.",
                    "options": {
                        "1": {
                            "text": "Show me what you have for sale.",
                            "next": "shop"
                        },
                        "2": {
                            "text": "Any rumors lately?",
                            "next": "rumors"
                        },
                        "3": {
                            "text": "How do you get your merchandise?",
                            "next": "merchandise"
                        },
                        "4": {
                            "text": "I'm looking for something specific.",
                            "next": "quest_intro"
                        }
                    }
                },
                "shop": {
                    "text": "Take a look, take a look! Fine goods at reasonable prices. Well, reasonable considering the state of the world.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "rumors": {
                    "text": "Rumors? Oh, I hear many things... They say the old king still wanders the Ringed Citadel, hollowed but retaining a fragment of his former self. And in the Ashen Woods, the tree shepherds have gone mad, attacking any who venture too deep.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the king.",
                            "next": "king"
                        },
                        "2": {
                            "text": "What are tree shepherds?",
                            "next": "shepherds"
                        },
                        "3": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "king": {
                    "text": "King Morgaeth was a wise ruler, once. They say he delved too deep into forbidden arts in his quest to save the kingdom from the fading of the Flame. Now he's neither dead nor truly alive... a hollow shell of royalty.",
                    "options": {
                        "1": {
                            "text": "What forbidden arts did he study?",
                            "next": "forbidden_arts"
                        },
                        "2": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        }
                    }
                },
                "forbidden_arts": {
                    "text": "They say he sought to draw power from the Abyss itself. To use darkness to preserve light, if you can imagine such madness. The royal archives might hold more answers, but none dare venture to the Ringed Citadel now.",
                    "options": {
                        "1": {
                            "text": "Interesting. Thank you for the information.",
                            "next": "default",
                            "quest_progress": {"hint": "kings_fall"}
                        }
                    }
                },
                "shepherds": {
                    "text": "Ancient creatures, like walking trees but with awareness. They tended the forests for millennia in peace. The corruption has twisted them, made them violent. A shame. They were magnificent beings.",
                    "options": {
                        "1": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "merchandise": {
                    "text": "Ah, professional secrets! *winks nervously* Let's just say I have... arrangements with certain brave souls who venture where others fear to tread. They bring me goods, I give them essence, everyone profits!",
                    "options": {
                        "1": {
                            "text": "Sounds dangerous.",
                            "next": "dangerous"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dangerous": {
                    "text": "Dangerous? *laughs shakily* My friend, everything is dangerous now. At least my suppliers choose their danger. Most of them return... some of the time.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "quest_intro": {
                    "text": "Something specific? *eyes narrow with interest* I might have what you need, or know where to find it. What are you looking for?",
                    "options": {
                        "1": {
                            "text": "I need access to the Ringed Citadel.",
                            "next": "quest_citadel"
                        },
                        "2": {
                            "text": "Just browsing, actually.",
                            "next": "default"
                        }
                    }
                },
                "quest_citadel": {
                    "text": "*lowers voice* The Citadel? Not many seek to go there willingly. *glances around nervously* I might know of a way, but it will cost you. Not just essence, but a favor.",
                    "options": {
                        "1": {
                            "text": "What kind of favor?",
                            "next": "quest_details"
                        },
                        "2": {
                            "text": "Never mind, too risky.",
                            "next": "default"
                        }
                    }
                },
                "quest_details": {
                    "text": "One of my suppliers ventured into the Blighted Marshes east of here. Never returned. Carried a signet ring I need back. Find it, and I'll give you what you need to enter the Citadel.",
                    "options": {
                        "1": {
                            "text": "I'll find your ring.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Good, good. The marshes are treacherous, but look for a broken cart near the eastern path. That's where my supplier was headed. The ring has a blue stone, can't miss it.",
                    "options": {
                        "1": {
                            "text": "I'll return when I have it.",
                            "next": "default",
                            "quest_progress": {"start": "signet_quest"}
                        }
                    }
                },
                "quest_complete": {
                    "*eyes widen* You found it! And lived to tell the tale! I'm impressed. As promised, here's what you need—a royal seal. It will grant you passage through the outer gates of the Ringed Citadel.",
                    "options": {
                        "1": {
                            "text": "Thank you for your help.",
                            "next": "default",
                            "quest_progress": {"complete": "signet_quest"}
                        }
                    }
                }
            },
            quest={
                "id": "signet_quest",
                "name": "The Merchant's Signet",
                "description": "Find Ulrich's missing signet ring in the Blighted Marshes.",
                "objectives": [
                    {"type": "item", "target": "blue_signet", "quantity": 1}
                ],
                "rewards": {
                    "item": "royal_seal",
                    "essence": 300
                }
            },
            shop_inventory=["estus_shard", "life_gem", "homeward_bone", "green_blossom"]
        )
        
        self.npcs["sister_friede"] = NPC(
            id="sister_friede",
            name="Sister Friede",
            description="A tall, slender woman in white robes that seem untouched by the grime and decay around her. Her face is partially obscured by a hood, but you can see her pale skin and piercing blue eyes. She moves with eerie grace.",
            dialogue={
                "default": {
                    "text": "Ashen One, why do you disturb this sanctuary? This is a place of quiet reflection, not for those who would perpetuate a doomed cycle.",
                    "options": {
                        "1": {
                            "text": "I seek guidance.",
                            "next": "guidance"
                        },
                        "2": {
                            "text": "What cycle do you speak of?",
                            "next": "cycle"
                        },
                        "3": {
                            "text": "Who are you?",
                            "next": "identity"
                        },
                        "4": {
                            "text": "Are you in danger here?",
                            "next": "quest_intro"
                        }
                    }
                },
                "guidance": {
                    "text": "Guidance? *soft laugh* The path ahead is shrouded for all of us. But if you must continue your journey, seek the depths of the Ashen Woods. There lies an ancient tree shepherd who remembers the time before corruption. His wisdom may aid you, if he doesn't kill you first.",
                    "options": {
                        "1": {
                            "text": "Thank you for the information.",
                            "next": "default"
                        },
                        "2": {
                            "text": "Why would he help me?",
                            "next": "help"
                        }
                    }
                },
                "help": {
                    "text": "He wouldn't, not willingly. But in his madness, truths slip out between attempts to end your life. Listen carefully... if you survive long enough to hear anything at all.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "cycle": {
                    "text": "The endless cycle of Light and Dark. For eons, the First Flame has been rekindled when it begins to fade, postponing the Age of Dark that is our birthright. Each rekindling only makes the inevitable collapse more devastating.",
                    "options": {
                        "1": {
                            "text": "You want the Flame to fade?",
                            "next": "fade"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "fade": {
                    "text": "*her eyes narrow slightly* I want what is natural. All fires eventually burn out. Fighting this truth has brought us to this state of perpetual decay. Let it end, and something new may begin.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "identity": {
                    "text": "I am simply a watcher. I've seen kingdoms rise and fall, flames kindle and fade. Now I wait here, in this broken cathedral, observing the final gasps of a dying age.",
                    "options": {
                        "1": {
                            "text": "You speak as if you're ancient.",
                            "next": "ancient"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "ancient": {
                    "text": "*she smiles enigmatically* Time loses meaning when you've witnessed enough cycles. But enough about me. What will you do, Ashen One? Perpetuate this dying world, or help usher in something new?",
                    "options": {
                        "1": {
                            "text": "I'll restore the Flame.",
                            "next": "restore",
                            "relationship": -10
                        },
                        "2": {
                            "text": "Perhaps the Dark should have its time.",
                            "next": "dark",
                            "relationship": 10
                        },
                        "3": {
                            "text": "I haven't decided yet.",
                            "next": "undecided"
                        }
                    }
                },
                "restore": {
                    "text": "*her expression hardens* Then you are no different from the others. Go your way, Ashen One. May you find what you seek... and understand its true cost.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dark": {
                    "text": "*she studies you with new interest* Perhaps there is wisdom in you after all. The Dark is not to be feared, but embraced as part of the natural order. Remember this when your resolve is tested.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "undecided": {
                    "text": "Indecision is... understandable. The weight of such choices is immense. Reflect carefully, Ashen One. Not all is as it seems in Ardenvale.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "quest_intro": {
                    "*she seems surprised by your concern* No, not from the hollowed ones. They avoid this place. But there is a matter that... troubles me. The cathedral's sacred chalice has been stolen, taken to the bell tower by one who has fallen far from grace.",
                    "options": {
                        "1": {
                            "text": "I could retrieve it for you.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "Why is the chalice important?",
                            "next": "chalice_importance"
                        }
                    }
                },
                "chalice_importance": {
                    "text": "It contains old knowledge, symbols of both light and dark in perfect balance. In the wrong hands, this knowledge could upset the natural order, prolong this agonizing age of transition.",
                    "options": {
                        "1": {
                            "text": "I'll retrieve the chalice.",
                            "next": "quest_accept"
                        },
                        "2": {
                            "text": "I'll think about it.",
                            "next": "default"
                        }
                    }
                },
                "quest_accept": {
                    "text": "Your offer is... unexpected. The thief is a former deacon, now corrupted beyond recognition. Ascend to the bell tower, but be wary—he will not surrender the chalice willingly.",
                    "options": {
                        "1": {
                            "text": "I'll be careful.",
                            "next": "default",
                            "quest_progress": {"start": "chalice_quest"}
                        }
                    }
                },
                "quest_complete": {
                    "*her eyes widen slightly as you present the chalice* You succeeded where others would have failed. The balance is preserved, for now. Please, take this talisman as a token of my... gratitude. It bears an old symbol of the dark.",
                    "options": {
                        "1": {
                            "text": "Thank you, Sister Friede.",
                            "next": "default",
                            "quest_progress": {"complete": "chalice_quest"},
                            "relationship": 15
                        }
                    }
                }
            },
            quest={
                "id": "chalice_quest",
                "name": "The Sacred Chalice",
                "description": "Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
                "objectives": [
                    {"type": "item", "target": "sacred_chalice", "quantity": 1}
                ],
                "rewards": {
                    "item": "dark_talisman",
                    "essence": 350,
                    "faction": "Children of Dark",
                    "reputation": 15
                }
            },
            faction="Children of Dark"
        )
    
    def load_items(self):
        """Load all item data."""
        # Weapons
        self.items["reinforced_sword"] = Weapon(
            id="reinforced_sword",
            name="Reinforced Longsword",
            description="A sturdy longsword with reinforced steel. Reliable and well-balanced.",
            damage=15,
            damage_type="physical",
            weight=3.0,
            value=200,
            two_handed=False
        )
        
        self.items["knight_sword"] = Weapon(
            id="knight_sword",
            name="Knight's Sword",
            description="A well-crafted sword used by the knights of Highcastle. The blade bears the insignia of the royal guard.",
            damage=18,
            damage_type="physical",
            weight=3.5,
            value=300,
            two_handed=False
        )
        
        self.items["woodsman_axe"] = Weapon(
            id="woodsman_axe",
            name="Woodsman's Axe",
            description="A heavy axe used for chopping wood, now repurposed as a weapon. Slow but powerful.",
            damage=22,
            damage_type="physical",
            weight=4.5,
            value=180,
            two_handed=True
        )
        
        self.items["cathedral_greatsword"] = Weapon(
            id="cathedral_greatsword",
            name="Cathedral Greatsword",
            description="A massive sword wielded by the knights of the cathedral. Holy symbols are etched into the blade.",
            damage=26,
            damage_type="physical",
            weight=6.0,
            value=450,
            two_handed=True,
            special_ability={"name": "Holy Light", "damage": 15, "type": "holy"}
        )
        
        self.items["ember_blade"] = Weapon(
            id="ember_blade",
            name="Ember Blade",
            description="A sword forged in the heart of the Ashen Woods. The blade seems to smolder with inner heat.",
            damage=20,
            damage_type="fire",
            weight=3.0,
            value=500,
            two_handed=False,
            special_ability={"name": "Ignite", "damage": 12, "type": "fire", "duration": 3}
        )
        
        self.items["vordt_mace"] = Weapon(
            id="vordt_mace",
            name="Vordt's Frostmace",
            description="A massive mace once wielded by Vordt, Guardian of the Frost Gate. Crystals of ice form along its surface.",
            damage=30,
            damage_type="physical",
            weight=8.0,
            value=700,
            two_handed=True,
            special_ability={"name": "Frost Strike", "damage": 20, "type": "ice", "slow_effect": True}
        )
        
        self.items["kings_greatsword"] = Weapon(
            id="kings_greatsword",
            name="King's Greatsword",
            description="The royal greatsword of King Morgaeth, now tainted with dark energy. It pulses with corrupted power.",
            damage=35,
            damage_type="physical",
            weight=7.0,
            value=1000,
            two_handed=True,
            special_ability={"name": "Royal Wrath", "damage": 40, "type": "dark", "cooldown": 5}
        )
        
        # Armor
        self.items["knight_helm"] = Armor(
            id="knight_helm",
            name="Knight's Helm",
            description="A standard helmet worn by the knights of Highcastle. Provides good protection but limits visibility.",
            defense=10,
            armor_type="head",
            weight=2.0,
            value=200
        )
        
        self.items["knight_shield"] = Armor(
            id="knight_shield",
            name="Knight's Shield",
            description="A sturdy kite shield bearing the crest of Highcastle. Well-balanced for both defense and mobility.",
            defense=15,
            armor_type="shield",
            weight=3.5,
            value=250
        )
        
        self.items["rusted_shield"] = Armor(
            id="rusted_shield",
            name="Rusted Shield",
            description="A worn shield that has seen better days. Despite the rust, it still offers adequate protection.",
            defense=8,
            armor_type="shield",
            weight=3.0,
            value=100
        )
        
        self.items["cathedral_plate"] = Armor(
            id="cathedral_plate",
            name="Cathedral Plate Armor",
            description="Heavy armor worn by the elite knights of the cathedral. Ornate religious symbols adorn the breastplate.",
            defense=25,
            armor_type="chest",
            weight=8.0,
            value=500,
            resistance={"dark": 15}
        )
        
        self.items["deacon_robes"] = Armor(
            id="deacon_robes",
            name="Deacon's Robes",
            description="Dark robes worn by the deacons of the cathedral. Offers little physical protection but imbued with arcane resistance.",
            defense=5,
            armor_type="chest",
            weight=1.5,
            value=300,
            resistance={"magic": 20, "fire": 10}
        )
        
        self.items["frost_knight_armor"] = Armor(
            id="frost_knight_armor",
            name="Frost Knight Armor",
            description="Armor coated in a permanent layer of frost. Extremely heavy but offers exceptional protection.",
            defense=30,
            armor_type="chest",
            weight=12.0,
            value=800,
            resistance={"fire": 25, "ice": -10}  # Vulnerable to ice
        )
        
        self.items["hollowed_crown"] = Armor(
            id="hollowed_crown",
            name="Hollowed Crown",
            description="The tarnished crown of King Morgaeth. Dark energy swirls within its jewels.",
            defense=12,
            armor_type="head",
            weight=1.0,
            value=1200,
            resistance={"dark": 30, "holy": -25}  # Vulnerable to holy
        )
        
        # Consumables
        self.items["soul_remnant"] = Consumable(
            id="soul_remnant",
            name="Soul Remnant",
            description="A fragment of essence that can be consumed to restore a small amount of health.",
            effect={"healing": 15},
            value=10,
            quantity=1
        )
        
        self.items["life_gem"] = Consumable(
            id="life_gem",
            name="Life Gem",
            description="A crystal that slowly restores health when crushed and consumed.",
            effect={"healing": 30, "over_time": True, "duration": 5},
            value=100,
            quantity=1
        )
        
        self.items["ember"] = Consumable(
            id="ember",
            name="Ember",
            description="A warm ember that temporarily boosts maximum health when consumed.",
            effect={"max_health_boost": 20, "duration": 180},
            value=150,
            quantity=1
        )
        
        self.items["green_blossom"] = Consumable(
            id="green_blossom",
            name="Green Blossom",
            description="A fragrant green herb that temporarily boosts stamina regeneration.",
            effect={"stamina_regen": 20, "duration": 60},
            value=120,
            quantity=1
        )
        
        self.items["estus_shard"] = Item(
            id="estus_shard",
            name="Estus Shard",
            description="A fragment of an Estus Flask. Can be used to increase the number of uses for your Estus Flask.",
            item_type="key",
            value=500,
            usable=True
        )
        
        self.items["homeward_bone"] = Item(
            id="homeward_bone",
            name="Homeward Bone",
            description="A charred bone that carries the scent of home. Use to return to the last rested beacon.",
            item_type="consumable",
            value=150,
            usable=True,
            quantity=1
        )
        
        self.items["dark_residue"] = Item(
            id="dark_residue",
            name="Dark Residue",
            description="A strange, viscous substance that seems to absorb light. Used in certain crafting recipes.",
            item_type="material",
            value=50,
            usable=False,
            quantity=1
        )
        
        self.items["ember_essence"] = Item(
            id="ember_essence",
            name="Ember Essence",
            description="A concentrated form of fire energy. Warm to the touch and glows softly in darkness.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["frost_essence"] = Item(
            id="frost_essence",
            name="Frost Essence",
            description="Crystallized cold energy. The air around it is perpetually chilled.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["blessed_medallion"] = Item(
            id="blessed_medallion",
            name="Blessed Medallion",
            description="A holy symbol that provides protection against the dark. Slowly regenerates health when equipped.",
            item_type="amulet",
            value=300,
            equippable=True,
            stats={"health_regen": 1, "resistance": {"dark": 10}},
            quantity=1
        )
        
        self.items["dark_tome"] = Item(
            id="dark_tome",
            name="Dark Tome",
            description="An ancient book containing forbidden knowledge. The pages seem to whisper when turned.",
            item_type="catalyst",
            value=400,
            equippable=True,
            stats={"spell_boost": 15, "intelligence_scaling": True},
            quantity=1
        )
        
        self.items["royal_signet"] = Item(
            id="royal_signet",
            name="Royal Signet Ring",
            description="The royal signet of King Morgaeth. Grants authority and increases essence gained from defeating enemies.",
            item_type="ring",
            value=800,
            equippable=True,
            stats={"essence_gain": 1.2, "charisma": 5},
            quantity=1
        )
        
    def load_enemies(self):
        """Load all enemy data."""
        # Basic enemies
        self.enemies["wandering_hollow"] = Enemy(
            id="wandering_hollow",
            name="Wandering Hollow",
            description="A hollowed out corpse that wanders aimlessly. It's eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=1,
            hp=50,
            attack=10,
            defense=5,
            attack_patterns=[{"name": "Basic Attack", "damage": 10, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=10
        )
        
        self.enemies["fallen_knight"] = Enemy(
            id="fallen_knight",
            name="Fallen Knight",
            description="A knight in armor that has been hollowed out. Its eyes are dark and lifeless, reflecting the corruption that has consumed it.",
            level=2,
            hp=70,
            attack=15,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 15, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=20
        )
        
        # Add more enemies as needed...
    
    def load_bosses(self):
        """Load all boss data."""
        # Basic bosses
        self.bosses["hollow_citizen"] = Enemy(
            id="hollow_citizen",
            name="Hollow Citizen",
            description="A hollowed out citizen that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=3,
            hp=100,
            attack=20,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 20, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=30
        )
        
        self.bosses["corrupted_guard"] = Enemy(
            id="corrupted_guard",
            name="Corrupted Guard",
            description="A guard in armor that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=4,
            hp=120,
            attack=25,
            defense=15,
            attack_patterns=[{"name": "Basic Attack", "damage": 25, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=40
        )
        
        # Add more bosses as needed...
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
            ],
            rewards={
                "item": "kings_greatsword",
                "essence": 1000,
                "lore": "king_morgaeth_lore"
            }
        )
        
        self.quests["ashen_heart"] = Quest(
            id="ashen_heart",
            name="Heart of the Ashen Woods",
            description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
            objectives=[
                {"type": "kill", "target": "ashen_lord", "quantity": 1}
            ],
            rewards={
                "item": "ashen_talisman",
                "essence": 800,
                "lore": "ashen_woods_lore"
            }
        )
        
        self.quests["frost_guardian"] = Quest(
            id="frost_guardian",
            name="Guardian of the Frost Gate",
            description="Defeat Vordt and claim passage to the northern territories.",
            objectives=[
                {"type": "kill", "target": "vordt", "quantity": 1}
            ],
            rewards={
                "item": "frost_essence",
                "essence": 500
            }
        )
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["ember_quest"] = Quest(
            id="ember_quest",
            name="The Smith's Request",
            description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
            objectives=[
                {"type": "item", "target": "ember_essence", "quantity": 1}
            ],
            rewards={
                "item": "flamebrand",
                "essence": 200
            }
        )
        
        self.quests["signet_quest"] = Quest(
            id="signet_quest",
            name="The Merchant's Signet",
            description="Find Ulrich's missing signet ring in the Blighted Marshes.",
            objectives=[
                {"type": "item", "target": "blue_signet", "quantity": 1}
            ],
            rewards={
                "item": "royal_seal",
                "essence": 300
            }
        )
        
        self.quests["chalice_quest"] = Quest(
            id="chalice_quest",
            name="The Sacred Chalice",
            description="Retrieve the sacred chalice from the corrupted deacon in the bell tower.",
            objectives=[
                {"type": "item", "target": "sacred_chalice", "quantity": 1}
            ],
            rewards={
                "item": "dark_talisman",
                "essence": 350,
                "faction": "Children of Dark",
                "reputation": 15
            }
        )
        
        self.quests["kings_fall"] = Quest(
            id="kings_fall",
            name="The Hollowed Crown",
            description="Discover the fate of King Morgaeth and put an end to his suffering.",
            objectives=[
                {"type": "kill", "target": "king_morgaeth", "quantity": 1}
import os
import json
import time
import random
import pickle
import datetime
import platform
import sys
from typing import Dict, List, Optional, Tuple, Union, Any

# Constants
SAVE_DIR = "saves"
AUTOSAVE_FILE = os.path.join(SAVE_DIR, "autosave.sav")
VERSION = "1.0.0"

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# ASCII Art and UI Elements
TITLE_ART = """
  ╔═══════════════════════════════════════════════════════════╗
  ║  ▄████▄   ██▀███   █    ██  ███▄ ▄███▓ ▄▄▄▄    ██▓    ██▓ ║
  ║ ▒██▀ ▀█  ▓██ ▒ ██▒ ██  ▓██▒▓██▒▀█▀ ██▒▓█████▄ ▓██▒   ▓██▒ ║
  ║ ▒▓█    ▄ ▓██ ░▄█ ▒▓██  ▒██░▓██    ▓██░▒██▒ ▄██▒██░   ▒██░ ║
  ║ ▒▓▓▄ ▄██▒▒██▀▀█▄  ▓▓█  ░██░▒██    ▒██ ▒██░█▀  ▒██░   ▒██░ ║
  ║ ▒ ▓███▀ ░░██▓ ▒██▒▒▒█████▓ ▒██▒   ░██▒░▓█  ▀█▓░██████░██████╗
  ║ ░ ░▒ ▒  ░░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ░ ▒░   ░  ░░▒▓███▀▒░ ▒░▓  ░ ▒░▓  ║
  ║   ░  ▒     ░▒ ░ ▒░░░▒░ ░ ░ ░  ░      ░▒░▒   ░ ░ ░ ▒  ░ ░ ▒  ║
  ║ ░          ░░   ░  ░░░ ░ ░ ░      ░    ░    ░   ░ ░    ░ ░  ║
  ║ ░ ░         ░        ░            ░    ░          ░  ░   ░  ║
  ║                           ARDENVALE                        ║
  ╚═══════════════════════════════════════════════════════════╝
                A REALM SHATTERED BY A FADING FLAME
"""

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                      ARDENVALE                            ║
╚═══════════════════════════════════════════════════════════╝
"""

DIVIDER = "═" * 70

# Utility Functions
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
        
        return {
            "player_name": save_data["player"]["name"],
            "player_level": save_data["player"]["level"],
            "location": save_data["player"]["current_location"],
            "timestamp": save_data["timestamp"],
            "version": save_data["version"]
        }
    except Exception as e:
        return {
            "error": str(e),
            "filename": filename
        }

# Game Classes
class Item:
    def __init__(self, id: str, name: str, description: str, item_type: str, value: int = 0, 
                 weight: float = 0.0, stats: Dict = None, usable: bool = False, 
                 equippable: bool = False, quantity: int = 1):
        self.id = id
        self.name = name
        self.description = description
        self.item_type = item_type  # weapon, armor, consumable, key, etc.
        self.value = value
        self.weight = weight
        self.stats = stats or {}
        self.usable = usable
        self.equippable = equippable
        self.quantity = quantity
        self.equipped = False
    
    def use(self, player) -> str:
        """Use the item and return result message."""
        if not self.usable:
            return f"You cannot use the {self.name}."
        
        # Implement item usage logic here
        result = "You used the item, but nothing happened."
        
        # Example: Healing potion
        if self.item_type == "consumable" and "healing" in self.stats:
            heal_amount = self.stats["healing"]
            player.heal(heal_amount)
            result = f"You drink the {self.name} and recover {heal_amount} health."
            self.quantity -= 1
            
        return result
    
    def to_dict(self) -> Dict:
        """Convert item to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "value": self.value,
            "weight": self.weight,
            "stats": self.stats,
            "usable": self.usable,
            "equippable": self.equippable,
            "quantity": self.quantity,
            "equipped": self.equipped
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Create an item from dictionary data."""
        item = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=data["item_type"],
            value=data["value"],
            weight=data["weight"],
            stats=data["stats"],
            usable=data["usable"],
            equippable=data["equippable"],
            quantity=data["quantity"]
        )
        item.equipped = data["equipped"]
        return item

class Weapon(Item):
    def __init__(self, id: str, name: str, description: str, damage: int, 
                 damage_type: str, weight: float, value: int, 
                 special_ability: Dict = None, two_handed: bool = False):
        stats = {
            "damage": damage,
            "damage_type": damage_type,
            "two_handed": two_handed
        }
        if special_ability:
            stats["special_ability"] = special_ability
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="weapon",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )
    
    def get_damage(self) -> int:
        """Calculate the weapon's damage."""
        base_damage = self.stats["damage"]
        return base_damage
    
    def weapon_art(self, player, target) -> str:
        """Use the weapon's special ability."""
        if "special_ability" not in self.stats:
            return "This weapon has no special ability."
        
        ability = self.stats["special_ability"]
        # Implement weapon special ability logic
        
        return f"You use {ability['name']}!"

class Armor(Item):
    def __init__(self, id: str, name: str, description: str, defense: int, 
                 armor_type: str, weight: float, value: int, 
                 resistance: Dict = None):
        stats = {
            "defense": defense,
            "armor_type": armor_type,
        }
        if resistance:
            stats["resistance"] = resistance
            
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="armor",
            value=value,
            weight=weight,
            stats=stats,
            usable=False,
            equippable=True
        )

class Consumable(Item):
    def __init__(self, id: str, name: str, description: str, effect: Dict, 
                 value: int, weight: float = 0.1, quantity: int = 1):
        super().__init__(
            id=id,
            name=name,
            description=description,
            item_type="consumable",
            value=value,
            weight=weight,
            stats=effect,
            usable=True,
            equippable=False,
            quantity=quantity
        )

class Enemy:
    def __init__(self, id: str, name: str, description: str, level: int, 
                 hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.attack_patterns = attack_patterns or []
        self.loot_table = loot_table or []
        self.essence = essence
        self.weaknesses = weaknesses or []
        self.current_pattern_index = 0
    
    def get_next_attack(self) -> Dict:
        """Get the next attack pattern in sequence."""
        if not self.attack_patterns:
            return {"name": "Basic Attack", "damage": self.attack, "type": "physical"}
        
        pattern = self.attack_patterns[self.current_pattern_index]
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.attack_patterns)
        return pattern
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        # Apply weakness multipliers
        multiplier = 1.0
        if damage_type in self.weaknesses:
            multiplier = 1.5
            
        damage = int(max(1, amount * multiplier - self.defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the enemy is dead."""
        return self.hp <= 0
    
    def drop_loot(self) -> List[Item]:
        """Generate loot drops based on loot table."""
        drops = []
        for loot_entry in self.loot_table:
            if random.random() < loot_entry["chance"]:
                # Create the item from the item database
                item_id = loot_entry["item_id"]
                item = create_item(item_id)
                if item:
                    # Set quantity if specified
                    if "quantity" in loot_entry:
                        item.quantity = random.randint(
                            loot_entry["quantity"]["min"], 
                            loot_entry["quantity"]["max"]
                        )
                    drops.append(item)
        return drops
    
    def to_dict(self) -> Dict:
        """Convert enemy to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "attack_patterns": self.attack_patterns,
            "loot_table": self.loot_table,
            "essence": self.essence,
            "weaknesses": self.weaknesses,
            "current_pattern_index": self.current_pattern_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Enemy':
        """Create an enemy from dictionary data."""
        enemy = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            level=data["level"],
            hp=data["max_hp"],
            attack=data["attack"],
            defense=data["defense"],
            attack_patterns=data["attack_patterns"],
            loot_table=data["loot_table"],
            essence=data["essence"],
            weaknesses=data["weaknesses"]
        )
        enemy.hp = data["hp"]
        enemy.current_pattern_index = data["current_pattern_index"]
        return enemy

class Boss(Enemy):
    def __init__(self, id: str, name: str, title: str, description: str, 
                 level: int, hp: int, attack: int, defense: int, 
                 attack_patterns: List[Dict] = None, 
                 loot_table: List[Dict] = None, 
                 essence: int = 0, 
                 weaknesses: List[str] = None,
                 phases: List[Dict] = None):
        super().__init__(
            id=id,
            name=f"{name}, {title}",
            description=description,
            level=level,
            hp=hp,
            attack=attack,
            defense=defense,
            attack_patterns=attack_patterns,
            loot_table=loot_table,
            essence=essence,
            weaknesses=weaknesses
        )
        self.phases = phases or []
        self.current_phase = 0
        self.phase_triggers = [phase["trigger"] for phase in self.phases] if phases else []
    
    def update_phase(self) -> bool:
        """Check and update boss phase based on HP. Return True if phase changed."""
        if not self.phases:
            return False
            
        # Check if we should transition to the next phase
        hp_percentage = self.hp / self.max_hp * 100
        
        for i, trigger in enumerate(self.phase_triggers):
            if hp_percentage <= trigger and i > self.current_phase:
                self.current_phase = i
                # Apply phase changes
                phase = self.phases[i]
                if "attack_patterns" in phase:
                    self.attack_patterns = phase["attack_patterns"]
                    self.current_pattern_index = 0
                if "attack_boost" in phase:
                    self.attack += phase["attack_boost"]
                if "defense_boost" in phase:
                    self.defense += phase["defense_boost"]
                if "message" in phase:
                    print_slow(phase["message"])
                    
                return True
                
        return False

class Location:
    def __init__(self, id: str, name: str, description: str, 
                 connections: Dict[str, str] = None,
                 enemies: List[str] = None,
                 items: List[str] = None,
                 npcs: List[str] = None,
                 is_beacon: bool = False,
                 map_art: str = None,
                 first_visit_text: str = None,
                 events: Dict = None):
        self.id = id
        self.name = name
        self.description = description
        self.connections = connections or {}  # Direction: location_id
        self.enemies = enemies or []  # List of enemy ids that can spawn here
        self.items = items or []  # List of item ids that can be found here
        self.npcs = npcs or []  # List of NPC ids that can be found here
        self.is_beacon = is_beacon
        self.map_art = map_art
        self.first_visit_text = first_visit_text
        self.events = events or {}  # Event triggers
        self.visited = False
    
    def get_description(self) -> str:
        """Get the location description."""
        return self.description
    
    def get_connections_string(self) -> str:
        """Get a string describing available exits."""
        if not self.connections:
            return "There are no obvious exits."
            
        exits = []
        for direction, _ in self.connections.items():
            exits.append(direction)
        
        return f"Exits: {', '.join(exits)}"
    
    def to_dict(self) -> Dict:
        """Convert location to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connections": self.connections,
            "enemies": self.enemies,
            "items": self.items,
            "npcs": self.npcs,
            "is_beacon": self.is_beacon,
            "map_art": self.map_art,
            "first_visit_text": self.first_visit_text,
            "events": self.events,
            "visited": self.visited
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        """Create a location from dictionary data."""
        location = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            connections=data["connections"],
            enemies=data["enemies"],
            items=data["items"],
            npcs=data["npcs"],
            is_beacon=data["is_beacon"],
            map_art=data["map_art"],
            first_visit_text=data["first_visit_text"],
            events=data["events"]
        )
        location.visited = data["visited"]
        return location

class NPC:
    def __init__(self, id: str, name: str, description: str, 
                 dialogue: Dict[str, Dict] = None,
                 quest: Dict = None,
                 shop_inventory: List[str] = None,
                 faction: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.dialogue = dialogue or {"default": {"text": "...", "options": {}}}
        self.current_dialogue = "default"
        self.quest = quest
        self.shop_inventory = shop_inventory or []
        self.faction = faction
        self.met = False
        self.relationship = 0  # -100 to 100
    
    def get_dialogue(self) -> Dict:
        """Get the current dialogue options."""
        return self.dialogue.get(self.current_dialogue, self.dialogue["default"])
    
    def talk(self) -> str:
        """Start a conversation with the NPC."""
        if not self.met:
            self.met = True
            return f"You meet {self.name} for the first time.\n{self.description}"
        
        return f"{self.name}: {self.get_dialogue()['text']}"
    
    def respond(self, option: str) -> str:
        """Respond to a dialogue option."""
        dialogue = self.get_dialogue()
        
        if option in dialogue["options"]:
            response = dialogue["options"][option]
            
            # Update dialogue state if needed
            if "next" in response:
                self.current_dialogue = response["next"]
            
            # Handle quest progression
            if "quest_progress" in response and self.quest:
                # Implement quest progression logic
                pass
            
            # Handle relationship changes
            if "relationship" in response:
                self.relationship += response["relationship"]
                
            return response["text"]
        
        return "Invalid response."
    
    def to_dict(self) -> Dict:
        """Convert NPC to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dialogue": self.dialogue,
            "current_dialogue": self.current_dialogue,
            "quest": self.quest,
            "shop_inventory": self.shop_inventory,
            "faction": self.faction,
            "met": self.met,
            "relationship": self.relationship
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NPC':
        """Create an NPC from dictionary data."""
        npc = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            dialogue=data["dialogue"],
            quest=data["quest"],
            shop_inventory=data["shop_inventory"],
            faction=data["faction"]
        )
        npc.current_dialogue = data["current_dialogue"]
        npc.met = data["met"]
        npc.relationship = data["relationship"]
        return npc

class Player:
    def __init__(self, name: str, character_class: str, level: int = 1):
        self.name = name
        self.character_class = character_class
        self.level = level
        self.essence = 0  # Currency
        self.lost_essence = 0  # Lost on death
        self.lost_essence_location = None
        
        # Initialize stats based on class
        if character_class == "Warrior":
            self.max_hp = 100
            self.max_stamina = 80
            self.strength = 14
            self.dexterity = 9
            self.intelligence = 7
            self.faith = 8
            self.vitality = 12
            self.endurance = 10
        elif character_class == "Knight":
            self.max_hp = 90
            self.max_stamina = 90
            self.strength = 12
            self.dexterity = 12
            self.intelligence = 9
            self.faith = 11
            self.vitality = 10
            self.endurance = 11
        elif character_class == "Pyromancer":
            self.max_hp = 80
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 12
            self.faith = 14
            self.vitality = 8
            self.endurance = 9
        elif character_class == "Thief":
            self.max_hp = 75
            self.max_stamina = 100
            self.strength = 9
            self.dexterity = 14
            self.intelligence = 10
            self.faith = 8
            self.vitality = 9
            self.endurance = 14
        else:  # Default
            self.max_hp = 85
            self.max_stamina = 85
            self.strength = 10
            self.dexterity = 10
            self.intelligence = 10
            self.faith = 10
            self.vitality = 10
            self.endurance = 10
        
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.inventory = []
        self.equipment = {
            "weapon": None,
            "shield": None,
            "armor": None,
            "ring1": None,
            "ring2": None,
            "amulet": None
        }
        self.estus_flask = {
            "current": 3,
            "max": 3
        }
        self.current_location = "highcastle_entrance"
        self.quests = {}
        self.discovered_locations = set()
        self.killed_enemies = {}
        self.stance = "balanced"  # balanced, aggressive, defensive
    
    def heal(self, amount: int) -> int:
        """Heal the player and return amount healed."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def restore_stamina(self, amount: int) -> int:
        """Restore stamina and return amount restored."""
        old_stamina = self.stamina
        self.stamina = min(self.max_stamina, self.stamina + amount)
        return self.stamina - old_stamina
    
    def use_estus(self) -> bool:
        """Use an estus flask charge to heal."""
        if self.estus_flask["current"] <= 0:
            return False
        
        self.estus_flask["current"] -= 1
        heal_amount = int(self.max_hp * 0.4)  # Heal 40% of max HP
        self.heal(heal_amount)
        return True
    
    def rest_at_beacon(self):
        """Rest at a beacon to restore HP, stamina, and estus."""
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.estus_flask["current"] = self.estus_flask["max"]
    
    def add_item(self, item: Item) -> bool:
        """Add an item to inventory. Return True if successful."""
        # Check if the item is stackable and exists in inventory
        if item.quantity > 1:
            for inv_item in self.inventory:
                if inv_item.id == item.id:
                    inv_item.quantity += item.quantity
                    return True
                    
        self.inventory.append(item)
        return True
    
    def remove_item(self, item: Item) -> bool:
        """Remove an item from inventory. Return True if successful."""
        for i, inv_item in enumerate(self.inventory):
            if inv_item.id == item.id:
                if inv_item.quantity > 1:
                    inv_item.quantity -= 1
                    return True
                else:
                    self.inventory.pop(i)
                    return True
        return False
    
    def equip_item(self, item: Item) -> str:
        """Equip an item. Return result message."""
        if not item.equippable:
            return f"You cannot equip {item.name}."
            
        # Determine equipment slot
        slot = None
        if item.item_type == "weapon":
            slot = "weapon"
        elif item.item_type == "shield":
            slot = "shield"
        elif item.item_type == "armor":
            slot = "armor"
        elif item.item_type == "ring":
            # Check if ring slots are available
            if self.equipment["ring1"] is None:
                slot = "ring1"
            elif self.equipment["ring2"] is None:
                slot = "ring2"
            else:
                return "You cannot equip more rings."
        elif item.item_type == "amulet":
            slot = "amulet"
        else:
            return f"Cannot equip {item.name}."
            
        # Unequip current item in that slot if any
        if self.equipment[slot] is not None:
            self.equipment[slot].equipped = False
            
        # Equip new item
        self.equipment[slot] = item
        item.equipped = True
        
        return f"You equipped {item.name}."
    
    def unequip_item(self, slot: str) -> str:
        """Unequip an item from specified slot. Return result message."""
        if slot not in self.equipment or self.equipment[slot] is None:
            return f"Nothing equipped in {slot}."
            
        item = self.equipment[slot]
        item.equipped = False
        self.equipment[slot] = None
        
        return f"You unequipped {item.name}."
    
    def get_attack_power(self) -> int:
        """Calculate the player's attack power."""
        base_attack = self.strength // 2
        
        if self.equipment["weapon"]:
            weapon_damage = self.equipment["weapon"].get_damage()
            # Apply stat scaling based on weapon type
            weapon_stats = self.equipment["weapon"].stats
            if "scaling" in weapon_stats:
                if weapon_stats["scaling"] == "strength":
                    scaling_bonus = self.strength // 3
                elif weapon_stats["scaling"] == "dexterity":
                    scaling_bonus = self.dexterity // 3
                else:
                    scaling_bonus = 0
                weapon_damage += scaling_bonus
            
            base_attack += weapon_damage
        
        # Apply stance modifiers
        if self.stance == "aggressive":
            base_attack = int(base_attack * 1.2)  # 20% more damage
        elif self.stance == "defensive":
            base_attack = int(base_attack * 0.8)  # 20% less damage
            
        return base_attack
    
    def get_defense(self) -> int:
        """Calculate the player's defense value."""
        base_defense = self.vitality // 2
        
        if self.equipment["armor"]:
            base_defense += self.equipment["armor"].stats["defense"]
            
        if self.equipment["shield"] and self.stance != "aggressive":
            base_defense += self.equipment["shield"].stats["defense"]
        
        # Apply stance modifiers
        if self.stance == "defensive":
            base_defense = int(base_defense * 1.2)  # 20% more defense
        elif self.stance == "aggressive":
            base_defense = int(base_defense * 0.8)  # 20% less defense
            
        return base_defense
    
    def take_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Take damage and return actual damage dealt."""
        defense = self.get_defense()
        
        # Apply resistances from equipment
        resistance_mult = 1.0
        for slot, item in self.equipment.items():
            if item and "resistance" in item.stats and damage_type in item.stats["resistance"]:
                resistance_mult -= item.stats["resistance"][damage_type] / 100.0
        
        # Ensure resistance multiplier is at least 0.2 (80% damage reduction max)
        resistance_mult = max(0.2, resistance_mult)
        
        # Calculate final damage
        damage = int(max(1, amount * resistance_mult - defense // 2))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_dead(self) -> bool:
        """Check if the player is dead."""
        return self.hp <= 0
    
    def die(self):
        """Handle player death."""
        # Drop essence at current location
        self.lost_essence = self.essence
        self.lost_essence_location = self.current_location
        self.essence = 0
        
        # Respawn at last beacon
        # This would be implemented in the game loop logic
    
    def recover_lost_essence(self):
        """Recover lost essence."""
        if self.lost_essence > 0:
            self.essence += self.lost_essence
            self.lost_essence = 0
            self.lost_essence_location = None
            return True
        return False
    
    def level_up(self, stat: str) -> bool:
        """Level up a stat. Return True if successful."""
        cost = self.calculate_level_cost()
        
        if self.essence < cost:
            return False
            
        self.essence -= cost
        self.level += 1
        
        # Increase the chosen stat
        if stat == "strength":
            self.strength += 1
        elif stat == "dexterity":
            self.dexterity += 1
        elif stat == "intelligence":
            self.intelligence += 1
        elif stat == "faith":
            self.faith += 1
        elif stat == "vitality":
            self.vitality += 1
            self.max_hp += 5
            self.hp += 5
        elif stat == "endurance":
            self.endurance += 1
            self.max_stamina += 5
            self.stamina += 5
        
        return True
    
    def calculate_level_cost(self) -> int:
        """Calculate the essence cost for the next level."""
        return int(100 * (1.1 ** (self.level - 1)))
    
    def use_item(self, item_index: int) -> str:
        """Use an item from inventory by index."""
        if item_index < 0 or item_index >= len(self.inventory):
            return "Invalid item index."
            
        item = self.inventory[item_index]
        
        if not item.usable:
            return f"You cannot use {item.name}."
            
        result = item.use(self)
        
        # Remove item if quantity reaches 0
        if item.quantity <= 0:
            self.inventory.pop(item_index)
            
        return result
    
    def change_stance(self, new_stance: str) -> str:
        """Change combat stance. Return result message."""
        valid_stances = ["balanced", "aggressive", "defensive"]
        
        if new_stance not in valid_stances:
            return f"Invalid stance. Choose from: {', '.join(valid_stances)}"
            
        old_stance = self.stance
        self.stance = new_stance
        
        return f"Changed stance from {old_stance} to {new_stance}."
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for saving."""
        return {
            "name": self.name,
            "character_class": self.character_class,
            "level": self.level,
            "essence": self.essence,
            "lost_essence": self.lost_essence,
            "lost_essence_location": self.lost_essence_location,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "max_stamina": self.max_stamina,
            "stamina": self.stamina,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "faith": self.faith,
            "vitality": self.vitality,
            "endurance": self.endurance,
            "inventory": [item.to_dict() for item in self.inventory],
            "equipment": {slot: (item.to_dict() if item else None) for slot, item in self.equipment.items()},
            "estus_flask": self.estus_flask,
            "current_location": self.current_location,
            "quests": self.quests,
            "discovered_locations": list(self.discovered_locations),
            "killed_enemies": self.killed_enemies,
            "stance": self.stance
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create a player from dictionary data."""
        player = cls(
            name=data["name"],
            character_class=data["character_class"],
            level=data["level"]
        )
        player.essence = data["essence"]
        player.lost_essence = data["lost_essence"]
        player.lost_essence_location = data["lost_essence_location"]
        player.max_hp = data["max_hp"]
        player.hp = data["hp"]
        player.max_stamina = data["max_stamina"]
        player.stamina = data["stamina"]
        player.strength = data["strength"]
        player.dexterity = data["dexterity"]
        player.intelligence = data["intelligence"]
        player.faith = data["faith"]
        player.vitality = data["vitality"]
        player.endurance = data["endurance"]
        
        # Reconstruct inventory
        player.inventory = []
        for item_data in data["inventory"]:
            if item_data["item_type"] == "weapon":
                item = Weapon(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    damage=item_data["stats"]["damage"],
                    damage_type=item_data["stats"]["damage_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    special_ability=item_data["stats"].get("special_ability"),
                    two_handed=item_data["stats"].get("two_handed", False)
                )
            elif item_data["item_type"] == "armor":
                item = Armor(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    defense=item_data["stats"]["defense"],
                    armor_type=item_data["stats"]["armor_type"],
                    weight=item_data["weight"],
                    value=item_data["value"],
                    resistance=item_data["stats"].get("resistance")
                )
            elif item_data["item_type"] == "consumable":
                item = Consumable(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    effect=item_data["stats"],
                    value=item_data["value"],
                    weight=item_data["weight"],
                    quantity=item_data["quantity"]
                )
            else:
                item = Item.from_dict(item_data)
                
            item.quantity = item_data["quantity"]
            item.equipped = item_data["equipped"]
            player.inventory.append(item)
        
        # Reconstruct equipment
        player.equipment = {slot: None for slot in player.equipment.keys()}
        for slot, item_data in data["equipment"].items():
            if item_data:
                for item in player.inventory:
                    if item.id == item_data["id"]:
                        player.equipment[slot] = item
                        break
                        
        player.estus_flask = data["estus_flask"]
        player.current_location = data["current_location"]
        player.quests = data["quests"]
        player.discovered_locations = set(data["discovered_locations"])
        player.killed_enemies = data["killed_enemies"]
        player.stance = data["stance"]
        
        return player

class World:
    def __init__(self):
        self.locations = {}
        self.npcs = {}
        self.items = {}
        self.enemies = {}
        self.bosses = {}
        self.quests = {}
        self.active_events = set()
        self.game_state = {}
        
        # Initialize world components
        self.initialize_world()
    
    def initialize_world(self):
        """Initialize and load all world data."""
        self.load_locations()
        self.load_npcs()
        self.load_items()
        self.load_enemies()
        self.load_bosses()
        self.load_quests()
    
    def load_locations(self):
        """Load all location data."""
        # Highcastle Region
        self.locations["highcastle_entrance"] = Location(
            id="highcastle_entrance",
            name="Highcastle Gate",
            description="The towering gates of Highcastle stand before you, worn by time but still majestic. The once-bustling gatehouse is now quiet, with only a few guards maintaining their eternal vigil.",
            connections={
                "north": "highcastle_plaza",
                "east": "eastern_road",
                "west": "western_path"
            },
            enemies=["wandering_hollow", "fallen_knight"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Gate
       v S       o - You
  
  #################
  #####.....######
  ####...o...#####
  ###.........####
  ##.....+.....###
  #...............
  #...............
            """,
            first_visit_text="You arrive at the once-grand entrance to Highcastle, the last bastion of humanity in these dark times. The walls, though weathered, still stand tall against the encroaching darkness that has consumed much of Ardenvale."
        )
        
        self.locations["highcastle_plaza"] = Location(
            id="highcastle_plaza",
            name="Highcastle Central Plaza",
            description="The central plaza of Highcastle is a shadow of its former glory. Cracked fountains and weathered statues are silent witnesses to a time of prosperity long gone. A few desperate souls still wander here, clinging to routines of a life that no longer exists.",
            connections={
                "north": "highcastle_cathedral",
                "east": "eastern_district",
                "west": "western_district",
                "south": "highcastle_entrance"
            },
            enemies=["hollow_citizen", "corrupted_guard"],
            npcs=["andre_smith", "merchant_ulrich"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ###+######+####
  #...........+.#
  #.....o.......#
  #...#...#...#.#
  #.............#
  #...#...#...#.#
  ###....+....###
            """
        )
        
        self.locations["highcastle_cathedral"] = Location(
            id="highcastle_cathedral",
            name="Cathedral of the Fading Light",
            description="This once-magnificent cathedral now stands in partial ruin. Shafts of light pierce through holes in the ceiling, illuminating dust-covered pews and crumbling statues of forgotten deities. Despite its state, there is still an aura of reverence here.",
            connections={
                "south": "highcastle_plaza",
                "east": "cathedral_tower"
            },
            enemies=["cathedral_knight", "deacon_of_the_deep"],
            npcs=["sister_friede"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     ~ - Water
       |         + - Door
       v S       o - You
  
  ########+######
  #..#.......#..#
  #...........+.#
  #.............#
  #....o........#
  #.....###.....#
  ##....+....####
            """
        )
        
        # Ashen Woods Region
        self.locations["western_path"] = Location(
            id="western_path",
            name="Western Path",
            description="A winding path leads westward from Highcastle. Once a well-traveled trade route, it is now overgrown and dangerous. The trees along the path seem to lean inward, as if watching passersby with malicious intent.",
            connections={
                "east": "highcastle_entrance",
                "west": "ashen_woods_entrance"
            },
            enemies=["wild_beast", "hollow_woodsman"],
            map_art="""
       ^ N       
       |         # - Walls
  W <----> E     % - Trees
       |         ~ - Water
       v S       o - You
  
  %%%%%%%%%%%    
  %%%..........
  %%%...o......
  %%%...........
  %%%...........
  %%%.......%%%%
  %%%%%%%%%%%    
            """
        )
        
        self.locations["ashen_woods_entrance"] = Location(
            id="ashen_woods_entrance",
            name="Ashen Woods Entrance",
            description="The entrance to the Ashen Woods is marked by a sudden change in the landscape. The trees here are grey and lifeless, their bark turned to ash. Wisps of smoke rise from the ground, though there is no fire to be seen.",
            connections={
                "east": "western_path",
                "west": "ashen_woods_clearing"
            },
            enemies=["ember_wolf", "ashen_treant"],
            is_beacon=True,
            map_art="""
       ^ N       
       |         % - Trees
  W <----> E     ^ - Ash trees
       |         ~ - Water
       v S       o - You
  
  ^^^^^^^^^^^^^^
  ^^.....^^^.^^^
  ^.......o...^^
  ^............^
  ^^^..........^
  ^^^^^^^^^^^^^^
  ^^^^^^^^^^^^^^
            """
        )
        
        # Add more locations as needed...
    
    def load_npcs(self):
        """Load all NPC data."""
        self.npcs["andre_smith"] = NPC(
            id="andre_smith",
            name="Andre the Smith",
            description="A muscular blacksmith with arms like tree trunks. Despite the dark times, his eyes still hold a passionate fire for his craft. His hammer strikes rhythmically in the background.",
            dialogue={
                "default": {
                    "text": "Need something forged? Or perhaps an upgrade to that weapon of yours?",
                    "options": {
                        "1": {
                            "text": "I'd like to upgrade my weapon.",
                            "next": "upgrade"
                        },
                        "2": {
                            "text": "Tell me about yourself.",
                            "next": "about"
                        },
                        "3": {
                            "text": "What happened to this place?",
                            "next": "history"
                        },
                        "4": {
                            "text": "Farewell.",
                            "next": "default"
                        }
                    }
                },
                "upgrade": {
                    "text": "Ah, let me see what you've got. I can work with most materials, given enough time and the right components.",
                    "options": {
                        "1": {
                            "text": "Actually, let's talk about something else.",
                            "next": "default"
                        },
                        "2": {
                            "text": "Never mind.",
                            "next": "default"
                        }
                    }
                },
                "about": {
                    "text": "Been a smith all my life. Learned from my father, who learned from his. I've seen kingdoms rise and fall, but the forge remains. As long as there are warriors who need weapons, I'll be here.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "history": {
                    "text": "Highcastle was once the jewel of Ardenvale. When the First Flame began to fade, everything changed. The corruption spread, people hollowed, and darkness crept in. But we endure. We always do.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the First Flame.",
                            "next": "first_flame"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "first_flame": {
                    "text": "The First Flame is what brought light and disparity to our world. Heat and cold, life and death, light and dark... all because of the Flame. Now it fades, and the balance tips toward darkness. Some seek to rekindle it, others to usher in an Age of Dark. Me? I just forge.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                }
            },
            shop_inventory=["reinforced_sword", "knight_shield", "ember"]
        )
        
        self.npcs["merchant_ulrich"] = NPC(
            id="merchant_ulrich",
            name="Merchant Ulrich",
            description="A hunched man with a perpetual nervous twitch. His eyes dart about constantly, and his fingers fidget with the hem of his tattered cloak. Despite his appearance, he has somehow managed to maintain a stock of rare goods.",
            dialogue={
                "default": {
                    "text": "Ah, a customer! Rare sight these days. Looking to trade? I've got wares from all corners of Ardenvale, before... well, before everything went to ruin.",
                    "options": {
                        "1": {
                            "text": "Show me what you have for sale.",
                            "next": "shop"
                        },
                        "2": {
                            "text": "Any rumors lately?",
                            "next": "rumors"
                        },
                        "3": {
                            "text": "How do you get your merchandise?",
                            "next": "merchandise"
                        },
                        "4": {
                            "text": "Farewell.",
                            "next": "default"
                        }
                    }
                },
                "shop": {
                    "text": "Take a look, take a look! Fine goods at reasonable prices. Well, reasonable considering the state of the world.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "rumors": {
                    "text": "Rumors? Oh, I hear many things... They say the old king still wanders the Ringed Citadel, hollowed but retaining a fragment of his former self. And in the Ashen Woods, the tree shepherds have gone mad, attacking any who venture too deep.",
                    "options": {
                        "1": {
                            "text": "Tell me more about the king.",
                            "next": "king"
                        },
                        "2": {
                            "text": "What are tree shepherds?",
                            "next": "shepherds"
                        },
                        "3": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "king": {
                    "text": "King Morgaeth was a wise ruler, once. They say he delved too deep into forbidden arts in his quest to save the kingdom from the fading of the Flame. Now he's neither dead nor truly alive... a hollow shell of royalty.",
                    "options": {
                        "1": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "shepherds": {
                    "text": "Ancient creatures, like walking trees but with awareness. They tended the forests for millennia in peace. The corruption has twisted them, made them violent. A shame. They were magnificent beings.",
                    "options": {
                        "1": {
                            "text": "Back to rumors.",
                            "next": "rumors"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "merchandise": {
                    "text": "Ah, professional secrets! *winks nervously* Let's just say I have... arrangements with certain brave souls who venture where others fear to tread. They bring me goods, I give them essence, everyone profits!",
                    "options": {
                        "1": {
                            "text": "Sounds dangerous.",
                            "next": "dangerous"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dangerous": {
                    "text": "Dangerous? *laughs shakily* My friend, everything is dangerous now. At least my suppliers choose their danger. Most of them return... some of the time.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                }
            },
            shop_inventory=["estus_shard", "life_gem", "homeward_bone", "green_blossom"]
        )
        
        self.npcs["sister_friede"] = NPC(
            id="sister_friede",
            name="Sister Friede",
            description="A tall, slender woman in white robes that seem untouched by the grime and decay around her. Her face is partially obscured by a hood, but you can see her pale skin and piercing blue eyes. She moves with eerie grace.",
            dialogue={
                "default": {
                    "text": "Ashen One, why do you disturb this sanctuary? This is a place of quiet reflection, not for those who would perpetuate a doomed cycle.",
                    "options": {
                        "1": {
                            "text": "I seek guidance.",
                            "next": "guidance"
                        },
                        "2": {
                            "text": "What cycle do you speak of?",
                            "next": "cycle"
                        },
                        "3": {
                            "text": "Who are you?",
                            "next": "identity"
                        },
                        "4": {
                            "text": "I'll leave you to your reflection.",
                            "next": "default"
                        }
                    }
                },
                "guidance": {
                    "text": "Guidance? *soft laugh* The path ahead is shrouded for all of us. But if you must continue your journey, seek the depths of the Ashen Woods. There lies an ancient tree shepherd who remembers the time before corruption. His wisdom may aid you, if he doesn't kill you first.",
                    "options": {
                        "1": {
                            "text": "Thank you for the information.",
                            "next": "default"
                        },
                        "2": {
                            "text": "Why would he help me?",
                            "next": "help"
                        }
                    }
                },
                "help": {
                    "text": "He wouldn't, not willingly. But in his madness, truths slip out between attempts to end your life. Listen carefully... if you survive long enough to hear anything at all.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "cycle": {
                    "text": "The endless cycle of Light and Dark. For eons, the First Flame has been rekindled when it begins to fade, postponing the Age of Dark that is our birthright. Each rekindling only makes the inevitable collapse more devastating.",
                    "options": {
                        "1": {
                            "text": "You want the Flame to fade?",
                            "next": "fade"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "fade": {
                    "text": "*her eyes narrow slightly* I want what is natural. All fires eventually burn out. Fighting this truth has brought us to this state of perpetual decay. Let it end, and something new may begin.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "identity": {
                    "text": "I am simply a watcher. I've seen kingdoms rise and fall, flames kindle and fade. Now I wait here, in this broken cathedral, observing the final gasps of a dying age.",
                    "options": {
                        "1": {
                            "text": "You speak as if you're ancient.",
                            "next": "ancient"
                        },
                        "2": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "ancient": {
                    "text": "*she smiles enigmatically* Time loses meaning when you've witnessed enough cycles. But enough about me. What will you do, Ashen One? Perpetuate this dying world, or help usher in something new?",
                    "options": {
                        "1": {
                            "text": "I'll restore the Flame.",
                            "next": "restore",
                            "relationship": -10
                        },
                        "2": {
                            "text": "Perhaps the Dark should have its time.",
                            "next": "dark",
                            "relationship": 10
                        },
                        "3": {
                            "text": "I haven't decided yet.",
                            "next": "undecided"
                        }
                    }
                },
                "restore": {
                    "text": "*her expression hardens* Then you are no different from the others. Go your way, Ashen One. May you find what you seek... and understand its true cost.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "dark": {
                    "text": "*she studies you with new interest* Perhaps there is wisdom in you after all. The Dark is not to be feared, but embraced as part of the natural order. Remember this when your resolve is tested.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                },
                "undecided": {
                    "text": "Indecision is... understandable. The weight of such choices is immense. Reflect carefully, Ashen One. Not all is as it seems in Ardenvale.",
                    "options": {
                        "1": {
                            "text": "Back to the main topic.",
                            "next": "default"
                        }
                    }
                }
            },
            faction="Children of Dark"
        )
        
        # Add more NPCs as needed...
    
    def load_items(self):
        """Load all item data."""
        # Weapons
        self.items["reinforced_sword"] = Weapon(
            id="reinforced_sword",
            name="Reinforced Longsword",
            description="A sturdy longsword with reinforced steel. Reliable and well-balanced.",
            damage=15,
            damage_type="physical",
            weight=3.0,
            value=200,
            two_handed=False
        )
        
        self.items["knight_sword"] = Weapon(
            id="knight_sword",
            name="Knight's Sword",
            description="A well-crafted sword used by the knights of Highcastle. The blade bears the insignia of the royal guard.",
            damage=18,
            damage_type="physical",
            weight=3.5,
            value=300,
            two_handed=False
        )
        
        self.items["woodsman_axe"] = Weapon(
            id="woodsman_axe",
            name="Woodsman's Axe",
            description="A heavy axe used for chopping wood, now repurposed as a weapon. Slow but powerful.",
            damage=22,
            damage_type="physical",
            weight=4.5,
            value=180,
            two_handed=True
        )
        
        self.items["cathedral_greatsword"] = Weapon(
            id="cathedral_greatsword",
            name="Cathedral Greatsword",
            description="A massive sword wielded by the knights of the cathedral. Holy symbols are etched into the blade.",
            damage=26,
            damage_type="physical",
            weight=6.0,
            value=450,
            two_handed=True,
            special_ability={"name": "Holy Light", "damage": 15, "type": "holy"}
        )
        
        self.items["ember_blade"] = Weapon(
            id="ember_blade",
            name="Ember Blade",
            description="A sword forged in the heart of the Ashen Woods. The blade seems to smolder with inner heat.",
            damage=20,
            damage_type="fire",
            weight=3.0,
            value=500,
            two_handed=False,
            special_ability={"name": "Ignite", "damage": 12, "type": "fire", "duration": 3}
        )
        
        self.items["vordt_mace"] = Weapon(
            id="vordt_mace",
            name="Vordt's Frostmace",
            description="A massive mace once wielded by Vordt, Guardian of the Frost Gate. Crystals of ice form along its surface.",
            damage=30,
            damage_type="physical",
            weight=8.0,
            value=700,
            two_handed=True,
            special_ability={"name": "Frost Strike", "damage": 20, "type": "ice", "slow_effect": True}
        )
        
        self.items["kings_greatsword"] = Weapon(
            id="kings_greatsword",
            name="King's Greatsword",
            description="The royal greatsword of King Morgaeth, now tainted with dark energy. It pulses with corrupted power.",
            damage=35,
            damage_type="physical",
            weight=7.0,
            value=1000,
            two_handed=True,
            special_ability={"name": "Royal Wrath", "damage": 40, "type": "dark", "cooldown": 5}
        )
        
        # Armor
        self.items["knight_helm"] = Armor(
            id="knight_helm",
            name="Knight's Helm",
            description="A standard helmet worn by the knights of Highcastle. Provides good protection but limits visibility.",
            defense=10,
            armor_type="head",
            weight=2.0,
            value=200
        )
        
        self.items["knight_shield"] = Armor(
            id="knight_shield",
            name="Knight's Shield",
            description="A sturdy kite shield bearing the crest of Highcastle. Well-balanced for both defense and mobility.",
            defense=15,
            armor_type="shield",
            weight=3.5,
            value=250
        )
        
        self.items["rusted_shield"] = Armor(
            id="rusted_shield",
            name="Rusted Shield",
            description="A worn shield that has seen better days. Despite the rust, it still offers adequate protection.",
            defense=8,
            armor_type="shield",
            weight=3.0,
            value=100
        )
        
        self.items["cathedral_plate"] = Armor(
            id="cathedral_plate",
            name="Cathedral Plate Armor",
            description="Heavy armor worn by the elite knights of the cathedral. Ornate religious symbols adorn the breastplate.",
            defense=25,
            armor_type="chest",
            weight=8.0,
            value=500,
            resistance={"dark": 15}
        )
        
        self.items["deacon_robes"] = Armor(
            id="deacon_robes",
            name="Deacon's Robes",
            description="Dark robes worn by the deacons of the cathedral. Offers little physical protection but imbued with arcane resistance.",
            defense=5,
            armor_type="chest",
            weight=1.5,
            value=300,
            resistance={"magic": 20, "fire": 10}
        )
        
        self.items["frost_knight_armor"] = Armor(
            id="frost_knight_armor",
            name="Frost Knight Armor",
            description="Armor coated in a permanent layer of frost. Extremely heavy but offers exceptional protection.",
            defense=30,
            armor_type="chest",
            weight=12.0,
            value=800,
            resistance={"fire": 25, "ice": -10}  # Vulnerable to ice
        )
        
        self.items["hollowed_crown"] = Armor(
            id="hollowed_crown",
            name="Hollowed Crown",
            description="The tarnished crown of King Morgaeth. Dark energy swirls within its jewels.",
            defense=12,
            armor_type="head",
            weight=1.0,
            value=1200,
            resistance={"dark": 30, "holy": -25}  # Vulnerable to holy
        )
        
        # Consumables
        self.items["soul_remnant"] = Consumable(
            id="soul_remnant",
            name="Soul Remnant",
            description="A fragment of essence that can be consumed to restore a small amount of health.",
            effect={"healing": 15},
            value=10,
            quantity=1
        )
        
        self.items["life_gem"] = Consumable(
            id="life_gem",
            name="Life Gem",
            description="A crystal that slowly restores health when crushed and consumed.",
            effect={"healing": 30, "over_time": True, "duration": 5},
            value=100,
            quantity=1
        )
        
        self.items["ember"] = Consumable(
            id="ember",
            name="Ember",
            description="A warm ember that temporarily boosts maximum health when consumed.",
            effect={"max_health_boost": 20, "duration": 180},
            value=150,
            quantity=1
        )
        
        self.items["green_blossom"] = Consumable(
            id="green_blossom",
            name="Green Blossom",
            description="A fragrant green herb that temporarily boosts stamina regeneration.",
            effect={"stamina_regen": 20, "duration": 60},
            value=120,
            quantity=1
        )
        
        self.items["estus_shard"] = Item(
            id="estus_shard",
            name="Estus Shard",
            description="A fragment of an Estus Flask. Can be used to increase the number of uses for your Estus Flask.",
            item_type="key",
            value=500,
            usable=True
        )
        
        self.items["homeward_bone"] = Item(
            id="homeward_bone",
            name="Homeward Bone",
            description="A charred bone that carries the scent of home. Use to return to the last rested beacon.",
            item_type="consumable",
            value=150,
            usable=True,
            quantity=1
        )
        
        self.items["dark_residue"] = Item(
            id="dark_residue",
            name="Dark Residue",
            description="A strange, viscous substance that seems to absorb light. Used in certain crafting recipes.",
            item_type="material",
            value=50,
            usable=False,
            quantity=1
        )
        
        self.items["ember_essence"] = Item(
            id="ember_essence",
            name="Ember Essence",
            description="A concentrated form of fire energy. Warm to the touch and glows softly in darkness.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["frost_essence"] = Item(
            id="frost_essence",
            name="Frost Essence",
            description="Crystallized cold energy. The air around it is perpetually chilled.",
            item_type="material",
            value=75,
            usable=False,
            quantity=1
        )
        
        self.items["blessed_medallion"] = Item(
            id="blessed_medallion",
            name="Blessed Medallion",
            description="A holy symbol that provides protection against the dark. Slowly regenerates health when equipped.",
            item_type="amulet",
            value=300,
            equippable=True,
            stats={"health_regen": 1, "resistance": {"dark": 10}},
            quantity=1
        )
        
        self.items["dark_tome"] = Item(
            id="dark_tome",
            name="Dark Tome",
            description="An ancient book containing forbidden knowledge. The pages seem to whisper when turned.",
            item_type="catalyst",
            value=400,
            equippable=True,
            stats={"spell_boost": 15, "intelligence_scaling": True},
            quantity=1
        )
        
        self.items["royal_signet"] = Item(
            id="royal_signet",
            name="Royal Signet Ring",
            description="The royal signet of King Morgaeth. Grants authority and increases essence gained from defeating enemies.",
            item_type="ring",
            value=800,
            equippable=True,
            stats={"essence_gain": 1.2, "charisma": 5},
            quantity=1
        )
    
    def load_enemies(self):
        """Load all enemy data."""
        # Basic enemies
        self.enemies["wandering_hollow"] = Enemy(
            id="wandering_hollow",
            name="Wandering Hollow",
            description="A hollowed out corpse that wanders aimlessly. It's eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=1,
            hp=50,
            attack=10,
            defense=5,
            attack_patterns=[{"name": "Basic Attack", "damage": 10, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=10
        )
        
        self.enemies["fallen_knight"] = Enemy(
            id="fallen_knight",
            name="Fallen Knight",
            description="A knight in armor that has been hollowed out. Its eyes are dark and lifeless, reflecting the corruption that has consumed it.",
            level=2,
            hp=70,
            attack=15,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 15, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=20
        )
        
        # Add more enemies as needed...
    
    def load_bosses(self):
        """Load all boss data."""
        # Basic bosses
        self.bosses["hollow_citizen"] = Enemy(
            id="hollow_citizen",
            name="Hollow Citizen",
            description="A hollowed out citizen that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=3,
            hp=100,
            attack=20,
            defense=10,
            attack_patterns=[{"name": "Basic Attack", "damage": 20, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=30
        )
        
        self.bosses["corrupted_guard"] = Enemy(
            id="corrupted_guard",
            name="Corrupted Guard",
            description="A guard in armor that has been corrupted by the darkness. Its eyes are dark and empty, reflecting the corruption that has consumed it.",
            level=4,
            hp=120,
            attack=25,
            defense=15,
            attack_patterns=[{"name": "Basic Attack", "damage": 25, "type": "physical"}],
            loot_table=[{"item_id": "homeward_bone", "chance": 0.5}],
            essence=40
        )
        
        # Add more bosses as needed...
    
    def load_quests(self):
        """Load all quest data."""
        # Basic quests
        self.quests["highcastle_quest"] = Quest(
            id="highcastle_quest",
            name="Highcastle Quest",
            description="Defeat the corrupted guards and restore peace to Highcastle.",
            objectives=[{"type": "kill", "target": "corrupted_guard", "quantity": 2}],
            rewards={"essence": 50, "item": "reinforced_sword"},
            faction="Heroes of Ardenvale"
        )
        
        # Add more quests as needed...

class CombatSystem:
    def __init__(self):
        self.combo_counter = 0
        self.last_attack_time = 0
        self.combo_window = 2.0  # seconds
        self.special_moves = {
            "warrior": {
                "heavy_slash": {"damage_mult": 1.5, "stamina_cost": 20},
                "shield_bash": {"damage": 10, "stamina_cost": 15, "stun_chance": 0.3}
            },
            "knight": {
                "holy_slash": {"damage_mult": 1.3, "stamina_cost": 25, "faith_scaling": True},
                "divine_shield": {"defense_boost": 1.5, "stamina_cost": 30, "duration": 3}
            },
            "pyromancer": {
                "flame_burst": {"damage": 25, "stamina_cost": 35, "intelligence_scaling": True},
                "ember_shield": {"damage_reduction": 0.5, "stamina_cost": 20, "duration": 2}
            },
            "thief": {
                "quick_strike": {"damage_mult": 1.2, "stamina_cost": 15, "dexterity_scaling": True},
                "smoke_bomb": {"evasion_boost": 0.8, "stamina_cost": 25, "duration": 2}
            }
        }
    
    def calculate_damage(self, attacker, defender, attack_type="basic"):
        """Calculate damage based on attack type, stats, and equipment."""
        base_damage = attacker.get_attack_power()
        
        # Apply combo multiplier
        if time.time() - self.last_attack_time < self.combo_window:
            self.combo_counter += 1
            combo_mult = 1.0 + (self.combo_counter * 0.1)  # 10% more damage per combo
        else:
            self.combo_counter = 0
            combo_mult = 1.0
            
        self.last_attack_time = time.time()
        
        # Apply special move effects
        if attack_type != "basic":
            move = self.special_moves[attacker.character_class.lower()][attack_type]
            if "damage_mult" in move:
                base_damage *= move["damage_mult"]
            if "damage" in move:
                base_damage = move["damage"]
                
            # Apply stat scaling
            if "faith_scaling" in move and move["faith_scaling"]:
                base_damage += attacker.faith // 2
            if "intelligence_scaling" in move and move["intelligence_scaling"]:
                base_damage += attacker.intelligence // 2
            if "dexterity_scaling" in move and move["dexterity_scaling"]:
                base_damage += attacker.dexterity // 2
                
            # Apply stamina cost
            attacker.stamina = max(0, attacker.stamina - move["stamina_cost"])
        
        # Apply stance modifiers
        if attacker.stance == "aggressive":
            base_damage *= 1.2
        elif attacker.stance == "defensive":
            base_damage *= 0.8
            
        # Calculate final damage
        final_damage = int(base_damage * combo_mult)
        return defender.take_damage(final_damage)
    
    def get_available_moves(self, player):
        """Get available special moves for the player's class."""
        return self.special_moves[player.character_class.lower()]
    
    def display_combat_ui(self, player, enemy):
        """Display a visual combat interface."""
        clear_screen()
        print(DIVIDER)
        print(f"⚔️ COMBAT ⚔️")
        print(DIVIDER)
        
        # Display health bars
        print(f"\n{player.name} (Level {player.level})")
        print(f"HP: {display_bar(player.hp, player.max_hp)}")
        print(f"SP: {display_bar(player.stamina, player.max_stamina)}")
        
        print(f"\n{enemy.name} (Level {enemy.level})")
        print(f"HP: {display_bar(enemy.hp, enemy.max_hp)}")
        
        # Display stance and available moves
        print(f"\nStance: {player.stance.upper()}")
        print("\nAvailable Moves:")
        for move_name, move_data in self.get_available_moves(player).items():
            print(f"- {move_name.replace('_', ' ').title()}")
            print(f"  Stamina Cost: {move_data['stamina_cost']}")
        
        print(DIVIDER)

class QuestSystem:
    def __init__(self):
        self.active_quests = {}
        self.completed_quests = set()
        self.lore_discovered = set()
        self.faction_reputation = {
            "Heroes of Ardenvale": 0,
            "Children of Dark": 0,
            "Ashen Order": 0,
            "Highcastle Guard": 0
        }
        
        # Lore categories
        self.lore_categories = {
            "history": "Ancient tales of Ardenvale's past",
            "legends": "Myths and legends passed down through generations",
            "secrets": "Hidden knowledge and forbidden lore",
            "characters": "Stories of important figures in the world"
        }
    
    def start_quest(self, quest_id: str, quest_data: Dict):
        """Start a new quest."""
        if quest_id in self.active_quests:
            return False
            
        self.active_quests[quest_id] = {
            "data": quest_data,
            "progress": {obj["type"]: 0 for obj in quest_data["objectives"]},
            "start_time": datetime.datetime.now()
        }
        return True
    
    def update_quest_progress(self, quest_id: str, objective_type: str, amount: int = 1):
        """Update progress for a quest objective."""
        if quest_id not in self.active_quests:
            return False
            
        quest = self.active_quests[quest_id]
        if objective_type in quest["progress"]:
            quest["progress"][objective_type] += amount
            return True
        return False
    
    def check_quest_completion(self, quest_id: str) -> bool:
        """Check if a quest is complete and handle rewards."""
        if quest_id not in self.active_quests:
            return False
            
        quest = self.active_quests[quest_id]
        completed = True
        
        for objective in quest["data"]["objectives"]:
            if quest["progress"][objective["type"]] < objective["quantity"]:
                completed = False
                break
                
        if completed:
            self.complete_quest(quest_id)
            return True
            
        return False
    
    def complete_quest(self, quest_id: str):
        """Complete a quest and grant rewards."""
        quest = self.active_quests[quest_id]
        
        # Grant rewards
        if "rewards" in quest["data"]:
            rewards = quest["data"]["rewards"]
            if "essence" in rewards:
                # Add essence to player
                pass
            if "item" in rewards:
                # Add item to player inventory
                pass
            if "faction" in rewards:
                # Update faction reputation
                self.faction_reputation[rewards["faction"]] += rewards.get("reputation", 0)
        
        # Add to completed quests
        self.completed_quests.add(quest_id)
        del self.active_quests[quest_id]
        
        # Discover lore if quest has associated lore
        if "lore" in quest["data"]:
            self.discover_lore(quest["data"]["lore"])
    
    def discover_lore(self, lore_id: str):
        """Add discovered lore to the player's collection."""
        self.lore_discovered.add(lore_id)
    
    def get_quest_status(self, quest_id: str) -> Dict:
        """Get the current status of a quest."""
        if quest_id in self.active_quests:
            quest = self.active_quests[quest_id]
            return {
                "name": quest["data"]["name"],
                "description": quest["data"]["description"],
                "progress": quest["progress"],
                "objectives": quest["data"]["objectives"]
            }
        elif quest_id in self.completed_quests:
            return {
                "name": "Completed Quest",
                "status": "completed"
            }
        return None
    
    def display_quest_log(self):
        """Display the quest log with active and completed quests."""
        clear_screen()
        print(DIVIDER)
        print("📜 QUEST LOG 📜")
        print(DIVIDER)
        
        if not self.active_quests and not self.completed_quests:
            print("\nNo quests available.")
            return
            
        if self.active_quests:
            print("\nActive Quests:")
            for quest_id, quest in self.active_quests.items():
                print(f"\n{quest['data']['name']}")
                print(f"Description: {quest['data']['description']}")
                print("Progress:")
                for objective in quest['data']['objectives']:
                    progress = quest['progress'][objective['type']]
                    print(f"- {objective['type']}: {progress}/{objective['quantity']}")
        
        if self.completed_quests:
            print("\nCompleted Quests:")
            for quest_id in self.completed_quests:
                print(f"- {quest_id}")
        
        print(DIVIDER)
    
    def display_lore(self):
        """Display discovered lore entries."""
        clear_screen()
        print(DIVIDER)
        print("📚 LORE COLLECTION 📚")
        print(DIVIDER)
        
        if not self.lore_discovered:
            print("\nNo lore discovered yet.")
            return
            
        for category, description in self.lore_categories.items():
            print(f"\n{category.upper()}")
            print(f"{description}")
            # Display lore entries in this category
            # Implementation depends on how lore is stored
        
        print(DIVIDER)

class UISystem:
    def __init__(self):
        self.colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "purple": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "reset": "\033[0m"
        }
        
        # UI elements
        self.frames = {
            "single": {
                "top_left": "┌",
                "top_right": "┐",
                "bottom_left": "└",
                "bottom_right": "┘",
                "horizontal": "─",
                "vertical": "│"
            },
            "double": {
                "top_left": "╔",
                "top_right": "╗",
                "bottom_left": "╚",
                "bottom_right": "╝",
                "horizontal": "═",
                "vertical": "║"
            }
        }
    
    def create_frame(self, content: str, frame_type: str = "single", title: str = None) -> str:
        """Create a framed box around content."""
        frame = self.frames[frame_type]
        lines = content.split("\n")
        width = max(len(line) for line in lines)
        
        if title:
            width = max(width, len(title) + 4)
            title_line = f"{frame['horizontal']} {title} {' ' * (width - len(title) - 2)}{frame['horizontal']}"
        else:
            title_line = frame['horizontal'] * (width + 2)
            
        result = [f"{frame['top_left']}{title_line}{frame['top_right']}"]
        
        for line in lines:
            padding = ' ' * (width - len(line))
            result.append(f"{frame['vertical']} {line}{padding} {frame['vertical']}")
            
        result.append(f"{frame['bottom_left']}{frame['horizontal'] * (width + 2)}{frame['bottom_right']}")
        return "\n".join(result)
    
    def display_title_screen(self):
        """Display the game's title screen."""
        clear_screen()
        print(TITLE_ART)
        print("\n" + " " * 20 + "A REALM SHATTERED BY A FADING FLAME")
        print("\n" + " " * 25 + "[N] New Game")
        print(" " * 25 + "[L] Load Game")
        print(" " * 25 + "[Q] Quit")
    
    def display_location(self, location: Location):
        """Display location information with ASCII art."""
        clear_screen()
        print(DIVIDER)
        print(f"📍 {location.name}")
        print(DIVIDER)
        
        # Display map if available
        if location.map_art:
            print("\n" + location.map_art)
        
        # Display description
        print("\n" + location.description)
        
        # Display first visit text if applicable
        if not location.visited and location.first_visit_text:
            print("\n" + self.colors["yellow"] + location.first_visit_text + self.colors["reset"])
            location.visited = True
        
        # Display connections
        print("\n" + location.get_connections_string())
        
        # Display NPCs if present
        if location.npcs:
            print("\nNPCs present:")
            for npc_id in location.npcs:
                print(f"- {npc_id}")
        
        print(DIVIDER)
    
    def display_inventory(self, player: Player):
        """Display the player's inventory with ASCII art."""
        clear_screen()
        print(DIVIDER)
        print("🎒 INVENTORY")
        print(DIVIDER)
        
        # Display equipment
        print("\nEQUIPPED:")
        for slot, item in player.equipment.items():
            if item:
                print(f"{slot.title()}: {item.name}")
            else:
                print(f"{slot.title()}: None")
        
        # Display inventory
        print("\nINVENTORY:")
        if not player.inventory:
            print("Empty")
        else:
            for i, item in enumerate(player.inventory):
                equipped = " (Equipped)" if item.equipped else ""
                quantity = f" x{item.quantity}" if item.quantity > 1 else ""
                print(f"{i+1}. {item.name}{equipped}{quantity}")
                print(f"   {item.description}")
        
        print(DIVIDER)
    
    def display_character_sheet(self, player: Player):
        """Display the player's character sheet with ASCII art."""
        clear_screen()
        print(DIVIDER)
        print("👤 CHARACTER SHEET")
        print(DIVIDER)
        
        # Basic info
        print(f"\nName: {player.name}")
        print(f"Class: {player.character_class}")
        print(f"Level: {player.level}")
        print(f"Essence: {player.essence}")
        
        # Stats
        print("\nSTATS:")
        print(f"HP: {display_bar(player.hp, player.max_hp)}")
        print(f"Stamina: {display_bar(player.stamina, player.max_stamina)}")
        print(f"Strength: {player.strength}")
        print(f"Dexterity: {player.dexterity}")
        print(f"Intelligence: {player.intelligence}")
        print(f"Faith: {player.faith}")
        print(f"Vitality: {player.vitality}")
        print(f"Endurance: {player.endurance}")
        
        print(DIVIDER)
    
    def display_dialogue(self, npc: NPC, dialogue: Dict):
        """Display dialogue with an NPC."""
        clear_screen()
        print(DIVIDER)
        print(f"💭 {npc.name}")
        print(DIVIDER)
        
        print(f"\n{npc.description}\n")
        print(dialogue["text"])
        
        if "options" in dialogue:
            print("\nOptions:")
            for key, option in dialogue["options"].items():
                print(f"{key}. {option['text']}")
        
        print(DIVIDER)
    
    def display_notification(self, message: str, color: str = "white"):
        """Display a notification message."""
        print(f"\n{self.colors[color]}{message}{self.colors['reset']}")
    
    def display_loading_screen(self, message: str = "Loading..."):
        """Display a loading screen with animation."""
        clear_screen()
        print(DIVIDER)
        print("\n" + " " * 25 + message)
        
        for i in range(3):
            print("\r" + " " * 25 + "." * (i + 1), end="", flush=True)
            time.sleep(0.5)
        
        print("\n" + DIVIDER)

class Quest:
    def __init__(self, id: str, name: str, description: str, objectives: List[Dict],
                 rewards: Dict, faction: str = None, lore: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.objectives = objectives  # List of dicts with 'type', 'target', 'quantity'
        self.rewards = rewards  # Dict with keys like 'essence', 'item', 'reputation'
        self.faction = faction
        self.lore = lore
        
    def to_dict(self) -> Dict:
        """Convert quest to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "objectives": self.objectives,
            "rewards": self.rewards,
            "faction": self.faction,
            "lore": self.lore
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Quest':
        """Create a quest from dictionary data."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            objectives=data["objectives"],
            rewards=data["rewards"],
            faction=data.get("faction"),
            lore=data.get("lore")
        )

class GameEngine:
    def __init__(self):
        """Initialize the game engine."""
        self.player = None
        self.world = World()
        self.ui = UISystem()
        self.combat = CombatSystem()
        self.quests = QuestSystem()
        self.running = False
        self.current_location = None
        self.autosave_interval = 15 * 60  # 15 minutes
        self.last_autosave = time.time()
        
        # Function mappings for commands
        self.commands = {
            # Movement
            "go": self.go_direction,
            "move": self.go_direction,
            "north": lambda: self.go_direction("north"),
            "south": lambda: self.go_direction("south"),
            "east": lambda: self.go_direction("east"),
            "west": lambda: self.go_direction("west"),
            "n": lambda: self.go_direction("north"),
            "s": lambda: self.go_direction("south"),
            "e": lambda: self.go_direction("east"),
            "w": lambda: self.go_direction("west"),
            
            # Actions
            "look": self.look,
            "examine": self.examine,
            "talk": self.talk_to_npc,
            "attack": self.attack_enemy,
            "rest": self.rest,
            "use": self.use_item,
            
            # Inventory
            "inventory": self.show_inventory,
            "i": self.show_inventory,
            "equip": self.equip_item,
            "unequip": self.unequip_item,
            "drop": self.drop_item,
            
            # Character
            "character": self.show_character,
            "c": self.show_character,
            "level": self.level_up,
            "stats": self.show_character,
            
            # Game
            "help": self.show_help,
            "save": self.save_game,
            "load": self.load_game,
            "quit": self.quit_game,
            "exit": self.quit_game,
            
            # Quests
            "quests": self.show_quests,
            "q": self.show_quests,
            "lore": self.show_lore,
            
            # Combat
            "stance": self.change_stance
        }
        
    def create_character(self):
        """Create a new character with player input."""
        clear_screen()
        print(TITLE_ART)
        print("\nCHARACTER CREATION")
        print(DIVIDER)
        
        name = input("\nEnter your character's name: ")
        
        print("\nChoose your character class:")
        print("1. Warrior - Strong and resilient, specializes in heavy weapons")
        print("2. Knight - Balanced fighter with good defense and offense")
        print("3. Pyromancer - Wields flame and arcane abilities")
        print("4. Thief - Quick and deadly, excels with light weapons and evasion")
        
        valid_choice = False
        while not valid_choice:
            choice = input("\nEnter your choice (1-4): ")
            if choice == "1":
                character_class = "Warrior"
                valid_choice = True
            elif choice == "2":
                character_class = "Knight"
                valid_choice = True
            elif choice == "3":
                character_class = "Pyromancer"
                valid_choice = True
            elif choice == "4":
                character_class = "Thief"
                valid_choice = True
            else:
                print("Invalid choice. Please try again.")
        
        self.player = Player(name, character_class)
        print(f"\nWelcome, {name} the {character_class}!")
        time.sleep(2)
        
        # Start at the default location
        self.current_location = self.world.locations["highcastle_entrance"]
        self.player.discovered_locations.add("highcastle_entrance")
    
    def go_direction(self, direction: str):
        """Move in the specified direction."""
        if direction in self.current_location.connections:
            target_location_id = self.current_location.connections[direction]
            if target_location_id in self.world.locations:
                self.current_location = self.world.locations[target_location_id]
                self.player.current_location = target_location_id
                
                # Add to discovered locations
                self.player.discovered_locations.add(target_location_id)
                
                # Display the new location
                self.ui.display_location(self.current_location)
                
                # Check for random encounter
                if random.random() < 0.3 and self.current_location.enemies:  # 30% chance
                    enemy_id = random.choice(self.current_location.enemies)
                    if enemy_id in self.world.enemies:
                        enemy = Enemy.from_dict(self.world.enemies[enemy_id].to_dict())
                        self.start_combat(enemy)
            else:
                print(f"Error: Location '{target_location_id}' not found.")
        else:
            print(f"You cannot go {direction} from here.")
    
    def look(self):
        """Look around the current location."""
        self.ui.display_location(self.current_location)
    
    def examine(self, target: str = None):
        """Examine an object or NPC in the current location."""
        if not target:
            print("What do you want to examine?")
            return
            
        # Check if it's an NPC
        for npc_id in self.current_location.npcs:
            if npc_id.lower() == target.lower() or self.world.npcs[npc_id].name.lower() == target.lower():
                npc = self.world.npcs[npc_id]
                print(f"\n{npc.name}")
                print(f"{npc.description}")
                return
                
        # Check if it's an item in the inventory
        for item in self.player.inventory:
            if item.name.lower() == target.lower():
                print(f"\n{item.name}")
                print(f"{item.description}")
                if item.stats:
                    print("Stats:")
                    for stat, value in item.stats.items():
                        print(f"- {stat}: {value}")
                return
                
        print(f"You don't see any {target} here.")
    
    def talk_to_npc(self, target: str = None):
        """Talk to an NPC in the current location."""
        if not target:
            print("Who do you want to talk to?")
            return
            
        # Find the NPC
        for npc_id in self.current_location.npcs:
            if npc_id.lower() == target.lower() or self.world.npcs[npc_id].name.lower() == target.lower():
                npc = self.world.npcs[npc_id]
                
                # Get initial dialogue
                dialogue = npc.get_dialogue()
                
                # Dialog loop
                while True:
                    clear_screen()
                    print(DIVIDER)
                    print(f"💭 {npc.name}")
                    print(DIVIDER)
                    
                    # Display NPC description on first meeting
                    if not npc.met:
                        print(f"\n{npc.description}\n")
                        npc.met = True
                    
                    # Display NPC dialogue
                    print(f"\n{npc.name}: {dialogue['text']}")
                    
                    # Display player response options
                    if "options" in dialogue:
                        print("\nHow will you respond?")
                        for key, option in dialogue["options"].items():
                            print(f"{key}. {option['text']}")
                        print("q. [End conversation]")
                        
                        choice = input("\nYour choice: ")
                        if choice.lower() == 'q':
                            return
                            
                        if choice in dialogue["options"]:
                            # Get NPC response to your choice
                            player_choice_text = dialogue["options"][choice]["text"]
                            npc_response = npc.respond(choice)
                            
                            # Show the conversation exchange
                            print(f"\nYou: {player_choice_text}")
                            print(f"\n{npc.name}: {npc_response}")
                            input("\nPress Enter to continue...")
                            
                            # Update dialogue for next loop
                            dialogue = npc.get_dialogue()
                        else:
                            print("Invalid choice.")
                            input("\nPress Enter to continue...")
                    else:
                        # No more dialogue options
                        input("\nPress Enter to end conversation...")
                        return
                
                return
                
        print(f"There's no one named {target} here.")
    
    def attack_enemy(self, target: str = None):
        """Initiate combat with an enemy."""
        if not target:
            print("What do you want to attack?")
            return
            
        # Check if the enemy is in this location
        for enemy_id in self.current_location.enemies:
            if enemy_id.lower() == target.lower() or (enemy_id in self.world.enemies and 
                self.world.enemies[enemy_id].name.lower() == target.lower()):
                
                enemy = Enemy.from_dict(self.world.enemies[enemy_id].to_dict())
                self.start_combat(enemy)
                return
                
        print(f"There's no {target} here to attack.")
    
    def rest(self):
        """Rest at a beacon to restore health and flask."""
        if not self.current_location.is_beacon:
            print("You can only rest at beacons.")
            return
            
        print("You rest at the beacon. Your health, stamina, and Estus Flasks are restored.")
        self.player.rest_at_beacon()
        
        # Check for autosave
        self.autosave()
    
    def use_item(self, item_name: str = None):
        """Use an item from inventory."""
        if not item_name:
            print("What do you want to use?")
            return
            
        # Find the item in inventory
        for i, item in enumerate(self.player.inventory):
            if item.name.lower() == item_name.lower():
                if not item.usable:
                    print(f"You cannot use the {item.name}.")
                    return
                    
                result = self.player.use_item(i)
                print(result)
                return
                
        # Special case for Estus Flask
        if item_name.lower() in ["estus", "flask", "estus flask"]:
            if self.player.use_estus():
                heal_amount = int(self.player.max_hp * 0.4)
                print(f"You drink from your Estus Flask and recover {heal_amount} health.")
            else:
                print("Your Estus Flask is empty.")
            return
                
        print(f"You don't have a {item_name}.")
    
    def show_inventory(self):
        """Display the player's inventory."""
        self.ui.display_inventory(self.player)
    
    def equip_item(self, item_name: str = None):
        """Equip an item from inventory."""
        if not item_name:
            print("What do you want to equip?")
            return
            
        # Find the item in inventory
        for item in self.player.inventory:
            if item.name.lower() == item_name.lower():
                if not item.equippable:
                    print(f"You cannot equip the {item.name}.")
                    return
                    
                result = self.player.equip_item(item)
                print(result)
                return
                
        print(f"You don't have a {item_name}.")
    
    def unequip_item(self, slot: str = None):
        """Unequip an item from a specified slot."""
        if not slot:
            print("Which slot do you want to unequip? (weapon/shield/armor/ring1/ring2/amulet)")
            return
            
        if slot.lower() not in self.player.equipment:
            print(f"Invalid equipment slot: {slot}")
            return
            
        result = self.player.unequip_item(slot.lower())
        print(result)
    
    def drop_item(self, item_name: str = None):
        """Drop an item from inventory."""
        if not item_name:
            print("What do you want to drop?")
            return
            
        # Find the item in inventory
        for item in self.player.inventory:
            if item.name.lower() == item_name.lower():
                if item.equipped:
                    print(f"You must unequip {item.name} before dropping it.")
                    return
                    
                if self.player.remove_item(item):
                    print(f"You dropped {item.name}.")
                else:
                    print(f"Failed to drop {item.name}.")
                return
                
        print(f"You don't have a {item_name}.")
    
    def show_character(self):
        """Display the character sheet."""
        self.ui.display_character_sheet(self.player)
    
    def level_up(self, stat: str = None):
        """Level up a character stat."""
        cost = self.player.calculate_level_cost()
        
        if not stat:
            clear_screen()
            print(DIVIDER)
            print("LEVEL UP")
            print(DIVIDER)
            print(f"\nYou have {self.player.essence} essence.")
            print(f"Cost to level up: {cost} essence.")
            
            print("\nCurrent Stats:")
            print(f"1. Strength: {self.player.strength}")
            print(f"2. Dexterity: {self.player.dexterity}")
            print(f"3. Intelligence: {self.player.intelligence}")
            print(f"4. Faith: {self.player.faith}")
            print(f"5. Vitality: {self.player.vitality}")
            print(f"6. Endurance: {self.player.endurance}")
            
            choice = input("\nEnter stat to level up (1-6), or 'q' to cancel: ")
            
            if choice.lower() == 'q':
                return
                
            stat_map = {
                "1": "strength",
                "2": "dexterity",
                "3": "intelligence",
                "4": "faith",
                "5": "vitality",
                "6": "endurance"
            }
            
            if choice in stat_map:
                stat = stat_map[choice]
            else:
                print("Invalid choice.")
                return
        
        # Attempt to level up
        if self.player.level_up(stat):
            print(f"You leveled up {stat} to {getattr(self.player, stat)}!")
        else:
            print(f"Not enough essence. You need {cost} essence.")
    
    def change_stance(self, new_stance: str = None):
        """Change combat stance."""
        valid_stances = ["balanced", "aggressive", "defensive"]
        
        if not new_stance:
            print("\nAvailable stances:")
            print("1. Balanced - Standard attack and defense")
            print("2. Aggressive - +20% attack, -20% defense")
            print("3. Defensive - +20% defense, -20% attack")
            
            choice = input("\nChoose a stance (1-3): ")
            
            if choice == "1":
                new_stance = "balanced"
            elif choice == "2":
                new_stance = "aggressive"
            elif choice == "3":
                new_stance = "defensive"
            else:
                print("Invalid choice.")
                return
        
        if new_stance.lower() in valid_stances:
            result = self.player.change_stance(new_stance.lower())
            print(result)
        else:
            print(f"Invalid stance. Choose from: {', '.join(valid_stances)}")
    
    def show_help(self):
        """Display available commands."""
        clear_screen()
        print(DIVIDER)
        print("HELP")
        print(DIVIDER)
        
        print("\nMovement:")
        print("  go/move [direction] - Move in the specified direction")
        print("  north/n, south/s, east/e, west/w - Move in that direction")
        
        print("\nActions:")
        print("  look - Look around the current location")
        print("  examine [object] - Examine an object or NPC")
        print("  talk [npc] - Talk to an NPC")
        print("  attack [enemy] - Attack an enemy")
        print("  rest - Rest at a beacon to restore health and flask")
        print("  use [item] - Use an item from inventory")
        
        print("\nInventory:")
        print("  inventory/i - Show inventory")
        print("  equip [item] - Equip an item")
        print("  unequip [slot] - Unequip an item from a slot")
        print("  drop [item] - Drop an item")
        
        print("\nCharacter:")
        print("  character/c/stats - Show character sheet")
        print("  level - Level up a stat")
        print("  stance - Change combat stance")
        
        print("\nQuests:")
        print("  quests/q - Show quest log")
        print("  lore - Show discovered lore")
        
        print("\nGame:")
        print("  save - Save the game")
        print("  load - Load a saved game")
        print("  quit/exit - Exit the game")
        
        print(DIVIDER)
    
    def show_quests(self):
        """Display the quest log."""
        self.quests.display_quest_log()
    
    def show_lore(self):
        """Display discovered lore."""
        self.quests.display_lore()
    
    def save_game(self, filename: str = None):
        """Save the game state."""
        try:
            save_path = save_game(self.player, self.world, filename)
            print(f"Game saved to {save_path}")
        except Exception as e:
            print(f"Error saving game: {e}")
    
    def load_game(self, filename: str = None):
        """Load a saved game."""
        if not filename:
            saves = list_saves()
            if not saves:
                print("No save files found.")
                return
            
            print("\nAvailable save files:")
            for i, save in enumerate(saves):
                info = get_save_info(save)
                print(f"{i+1}. {info.get('player_name', 'Unknown')} - Level {info.get('player_level', '?')} - {info.get('timestamp', 'Unknown')}")
            
            choice = input("\nEnter save number to load, or 'q' to cancel: ")
            if choice.lower() == 'q':
                return
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(saves):
                    filename = saves[index]
                else:
                    print("Invalid choice.")
                    return
            except ValueError:
                print("Invalid choice.")
                return
        
        try:
            self.player, self.world = load_game(filename)
            self.current_location = self.world.locations[self.player.current_location]
            print("Game loaded successfully.")
            
            # Display current location
            self.ui.display_location(self.current_location)
        except Exception as e:
            print(f"Error loading game: {e}")
    
    def quit_game(self):
        """Quit the game."""
        choice = input("Do you want to save before quitting? (y/n): ")
        if choice.lower() == 'y':
            self.save_game()
        
        self.running = False
        print("Thanks for playing! Goodbye.")
    
    def start_combat(self, enemy):
        """Start a combat encounter with an enemy."""
        print(f"\nA {enemy.name} approaches! Prepare for battle!")
        time.sleep(1)
        
        combat_active = True
        player_turn = True
        
        while combat_active:
            self.combat.display_combat_ui(self.player, enemy)
            
            if player_turn:
                print("\nYour turn!")
                print("1. Basic Attack")
                print("2. Special Move")
                print("3. Use Item")
                print("4. Change Stance")
                print("5. Flee")
                
                choice = input("\nChoose your action: ")
                
                if choice == "1":
                    # Basic attack
                    damage = self.combat.calculate_damage(self.player, enemy)
                    print(f"You attack the {enemy.name} for {damage} damage!")
                    
                    if enemy.is_dead():
                        self.handle_enemy_defeat(enemy)
                        combat_active = False
                        continue
                        
                elif choice == "2":
                    # Special move
                    moves = self.combat.get_available_moves(self.player)
                    print("\nAvailable Special Moves:")
                    
                    move_list = list(moves.keys())
                    for i, move_name in enumerate(move_list):
                        move = moves[move_name]
                        print(f"{i+1}. {move_name.replace('_', ' ').title()} - Stamina: {move['stamina_cost']}")
                    
                    move_choice = input("\nChoose a special move (or 'b' to go back): ")
                    if move_choice.lower() == 'b':
                        continue
                        
                    try:
                        index = int(move_choice) - 1
                        if 0 <= index < len(move_list):
                            move_name = move_list[index]
                            
                            # Check if enough stamina
                            move = moves[move_name]
                            if self.player.stamina < move["stamina_cost"]:
                                print("Not enough stamina!")
                                continue
                                
                            # Execute special move
                            damage = self.combat.calculate_damage(self.player, enemy, move_name)
                            print(f"You use {move_name.replace('_', ' ').title()} on the {enemy.name} for {damage} damage!")
                            
                            # Apply special effects
                            if "stun_chance" in move and random.random() < move["stun_chance"]:
                                print(f"The {enemy.name} is stunned!")
                                player_turn = True  # Get another turn
                            
                            if enemy.is_dead():
                                self.handle_enemy_defeat(enemy)
                                combat_active = False
                                continue
                        else:
                            print("Invalid choice.")
                            continue
                    except ValueError:
                        print("Invalid choice.")
                        continue
                
                elif choice == "3":
                    # Use item
                    if not self.player.inventory:
                        print("You have no items!")
                        continue
                        
                    print("\nInventory:")
                    usable_items = []
                    for i, item in enumerate(self.player.inventory):
                        if item.usable:
                            print(f"{len(usable_items)+1}. {item.name} x{item.quantity}")
                            usable_items.append(i)
                    
                    # Add Estus Flask
                    print(f"{len(usable_items)+1}. Estus Flask ({self.player.estus_flask['current']}/{self.player.estus_flask['max']})")
                    
                    item_choice = input("\nChoose an item to use (or 'b' to go back): ")
                    if item_choice.lower() == 'b':
                        continue
                        
                    try:
                        index = int(item_choice) - 1
                        if 0 <= index < len(usable_items):
                            result = self.player.use_item(usable_items[index])
                            print(result)
                        elif index == len(usable_items):
                            # Use Estus Flask
                            if self.player.use_estus():
                                heal_amount = int(self.player.max_hp * 0.4)
                                print(f"You drink from your Estus Flask and recover {heal_amount} health.")
                            else:
                                print("Your Estus Flask is empty!")
                                continue
                        else:
                            print("Invalid choice.")
                            continue
                    except ValueError:
                        print("Invalid choice.")
                        continue
                
                elif choice == "4":
                    # Change stance
                    self.change_stance()
                    continue  # Don't end turn
                
                elif choice == "5":
                    # Attempt to flee
                    if random.random() < 0.6:  # 60% chance to flee
                        print("You successfully fled from the battle!")
                        combat_active = False
                        continue
                    else:
                        print("You failed to flee!")
                
                else:
                    print("Invalid choice.")
                    continue
                
                player_turn = False
            
            else:
                # Enemy turn
                print(f"\n{enemy.name}'s turn!")
                time.sleep(1)
                
                attack = enemy.get_next_attack()
                damage = self.player.take_damage(attack["damage"], attack["type"])
                
                print(f"The {enemy.name} attacks you with {attack['name']} for {damage} damage!")
                
                if self.player.is_dead():
                    self.handle_player_death()
                    combat_active = False
                    continue
                
                # Check for boss phase transition
                if isinstance(enemy, Boss):
                    if enemy.update_phase():
                        print(f"The {enemy.name} enters a new phase!")
                
                player_turn = True
                
                # Restore some stamina each turn
                self.player.restore_stamina(5)
    
    def handle_enemy_defeat(self, enemy):
        """Handle enemy defeat and rewards."""
        print(f"\nYou defeated the {enemy.name}!")
        
        # Award essence
        self.player.essence += enemy.essence
        print(f"You gained {enemy.essence} essence.")
        
        # Award loot
        drops = enemy.drop_loot()
        if drops:
            print("You found:")
            for item in drops:
                self.player.add_item(item)
                print(f"- {item.name}")
        
        # Update quest progress if applicable
        for quest_id in self.quests.active_quests:
            quest = self.quests.active_quests[quest_id]
            for objective in quest["data"]["objectives"]:
                if objective["type"] == "kill" and objective["target"] == enemy.id:
                    self.quests.update_quest_progress(quest_id, "kill")
                    if self.quests.check_quest_completion(quest_id):
                        print(f"Quest completed: {quest['data']['name']}")
        
        # Mark enemy as killed in player records
        if enemy.id in self.player.killed_enemies:
            self.player.killed_enemies[enemy.id] += 1
        else:
            self.player.killed_enemies[enemy.id] = 1
    
    def handle_player_death(self):
        """Handle player death consequences."""
        clear_screen()
        print("\nYOU DIED")
        print("\nThe darkness claims you, but your journey is not over...")
        time.sleep(3)
        
        # Lose essence and set respawn point
        self.player.die()
        
        # Respawn at last beacon
        beacon_found = False
        for location_id, location in self.world.locations.items():
            if location.is_beacon and location_id in self.player.discovered_locations:
                self.current_location = location
                self.player.current_location = location_id
                beacon_found = True
                break
        
        if not beacon_found:
            # Respawn at starting location as fallback
            self.current_location = self.world.locations["highcastle_entrance"]
            self.player.current_location = "highcastle_entrance"
        
        # Restore minimal health
        self.player.hp = self.player.max_hp // 2
        
        print(f"\nYou awaken at {self.current_location.name}.")
        if self.player.lost_essence > 0:
            print(f"You lost {self.player.lost_essence} essence. Return to where you died to recover it.")
        
        time.sleep(2)
    
    def autosave(self):
        """Perform an autosave if enough time has passed."""
        current_time = time.time()
        if current_time - self.last_autosave >= self.autosave_interval:
            try:
                save_game(self.player, self.world, AUTOSAVE_FILE)
                self.last_autosave = current_time
                print("Game autosaved.")
            except Exception as e:
                print(f"Autosave failed: {e}")
    
    def process_command(self, command_string: str):
        """Process a command string from the player."""
        command_string = command_string.lower().strip()
        
        if not command_string:
            return
            
        # Split the command into parts
        parts = command_string.split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Execute the command if it exists
        if command in self.commands:
            cmd_func = self.commands[command]
            
            # Check if it's a parameterless function or needs arguments
            if args:
                # Join the rest as a single string for commands that expect it
                arg_str = " ".join(args)
                if callable(cmd_func):
                    try:
                        cmd_func(arg_str)
                    except TypeError:
                        # If it doesn't accept an argument, call it without
                        cmd_func()
            else:
                cmd_func()
        else:
            print(f"Unknown command: {command}. Type 'help' for a list of commands.")
    
    def run(self):
        """Run the main game loop."""
        self.running = True
        
        # Display title screen
        self.ui.display_title_screen()
        
        # Main menu
        while self.running:
            choice = input("\nEnter your choice: ").lower()
            
            if choice == 'n':
                # New game
                self.create_character()
                
                # Main game loop
                self.ui.display_location(self.current_location)
                
                while self.running:
                    command = input("\n> ")
                    self.process_command(command)
                    
                    # Check for autosave
                    self.autosave()
                    
            elif choice == 'l':
                # Load game
                self.load_game()
                
                if self.player:
                    # Main game loop
                    while self.running:
                        command = input("\n> ")
                        self.process_command(command)
                        
                        # Check for autosave
                        self.autosave()
                else:
                    # Return to title if no game loaded
                    self.ui.display_title_screen()
                    
            elif choice == 'q':
                print("Thanks for playing! Goodbye.")
                self.running = False
                
            else:
                print("Invalid choice. Please try again.")


def create_item(item_id: str) -> Item:
    """Create an item instance from the item database."""
    # This function would create items based on their ID in a more complete implementation
    # Here we'll just return a placeholder item
    return Item(
        id=item_id,
        name="Unknown Item",
        description="A mysterious item.",
        item_type="misc",
        value=10
    )


# Main entry point
if __name__ == "__main__":
    try:
        # Display welcome message
        clear_screen()
        print("Welcome to ARDENVALE!")
        print("Loading game...")
        time.sleep(1)
        
        # Initialize and run the game
        game = GameEngine()
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Sorry for the inconvenience!")
    finally:
        print("\nThanks for playing ARDENVALE!")