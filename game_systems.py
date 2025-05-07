import random
import time
from typing import Dict, List, Tuple, Any, Optional
import os

from config import DIVIDER
from utils import print_slow, display_bar, display_countdown, input_with_timeout, clear_screen, print_centered

class CombatSystem:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.player_stance = "neutral"  # neutral, aggressive, defensive
        self.enemy_stance = "neutral"
        self.combo_counter = 0
        self.last_attack_time = 0
        self.combat_log = []
    
    def player_attack(self) -> Tuple[int, bool, str]:
        """Handle player attack and return damage, critical flag, and message."""
        damage = self.player.get_attack_damage()
        
        # Check if player has enough stamina
        weapon_stamina_cost = 10
        if self.player.inventory and self.player.inventory.equipped["weapon"]:
            weapon_stamina_cost = self.player.inventory.equipped["weapon"].stamina_cost
        
        if not self.player.use_stamina(weapon_stamina_cost):
            return 0, False, "You're too exhausted to attack!"
        
        # Apply stance modifiers
        if self.player_stance == "aggressive":
            damage = int(damage * 1.3)
        elif self.player_stance == "defensive":
            damage = int(damage * 0.7)
        
        # Check for critical hit (based on dexterity)
        crit_chance = 0.05 + (self.player.dexterity / 200)  # 5% base + up to 15% from dexterity
        critical = random.random() < crit_chance
        
        if critical:
            damage = int(damage * 1.5)
        
        # Apply combo bonus (consecutive hits)
        if time.time() - self.last_attack_time < 2.0:  # 2 second window for combos
            self.combo_counter += 1
            if self.combo_counter >= 3:
                damage = int(damage * (1 + (self.combo_counter * 0.1)))  # 10% per combo hit
        else:
            self.combo_counter = 0
        
        self.last_attack_time = time.time()
        
        # Apply random variance (±10%)
        variance = random.uniform(0.9, 1.1)
        damage = int(damage * variance)
        
        # Create message
        weapon_name = "fists"
        if self.player.inventory and self.player.inventory.equipped["weapon"]:
            weapon_name = self.player.inventory.equipped["weapon"].name
        
        if critical:
            message = f"You land a critical hit with your {weapon_name} for {damage} damage!"
        else:
            message = f"You attack with your {weapon_name} for {damage} damage."
        
        # Add combo text
        if self.combo_counter >= 3:
            message += f" Combo x{self.combo_counter}!"
        
        return damage, critical, message
    
    def enemy_attack(self) -> Tuple[int, bool, str]:
        """Handle enemy attack."""
        return self.enemy.attack_player(self.player)
    
    def change_stance(self, stance: str) -> str:
        """Change player's combat stance."""
        previous = self.player_stance
        self.player_stance = stance
        
        effects = {
            "neutral": "balanced attack and defense",
            "aggressive": "increased damage but lower defense",
            "defensive": "increased defense but lower damage"
        }
        
        return f"You switch from {previous} to {stance} stance: {effects[stance]}."
    
    def special_move(self, move_type: str) -> Tuple[int, str]:
        """Execute a special combat move."""
        if move_type == "parry":
            # Parry requires a quick-time event
            print_slow("Prepare to parry! Press SPACE when the enemy attacks...")
            result = input_with_timeout("", timeout=1.5)
            
            success = result.strip().lower() == " "
            if success:
                # Successful parry stuns enemy and allows counter
                damage = int(self.player.get_attack_damage() * 1.5)
                self.player.use_stamina(15)
                return damage, "Perfect parry! You counter-attack for heavy damage!"
            else:
                # Failed parry results in taking damage
                damage = int(self.enemy.attack * 0.5)
                self.player.take_damage(damage)
                return 0, f"You miss the parry timing and take {damage} damage!"
        
        elif move_type == "charge":
            # Charged attack: high damage but leaves you vulnerable
            if not self.player.use_stamina(25):
                return 0, "You don't have enough stamina for a charged attack!"
            
            damage = int(self.player.get_attack_damage() * 2)
            return damage, f"You charge your attack and deal {damage} massive damage!"
        
        elif move_type == "dodge":
            # Dodge: avoid next attack if successful
            if not self.player.use_stamina(15):
                return 0, "You don't have enough stamina to dodge!"
            
            # Dodge success based on dexterity
            dodge_chance = 0.5 + (self.player.dexterity / 100)  # 50% base + up to 30% from dexterity
            success = random.random() < dodge_chance
            
            if success:
                return 0, "You successfully dodge the enemy's attack!"
            else:
                return 0, "You attempt to dodge but the enemy anticipates your movement."
        
        return 0, "Invalid special move."
    
    def process_turn(self, player_action: str, player_target: Any = None) -> List[str]:
        """Process a full combat turn and return messages."""
        messages = []
        
        # Process player action
        if player_action == "attack":
            damage, critical, message = self.player_attack()
            messages.append(message)
            
            if damage > 0:
                actual_damage, killed = self.enemy.take_damage(damage)
                messages.append(f"You deal {actual_damage} damage to {self.enemy.name}.")
                
                if killed:
                    messages.append(f"You have defeated {self.enemy.name}!")
                    return messages
        
        elif player_action == "special":
            if player_target in ["parry", "charge", "dodge"]:
                damage, message = self.special_move(player_target)
                messages.append(message)
                
                if damage > 0:
                    actual_damage, killed = self.enemy.take_damage(damage)
                    messages.append(f"You deal {actual_damage} damage to {self.enemy.name}.")
                    
                    if killed:
                        messages.append(f"You have defeated {self.enemy.name}!")
                        return messages
        
        elif player_action == "stance":
            message = self.change_stance(player_target)
            messages.append(message)
        
        elif player_action == "item":
            # Use an item in combat
            item = player_target
            result = item.use(self.player)
            messages.append(result)
        
        elif player_action == "flee":
            # Attempt to flee based on dexterity
            flee_chance = 0.4 + (self.player.dexterity / 100)  # 40% base + up to 30% from dexterity
            success = random.random() < flee_chance
            
            if success:
                messages.append("You successfully flee from combat!")
                return messages
            else:
                messages.append("You fail to escape!")
        
        # Enemy turn (only if not defeated)
        if self.enemy.health > 0:
            # 70% chance for a normal attack, 30% for special ability if available
            if self.enemy.special_abilities and random.random() < 0.3:
                # Use a random special ability
                ability = random.choice(self.enemy.special_abilities)
                
                if ability["type"] == "aoe_attack":
                    damage = ability["damage"]
                    player_died = self.player.take_damage(damage)
                    messages.append(f"{self.enemy.name} uses {ability['name']} for {damage} damage!")
                    
                    if player_died:
                        messages.append("You have been defeated...")
                        return messages
                
                elif ability["type"] == "heal":
                    heal_amount = ability["amount"]
                    self.enemy.health = min(self.enemy.health + heal_amount, self.enemy.max_health)
                    messages.append(f"{self.enemy.name} uses {ability['name']} and recovers {heal_amount} health.")
                
                elif ability["type"] == "status":
                    self.player.apply_buff(ability["effect"], ability["potency"], ability["duration"])
                    messages.append(f"{self.enemy.name} uses {ability['name']} and afflicts you with {ability['effect']}!")
            
            else:
                # Normal attack
                damage, critical, message = self.enemy_attack()
                messages.append(message)
                
                player_died = self.player.take_damage(damage)
                if player_died:
                    messages.append("You have been defeated...")
        
        # Update player buffs
        self.player.update_buffs()
        
        # Regenerate some stamina each turn
        stamina_regen = 5 + (self.player.dexterity // 5)
        self.player.restore_stamina(stamina_regen)
        
        return messages

class UISystem:
    @staticmethod
    def draw_combat_ui(player, enemy):
        """Draw the combat interface."""
        clear_screen()
        print(DIVIDER)
        print_centered(f"COMBAT: {player.name} vs {enemy.name}")
        print(DIVIDER)
        
        # Health and stamina bars
        print(f"{player.name}'s Health: {display_bar(player.health, player.max_health, 20)}")
        print(f"{player.name}'s Stamina: {display_bar(player.stamina, player.max_stamina, 20)}")
        print()
        print(f"{enemy.name}'s Health: {display_bar(enemy.health, enemy.max_health, 20)}")
        print()
        
        # Combat log (last 5 messages)
        print("Combat Log:")
        for message in player.combat_log[-5:]:
            print(f"- {message}")
        print()
        
        # Available actions
        print("Actions:")
        print("1. Attack - Basic attack with equipped weapon")
        print("2. Special - Special moves (parry, charge, dodge)")
        print("3. Stance - Change combat stance (neutral, aggressive, defensive)")
        print("4. Item - Use a consumable item")
        print("5. Flee - Attempt to escape combat")
    
    @staticmethod
    def draw_character_ui(player):
        """Draw the character status screen."""
        clear_screen()
        print(DIVIDER)
        print_centered("CHARACTER STATUS")
        print(DIVIDER)
        
        # Character stats
        print(f"Name: {player.name}")
        print(f"Level: {player.level}")
        print(f"Experience: {player.experience}/{player.experience_required}")
        print()
        print(f"Health: {player.health}/{player.max_health}")
        print(f"Stamina: {player.stamina}/{player.max_stamina}")
        print()
        print(f"Strength: {player.strength}")
        print(f"Dexterity: {player.dexterity}")
        print(f"Intelligence: {player.intelligence}")
        print()
        print(f"Essence: {player.essence}")
        
        # Equipment
        print("\nEquipped Items:")
        if player.inventory:
            for slot, item in player.inventory.equipped.items():
                if item:
                    print(f"{slot.capitalize()}: {item.name}")
                else:
                    print(f"{slot.capitalize()}: None")
        
        # Active buffs
        if player.buffs:
            print("\nActive Effects:")
            for buff in player.buffs:
                duration = "Permanent" if buff["permanent"] else f"{buff['duration']} turns"
                print(f"{buff['type'].capitalize()}: {buff['amount']} ({duration})")
    
    @staticmethod
    def draw_inventory_ui(player):
        """Draw the inventory screen."""
        clear_screen()
        print(DIVIDER)
        print_centered("INVENTORY")
        print(DIVIDER)
        
        if not player.inventory or not player.inventory.items:
            print("Your inventory is empty.")
            return
        
        # Group items by type
        items_by_type = {
            "weapon": [],
            "armor": [],
            "consumable": [],
            "key": [],
            "material": [],
            "misc": []
        }
        
        for item in player.inventory.items:
            item_type = item.item_type
            if item_type not in items_by_type:
                item_type = "misc"
            items_by_type[item_type].append(item)
        
        # Display items by type
        for category, items in items_by_type.items():
            if items:
                print(f"\n{category.upper()}:")
                for i, item in enumerate(items, 1):
                    equipped_text = "[Equipped]" if item.equipped else ""
                    quantity_text = f"x{item.quantity}" if item.quantity > 1 else ""
                    print(f"{i}. {item.name} {quantity_text} {equipped_text}")
                    print(f"   {item.description}")
                    
                    # Show additional stats based on item type
                    if category == "weapon":
                        print(f"   Damage: {item.damage}, Speed: {item.attack_speed}")
                    elif category == "armor":
                        print(f"   Defense: {item.defense}, Type: {item.armor_type}")
                    elif category == "consumable":
                        print(f"   Effect: {item.effect_type}, Value: {item.effect_value}")
    
    @staticmethod
    def draw_map_ui(player, world):
        """Draw the world map UI."""
        clear_screen()
        print(DIVIDER)
        print_centered("WORLD MAP")
        print(DIVIDER)
        
        # Display region information
        current_region = player.current_location.region if player.current_location else None
        
        print(f"Current Location: {player.current_location.name if player.current_location else 'Unknown'}")
        print(f"Region: {current_region if current_region else 'Unknown'}")
        print()
        
        # Show discovered locations by region
        print("Discovered Locations:")
        
        regions_with_discoveries = {}
        for location in player.discovered_locations:
            region = location.region if location else "Unknown"
            if region not in regions_with_discoveries:
                regions_with_discoveries[region] = []
            regions_with_discoveries[region].append(location)
        
        for region, locations in regions_with_discoveries.items():
            print(f"\n{region}:")
            for location in locations:
                current_marker = "* " if location == player.current_location else "  "
                beacon_marker = "[Beacon] " if location.is_beacon else ""
                print(f"{current_marker}{location.name} {beacon_marker}")
        
        # Display ASCII map if available for current region
        if current_region and hasattr(world, 'region_maps') and current_region in world.region_maps:
            print("\nRegion Map:")
            print(world.region_maps[current_region])
    
    @staticmethod
    def draw_location_ui(location):
        """Draw the current location UI."""
        clear_screen()
        
        # Display location ASCII art if available
        if location.ascii_art:
            print(location.ascii_art)
        
        print(DIVIDER)
        print_centered(location.name)
        print(DIVIDER)
        
        # Location description
        print(location.description)
        print()
        
        # Show NPCs at location
        if location.npcs:
            print("Characters:")
            for npc_id in location.npcs:
                print(f"- {npc_id.replace('_', ' ').title()}")
            print()
        
        # Show enemies if any
        if location.active_enemies:
            print("Enemies:")
            for enemy in location.active_enemies:
                print(f"- {enemy.name}")
            print()
        
        # Show items on ground
        if location.items:
            print("Items:")
            for item in location.items:
                print(f"- {item.name}")
            print()
        
        # Show available directions
        if location.connections:
            print("Exits:")
            for direction, _ in location.connections.items():
                print(f"- {direction.capitalize()}")
            print()
        
        # Show if location is a beacon
        if location.is_beacon:
            print("This location has a beacon where you can rest and recover.")
            print()
        
        # Show dropped essence if any
        if location.dropped_essence > 0:
            print(f"You see {location.dropped_essence} essence that you dropped earlier.")
            print()

class QuestSystem:
    @staticmethod
    def display_quest_log(player, world):
        """Display the player's active quests."""
        clear_screen()
        print(DIVIDER)
        print_centered("QUEST LOG")
        print(DIVIDER)
        
        if not player.quest_log:
            print("You don't have any active quests.")
            return
        
        for quest_id in player.quest_log:
            quest = world.get_quest_by_id(quest_id)
            if quest:
                print(quest.get_progress_text())
                print()
    
    @staticmethod
    def update_quest_progress(player, world, action_type: str, target: str, amount: int = 1):
        """Update quest progress based on player actions."""
        updated_quests = []
        
        for quest_id in player.quest_log:
            quest = world.get_quest_by_id(quest_id)
            if quest and not quest.completed:
                if quest.update_progress(action_type, target, amount):
                    updated_quests.append(quest)
                    
                    # Check if quest completed
                    if quest.completed:
                        print_slow(f"Quest completed: {quest.name}")
                        player.completed_quests.append(quest_id)
                        player.quest_log.remove(quest_id)
                        
                        # Apply rewards
                        if "essence" in quest.rewards:
                            player.essence += quest.rewards["essence"]
                            print(f"Received {quest.rewards['essence']} essence.")
                        
                        if "item" in quest.rewards:
                            item_id = quest.rewards["item"]
                            item = world.get_item_by_id(item_id)
                            if item and player.inventory:
                                player.inventory.add_item(item)
                                print(f"Received {item.name}.")
                        
                        if "experience" in quest.rewards:
                            leveled_up = player.gain_experience(quest.rewards["experience"])
                            print(f"Gained {quest.rewards['experience']} experience.")
                            if leveled_up:
                                print("You leveled up!")
                        
                        if "faction" in quest.rewards and "reputation" in quest.rewards:
                            faction = quest.rewards["faction"]
                            rep = quest.rewards["reputation"]
                            if "faction_rep" not in player.flags:
                                player.flags["faction_rep"] = {}
                            if faction not in player.flags["faction_rep"]:
                                player.flags["faction_rep"][faction] = 0
                            player.flags["faction_rep"][faction] += rep
                            print(f"Gained {rep} reputation with {faction}.")
        
        return updated_quests
    
    @staticmethod
    def get_available_quests(player, npc, world) -> List:
        """Get quests available from an NPC."""
        if not npc.quest_giver:
            return []
        
        available_quests = []
        for quest_id, quest in world.quests.items():
            # Check if quest is already active or completed
            if quest_id in player.quest_log or quest_id in player.completed_quests:
                continue
            
            # Check for quest giver matching
            if hasattr(quest, "quest_giver") and quest.quest_giver == npc.id:
                # Check prerequisites if any
                if hasattr(quest, "prerequisites"):
                    prereq_met = True
                    for prereq in quest.prerequisites:
                        if prereq["type"] == "quest_complete" and prereq["id"] not in player.completed_quests:
                            prereq_met = False
                        elif prereq["type"] == "player_flag" and player.flags.get(prereq["flag"]) != prereq["value"]:
                            prereq_met = False
                        elif prereq["type"] == "level" and player.level < prereq["level"]:
                            prereq_met = False
                    
                    if prereq_met:
                        available_quests.append(quest)
                else:
                    available_quests.append(quest)
        
        return available_quests 