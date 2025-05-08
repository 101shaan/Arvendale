import time
import random
import sys
import os
from typing import Dict, List, Tuple, Any, Optional

from config import DIVIDER, TITLE_ART, BANNER, AUTOSAVE_FILE
from utils import clear_screen, print_slow, print_centered, save_game, load_game, list_saves, get_save_info
from models import Item, Weapon, Armor, Consumable, Inventory
from models_part2 import Player, NPC, Location
from models_part3 import World, Quest
from game_systems import CombatSystem, UISystem, QuestSystem
from game_data import initialize_game_data, create_player

class GameEngine:
    def __init__(self):
        self.player = None
        self.world = None
        self.running = False
        self.combat_system = None
        self.ui_system = UISystem()
        self.quest_system = QuestSystem()
    
    def start(self):
        """Start the game engine."""
        self.running = True
        self.main_menu()
    
    def main_menu(self):
        """Display the main menu."""
        while self.running:
            clear_screen()
            print(TITLE_ART)
            print(DIVIDER)
            print_centered("MAIN MENU")
            print(DIVIDER)
            print("1. New Game")
            print("2. Load Game")
            print("3. Credits")
            print("4. Quit")
            print(DIVIDER)
            
            choice = input("Enter your choice: ").strip()
            
            if choice == "1":
                self.new_game()
            elif choice == "2":
                self.load_game_menu()
            elif choice == "3":
                self.show_credits()
            elif choice == "4":
                self.quit_game()
                break
    
    def new_game(self):
        """Start a new game."""
        clear_screen()
        print(BANNER)
        print_slow("Awaken, Ashen One. The flame fades, and the lords go without thrones.")
        print_slow("What is your name?")
        
        name = input("> ").strip()
        if not name:
            name = "Ashen One"
        
        print_slow(f"Welcome to Ardenvale, {name}. Your journey begins...")
        
        # Initialize game world
        self.world = initialize_game_data()
        
        # Create player
        self.player = create_player(name)
        
        # Set starting location
        self.player.current_location = self.world.get_location_by_id("firelink_shrine")
        self.player.last_beacon = self.player.current_location
        self.player.discovered_locations.append(self.player.current_location)
        
        # Start first quest
        self.player.quest_log.append("ember_quest")
        
        # Start game loop
        self.game_loop()
    
    def load_game_menu(self):
        """Display the load game menu."""
        while True:
            clear_screen()
            print(BANNER)
            print_centered("LOAD GAME")
            print(DIVIDER)
            
            # Get save files
            saves = list_saves()
            
            if not saves:
                print("No save files found.")
                input("Press Enter to return to main menu...")
                return
            
            # Display saves
            print("Available Saves:")
            for i, save_file in enumerate(saves, 1):
                info = get_save_info(save_file)
                if "error" in info:
                    print(f"{i}. {save_file} (Corrupted)")
                else:
                    print(f"{i}. {info['player_name']} - Level {info['player_level']} - {info['location']}")
                    print(f"   Last played: {info['timestamp']}")
            
            print("\n0. Return to Main Menu")
            print(DIVIDER)
            
            choice = input("Enter your choice: ").strip()
            
            if choice == "0":
                return
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(saves):
                    self.load_game(saves[choice_idx])
                    return
            except ValueError:
                pass
    
    def load_game(self, filename: str):
        """Load a saved game."""
        try:
            self.player, self.world = load_game(filename)
            
            # Resolve location IDs
            self.world.resolve_location_ids(self.player)
            
            print_slow(f"Welcome back, {self.player.name}.")
            time.sleep(1)
            
            # Start game loop
            self.game_loop()
        except Exception as e:
            print(f"Error loading save file: {e}")
            input("Press Enter to continue...")
    
    def save_game_menu(self):
        """Display the save game menu."""
        clear_screen()
        print(BANNER)
        print_centered("SAVE GAME")
        print(DIVIDER)
        
        print("1. Quick Save")
        print("2. New Save")
        print("3. Cancel")
        print(DIVIDER)
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            filename = save_game(self.player, self.world, AUTOSAVE_FILE)
            print_slow(f"Game saved to {filename}")
            time.sleep(1)
        elif choice == "2":
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = save_game(self.player, self.world, 
                               os.path.join("saves", f"save_{self.player.name}_{timestamp}.sav"))
            print_slow(f"Game saved to {filename}")
            time.sleep(1)
    
    def show_credits(self):
        """Show game credits."""
        clear_screen()
        print(BANNER)
        print_centered("CREDITS")
        print(DIVIDER)
        
        print_centered("ARDENVALE")
        print_centered("A Dark Fantasy RPG")
        print()
        print_centered("Created by Shaan")
        print()
        print_centered("Inspired by Dark Souls and The Lord of the Rings")
        print()
        print_centered("Thank you for playing!")
        
        input("\nPress Enter to return to main menu...")
    
    def quit_game(self):
        """Quit the game with option to save."""
        clear_screen()
        print(BANNER)
        print_centered("QUIT GAME")
        print(DIVIDER)
        
        if self.player:
            print("Would you like to save your game before quitting?")
            print("1. Yes")
            print("2. No")
            print("3. Cancel")
            print(DIVIDER)
            
            choice = input("Enter your choice: ").strip()
            
            if choice == "1":
                save_game(self.player, self.world, AUTOSAVE_FILE)
                print_slow("Game saved.")
                time.sleep(1)
                self.running = False
            elif choice == "2":
                self.running = False
            # Option 3 implicitly cancels
        else:
            self.running = False
    
    def game_loop(self):
        """Main game loop."""
        autosave_counter = 0
        
        while self.running:
            # Check if player is dead
            if self.player.health <= 0:
                if not self.player.die():
                    print_slow("Game Over")
                    time.sleep(2)
                    self.running = False
                    return
            
            # Autosave every 10 turns
            autosave_counter += 1
            if autosave_counter >= 10:
                save_game(self.player, self.world, AUTOSAVE_FILE)
                autosave_counter = 0
            
            # Update world state
            self.world.update_world_state(self.player)
            
            # Check for combat with enemies at current location
            if self.player.current_location.active_enemies:
                self.enter_combat(self.player.current_location.active_enemies[0])
                continue
            
            # Display location UI
            self.ui_system.draw_location_ui(self.player.current_location)
            
            # Show available commands
            print(DIVIDER)
            print("Commands:")
            print("- look: Examine your surroundings")
            print("- go [direction]: Travel in a direction")
            print("- talk [character]: Speak with a character")
            print("- take [item]: Pick up an item")
            print("- inventory: Check your inventory")
            print("- equip [item]: Equip an item")
            print("- use [item]: Use an item")
            print("- status: View your character status")
            print("- quests: View your quest log")
            print("- map: View the world map")
            print("- rest: Rest at a beacon (if available)")
            print("- save: Save your game")
            print("- help: Show available commands")
            print("- quit: Exit the game")
            print(DIVIDER)
            
            command = input("> ").strip().lower()
            self.parse_command(command)
    
    def parse_command(self, command: str):
        """Parse and execute a player command."""
        # Split command into words
        words = command.split()
        if not words:
            return
        
        action = words[0]
        
        # Look command
        if action == "look":
            self.ui_system.draw_location_ui(self.player.current_location)
            input("Press Enter to continue...")
        
        # Go command
        elif action == "go" and len(words) > 1:
            direction = words[1]
            self.move_player(direction)
        
        # Talk command
        elif action == "talk" and len(words) > 1:
            target = " ".join(words[1:])
            self.talk_to_npc(target)
        
        # Take command
        elif action == "take" and len(words) > 1:
            item_name = " ".join(words[1:])
            self.take_item(item_name)
        
        # Inventory command
        elif action == "inventory":
            self.show_inventory()
        
        # Equip command
        elif action == "equip" and len(words) > 1:
            item_name = " ".join(words[1:])
            self.equip_item(item_name)
        
        # Use command
        elif action == "use" and len(words) > 1:
            item_name = " ".join(words[1:])
            self.use_item(item_name)
        
        # Status command
        elif action == "status":
            self.ui_system.draw_character_ui(self.player)
            input("Press Enter to continue...")
        
        # Quests command
        elif action == "quests":
            self.quest_system.display_quest_log(self.player, self.world)
            input("Press Enter to continue...")
        
        # Map command
        elif action == "map":
            self.ui_system.draw_map_ui(self.player, self.world)
            input("Press Enter to continue...")
        
        # Rest command
        elif action == "rest":
            if self.player.current_location.is_beacon:
                print_slow("You rest at the beacon. Your health and stamina are restored.")
                self.player.rest()
                self.player.last_beacon = self.player.current_location
                # Autosave on rest
                save_game(self.player, self.world, AUTOSAVE_FILE)
                time.sleep(1)
            else:
                print_slow("There is no beacon to rest at in this location.")
                time.sleep(1)
        
        # Save command
        elif action == "save":
            self.save_game_menu()
        
        # Help command
        elif action == "help":
            # This just displays the command list, which is already shown after each turn
            pass
        
        # Quit command
        elif action == "quit":
            self.quit_game()
        
        # Unknown command
        else:
            print_slow("Unknown command. Type 'help' for a list of commands.")
            time.sleep(1)
    
    def move_player(self, direction: str):
        """Move the player in the specified direction."""
        connections = self.player.current_location.connections
        
        if direction in connections:
            destination_id = connections[direction]
            destination = self.world.get_location_by_id(destination_id)
            
            if destination:
                # Check for visit requirements
                can_visit, reason = destination.can_visit(self.player)
                
                if can_visit:
                    # Update player location
                    self.player.previous_location = self.player.current_location
                    self.player.current_location = destination
                    
                    # Add to discovered locations
                    if destination not in self.player.discovered_locations:
                        self.player.discovered_locations.append(destination)
                        
                        # Update quest progress for discovering locations
                        self.quest_system.update_quest_progress(
                            self.player, self.world, "location", destination.id)
                    
                    # Spawn enemies
                    destination.spawn_enemies(self.world)
                else:
                    print_slow(reason)
                    time.sleep(1.5)
            else:
                print_slow("You cannot go that way.")
                time.sleep(1)
        else:
            print_slow(f"You cannot go {direction} from here.")
            time.sleep(1)
    
    def talk_to_npc(self, target: str):
        """Talk to an NPC."""
        npcs = self.world.get_npcs_at_location(self.player.current_location.id)
        
        target = target.lower()
        found_npc = None
        
        for npc in npcs:
            if target in npc.id.lower() or target in npc.name.lower():
                found_npc = npc
                break
        
        if found_npc:
            if found_npc.friendly:
                self.conversation_loop(found_npc)
            else:
                print_slow(f"{found_npc.name} is hostile and cannot be reasoned with!")
                time.sleep(1.5)
                
                # Initiate combat
                self.enter_combat(found_npc)
        else:
            print_slow(f"There is no one called '{target}' here.")
            time.sleep(1)
    
    def conversation_loop(self, npc: NPC):
        """Handle conversation with an NPC."""
        talking = True
        response = None
        
        while talking and self.running:
            clear_screen()
            print(DIVIDER)
            print_centered(f"Conversation with {npc.name}")
            print(DIVIDER)
            
            # Get dialogue and responses
            dialogue_text, responses = npc.talk(self.player, response)
            
            # Display dialogue
            print_slow(f"{npc.name}: {dialogue_text}")
            print()
            
            # Display response options
            print("Your response:")
            for i, (resp_id, resp_text) in enumerate(responses.items(), 1):
                print(f"{i}. {resp_text}")
            
            print(f"{len(responses) + 1}. End conversation")
            print(DIVIDER)
            
            # Get player response
            choice = input("> ").strip()
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(responses):
                    response = list(responses.keys())[choice_idx]
                    
                    # Update quest progress for talking
                    self.quest_system.update_quest_progress(
                        self.player, self.world, "talk", npc.id)
                elif choice_idx == len(responses):
                    talking = False
            except (ValueError, IndexError):
                pass
    
    def take_item(self, item_name: str):
        """Take an item from the current location."""
        items = self.player.current_location.items
        
        if not items:
            print_slow("There are no items here.")
            time.sleep(1)
            return
        
        item_name = item_name.lower()
        found_item = None
        
        for item in items:
            if item_name in item.name.lower() or item_name in item.description.lower():
                found_item = item
                break
        
        if found_item:
            if self.player.inventory.add_item(found_item):
                self.player.current_location.items.remove(found_item)
                print_slow(f"You picked up {found_item.name}.")
                
                # Update quest progress for collecting items
                self.quest_system.update_quest_progress(
                    self.player, self.world, "item", found_item.id)
                
                time.sleep(1)
            else:
                print_slow("Your inventory is full.")
                time.sleep(1)
        else:
            print_slow(f"There is no '{item_name}' here.")
            time.sleep(1)
    
    def show_inventory(self):
        """Show the player's inventory."""
        self.ui_system.draw_inventory_ui(self.player)
        
        # Display inventory management options
        print(DIVIDER)
        print("Inventory Options:")
        print("1. Equip an item")
        print("2. Use an item")
        print("3. Examine an item")
        print("4. Drop an item")
        print("5. Back")
        print(DIVIDER)
        
        choice = input("> ").strip()
        
        if choice == "1":
            # Equip an item
            print("Enter the name of the item to equip:")
            item_name = input("> ").strip()
            self.equip_item(item_name)
        elif choice == "2":
            # Use an item
            print("Enter the name of the item to use:")
            item_name = input("> ").strip()
            self.use_item(item_name)
        elif choice == "3":
            # Examine an item
            print("Enter the name of the item to examine:")
            item_name = input("> ").strip()
            self.examine_item(item_name)
        elif choice == "4":
            # Drop an item
            print("Enter the name of the item to drop:")
            item_name = input("> ").strip()
            self.drop_item(item_name)
    
    def equip_item(self, item_name: str):
        """Equip an item."""
        if not self.player.inventory:
            print_slow("You have no inventory.")
            time.sleep(1)
            return
        
        item_name = item_name.lower()
        found_item = None
        
        for item in self.player.inventory.items:
            if item_name in item.name.lower():
                found_item = item
                break
        
        if found_item:
            if found_item.equippable:
                result = self.player.inventory.equip_item(found_item)
                print_slow(result)
                time.sleep(1)
            else:
                print_slow(f"You cannot equip the {found_item.name}.")
                time.sleep(1)
        else:
            print_slow(f"You don't have a '{item_name}' in your inventory.")
            time.sleep(1)
    
    def use_item(self, item_name: str):
        """Use an item."""
        if not self.player.inventory:
            print_slow("You have no inventory.")
            time.sleep(1)
            return
        
        item_name = item_name.lower()
        found_item = None
        
        for item in self.player.inventory.items:
            if item_name in item.name.lower():
                found_item = item
                break
        
        if found_item:
            if found_item.usable:
                result = found_item.use(self.player)
                print_slow(result)
                time.sleep(1.5)
            else:
                print_slow(f"You cannot use the {found_item.name}.")
                time.sleep(1)
        else:
            print_slow(f"You don't have a '{item_name}' in your inventory.")
            time.sleep(1)
    
    def examine_item(self, item_name: str):
        """Examine an item in detail."""
        if not self.player.inventory:
            print_slow("You have no inventory.")
            time.sleep(1)
            return
        
        item_name = item_name.lower()
        found_item = None
        
        for item in self.player.inventory.items:
            if item_name in item.name.lower():
                found_item = item
                break
        
        if found_item:
            clear_screen()
            print(DIVIDER)
            print_centered(f"Examining: {found_item.name}")
            print(DIVIDER)
            
            print(f"Description: {found_item.description}")
            print(f"Type: {found_item.item_type}")
            print(f"Value: {found_item.value} essence")
            print(f"Weight: {found_item.weight}")
            
            if found_item.item_type == "weapon":
                print(f"Damage: {found_item.damage}")
                print(f"Attack Speed: {found_item.attack_speed}")
                print(f"Durability: {found_item.durability}/{found_item.max_durability}")
                print(f"Stamina Cost: {found_item.stamina_cost}")
                
                if found_item.special_effects:
                    print("\nSpecial Effects:")
                    for effect, value in found_item.special_effects.items():
                        print(f"- {effect.replace('_', ' ').title()}: {value}")
            
            elif found_item.item_type == "armor":
                print(f"Defense: {found_item.defense}")
                print(f"Armor Type: {found_item.armor_type}")
                print(f"Durability: {found_item.durability}/{found_item.max_durability}")
                
                if found_item.resistance:
                    print("\nResistances:")
                    for resist_type, value in found_item.resistance.items():
                        print(f"- {resist_type.title()}: {int(value * 100)}%")
            
            elif found_item.item_type == "consumable":
                print(f"Effect: {found_item.effect_type}")
                print(f"Potency: {found_item.effect_value}")
                if found_item.duration > 0:
                    print(f"Duration: {found_item.duration} turns")
            
            input("\nPress Enter to continue...")
        else:
            print_slow(f"You don't have a '{item_name}' in your inventory.")
            time.sleep(1)
    
    def drop_item(self, item_name: str):
        """Drop an item from inventory."""
        if not self.player.inventory:
            print_slow("You have no inventory.")
            time.sleep(1)
            return
        
        item_name = item_name.lower()
        found_item = None
        
        for item in self.player.inventory.items:
            if item_name in item.name.lower():
                found_item = item
                break
        
        if found_item:
            # Prevent dropping equipped items
            if found_item.equipped:
                print_slow(f"You need to unequip {found_item.name} first.")
                time.sleep(1)
                return
            
            # Confirm drop
            print_slow(f"Are you sure you want to drop {found_item.name}? (y/n)")
            confirm = input("> ").strip().lower()
            
            if confirm == "y" or confirm == "yes":
                self.player.inventory.remove_item(found_item)
                self.player.current_location.items.append(found_item)
                print_slow(f"You dropped {found_item.name}.")
                time.sleep(1)
        else:
            print_slow(f"You don't have a '{item_name}' in your inventory.")
            time.sleep(1)
    
    def enter_combat(self, enemy: NPC):
        """Enter combat with an enemy."""
        self.combat_system = CombatSystem(self.player, enemy)
        
        # Combat loop
        while self.running and enemy.health > 0 and self.player.health > 0:
            # Draw combat UI
            self.ui_system.draw_combat_ui(self.player, enemy)
            
            # Get player action
            print(DIVIDER)
            print("Your turn! Choose an action:")
            print("1. Attack")
            print("2. Special Move")
            print("3. Change Stance")
            print("4. Use Item")
            print("5. Flee")
            print(DIVIDER)
            
            choice = input("> ").strip()
            
            if choice == "1":
                # Attack
                messages = self.combat_system.process_turn("attack")
                for message in messages:
                    print_slow(message)
                    time.sleep(0.5)
                
                if enemy.health <= 0:
                    self.handle_enemy_defeat(enemy)
                    return
            
            elif choice == "2":
                # Special move
                print("Choose a special move:")
                print("1. Parry (Timing-based counter)")
                print("2. Charged Attack (High damage, high stamina cost)")
                print("3. Dodge (Avoid next attack)")
                print("4. Back")
                
                special_choice = input("> ").strip()
                
                if special_choice == "1":
                    messages = self.combat_system.process_turn("special", "parry")
                elif special_choice == "2":
                    messages = self.combat_system.process_turn("special", "charge")
                elif special_choice == "3":
                    messages = self.combat_system.process_turn("special", "dodge")
                else:
                    continue
                
                for message in messages:
                    print_slow(message)
                    time.sleep(0.5)
                
                if enemy.health <= 0:
                    self.handle_enemy_defeat(enemy)
                    return
            
            elif choice == "3":
                # Change stance
                print("Choose a stance:")
                print("1. Neutral (Balanced)")
                print("2. Aggressive (More damage, less defense)")
                print("3. Defensive (More defense, less damage)")
                print("4. Back")
                
                stance_choice = input("> ").strip()
                
                if stance_choice == "1":
                    messages = self.combat_system.process_turn("stance", "neutral")
                elif stance_choice == "2":
                    messages = self.combat_system.process_turn("stance", "aggressive")
                elif stance_choice == "3":
                    messages = self.combat_system.process_turn("stance", "defensive")
                else:
                    continue
                
                for message in messages:
                    print_slow(message)
                    time.sleep(0.5)
            
            elif choice == "4":
                # Use item
                usable_items = [item for item in self.player.inventory.items if item.usable]
                
                if not usable_items:
                    print_slow("You don't have any usable items.")
                    time.sleep(1)
                    continue
                
                print("Choose an item to use:")
                for i, item in enumerate(usable_items, 1):
                    print(f"{i}. {item.name}")
                print(f"{len(usable_items) + 1}. Back")
                
                item_choice = input("> ").strip()
                
                try:
                    item_idx = int(item_choice) - 1
                    if 0 <= item_idx < len(usable_items):
                        item = usable_items[item_idx]
                        messages = self.combat_system.process_turn("item", item)
                        
                        for message in messages:
                            print_slow(message)
                            time.sleep(0.5)
                except (ValueError, IndexError):
                    continue
            
            elif choice == "5":
                # Flee
                messages = self.combat_system.process_turn("flee")
                for message in messages:
                    print_slow(message)
                    time.sleep(0.5)
                
                # Check if flee was successful
                if "successfully flee" in messages[-1]:
                    return
            
            input("Press Enter to continue...")
    
    def handle_enemy_defeat(self, enemy: NPC):
        """Handle enemy defeat, looting, and quest updates."""
        print_slow(f"You have defeated {enemy.name}!")
        
        # Get loot
        items, essence = enemy.get_loot(self.world)
        
        # Award essence
        self.player.essence += essence
        print_slow(f"You gained {essence} essence.")
        
        # Award items
        if items:
            print_slow("You obtained:")
            for item in items:
                if self.player.inventory.add_item(item):
                    print_slow(f"- {item.name}")
                else:
                    print_slow(f"- Couldn't take {item.name} (inventory full)")
                    self.player.current_location.items.append(item)
        
        # Award experience
        exp_gain = enemy.health // 2
        leveled = self.player.gain_experience(exp_gain)
        print_slow(f"You gained {exp_gain} experience.")
        if leveled:
            print_slow(f"You've reached level {self.player.level}!")
        
        # Update quest progress
        self.quest_system.update_quest_progress(
            self.player, self.world, "kill", enemy.id)
        
        # Remove defeated enemy from active enemies
        self.player.current_location.active_enemies.remove(enemy)
        
        input("Press Enter to continue...")

# Run the game if executed directly
if __name__ == "__main__":
    game = GameEngine()
    game.start() 