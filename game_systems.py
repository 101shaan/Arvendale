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
        # Initialize player's combat log if it's empty
        if not hasattr(player, 'combat_log') or player.combat_log is None:
            player.combat_log = []
    
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
            # Parry requires waiting for enemy attack and timing the counter
            print_slow("Prepare to parry! Watch carefully and press SPACE immediately after the enemy attacks...")
            
            # Enemy will attack at a random time between 1-5 seconds
            attack_delay = random.uniform(1.0, 5.0)
            time.sleep(attack_delay)
            
            print_slow(f"{self.enemy.name} attacks!", delay=0.01)  # Very quick message
            
            # Player has 0.5 seconds to parry
            result = input_with_timeout("", timeout=0.5)
            success = result.strip().lower() == " "
            
            if not self.player.use_stamina(15):
                return 0, "You don't have enough stamina to parry!"
            
            if success:
                # Successful parry deflects damage back to enemy
                damage = self.enemy.attack  # Use enemy's own attack value
                actual_damage, killed = self.enemy.take_damage(damage)
                
                return damage, f"Perfect parry! You deflect {self.enemy.name}'s attack back for {actual_damage} damage!"
            else:
                # Failed parry results in taking increased damage
                damage = int(self.enemy.attack * 1.5)  # 1.5x damage when parry fails
                self.player.take_damage(damage)
                
                return 0, f"You miss the parry timing and take {damage} increased damage!"
        
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
        successful_parry = False  # Flag to track successful parries
        
        # Process player action
        if player_action == "attack":
            damage, critical, message = self.player_attack()
            messages.append(message)
            
            if damage > 0:
                actual_damage, killed = self.enemy.take_damage(damage)
                messages.append(f"You deal {actual_damage} damage to {self.enemy.name}.")
                
                if killed:
                    messages.append(f"You have defeated {self.enemy.name}!")
                    self.player.combat_log.extend(messages)
                    return messages
        
        elif player_action == "special":
            if player_target in ["parry", "charge", "dodge"]:
                damage, message = self.special_move(player_target)
                messages.append(message)
                
                # Check if this was a successful parry
                if player_target == "parry" and damage > 0:
                    successful_parry = True
                
                if damage > 0:
                    actual_damage, killed = self.enemy.take_damage(damage)
                    # For parry, the damage is already reported in the message
                    if player_target != "parry":
                        messages.append(f"You deal {actual_damage} damage to {self.enemy.name}.")
                    
                    if killed:
                        messages.append(f"You have defeated {self.enemy.name}!")
                        self.player.combat_log.extend(messages)
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
                self.player.combat_log.extend(messages)
                return messages
            else:
                messages.append("You fail to escape!")
        
        # Enemy turn (only if not defeated and no successful parry)
        if self.enemy.health > 0 and not successful_parry:
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
                        self.player.combat_log.extend(messages)
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
                    self.player.combat_log.extend(messages)
        elif successful_parry:
            messages.append("Your perfect parry gives you another turn!")
        
        # Update player buffs
        self.player.update_buffs()
        
        # Add messages to player's combat log 
        self.player.combat_log.extend(messages)
        
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
        """Draw the world map UI with ASCII art visualization."""
        clear_screen()
        print(DIVIDER)
        print_centered("WORLD MAP")
        print(DIVIDER)
        
        # Display compass and region information
        current_region = player.current_location.region if player.current_location else None
        
        # Display compass
        print("         N         ")
        print("         ↑         ")
        print("     NW  |  NE     ")
        print("       \\ | /       ")
        print("    W ←--+--→ E    ")
        print("       / | \\       ")
        print("     SW  |  SE     ")
        print("         ↓         ")
        print("         S         ")
        print()
                
        print(f"Current Location: {player.current_location.name if player.current_location else 'Unknown'}")
        print(f"Region: {current_region if current_region else 'Unknown'}")
        
        # Show available exits from current location
        if player.current_location and player.current_location.connections:
            exits = []
            for direction, location_id in player.current_location.connections.items():
                destination = world.get_location_by_id(location_id)
                exits.append(f"{direction.upper()}: {destination.name if destination else 'Unknown'}")
            
            print("\nExits: " + ", ".join(exits))
        print()
        
        # Get all regions for the world map
        all_regions = list(world.regions.keys()) if hasattr(world, 'regions') else []
        
        # Create a world map visualization
        if all_regions:
            # Map symbols - use emojis where appropriate
            symbols = {
                'player': '★',             # Current player position
                'beacon_unlocked': '🔥',   # Unlocked beacon (can rest)
                'beacon_protected': '🛡️',   # Protected beacon (needs clearing)
                'npc_friendly': '👤',      # Friendly NPC
                'npc_hostile': '💀',       # Hostile NPC/enemy
                'discovered': '■',         # Discovered location
                'unexplored': '□',         # Unexplored but known location
                'hidden': '░',             # Hidden/locked area  
                'boss': '👑',              # Boss area
                'shop': '💰',              # Shop/merchant area
                'quest': '❗',             # Quest area
                'path': '───',             # Path between locations (horizontal)
                'path_vertical': '│',      # Path between locations (vertical)
                'path_corner_tl': '┌',     # Path corner (top-left)
                'path_corner_tr': '┐',     # Path corner (top-right)
                'path_corner_bl': '└',     # Path corner (bottom-left)
                'path_corner_br': '┘',     # Path corner (bottom-right)
                'path_t_down': '┬',        # T-junction (down)
                'path_t_up': '┴',          # T-junction (up)
                'path_t_right': '├',       # T-junction (right)
                'path_t_left': '┤',        # T-junction (left)
                'path_cross': '┼',         # Crossroads
                'locked': '🔒',            # Locked location
                'danger': '⚠️',            # Dangerous area
                'item': '📦',              # Item location
                'water': '~~~',            # Water/river
                'bridge': '═╬═',           # Bridge
                'fog': '░░░',              # Fog of war/unexplored territory
                'viewpoint': '👁️',         # Viewpoint/lookout
                'portal': '⭕',            # Portal/teleporter
                'cave': '◓',               # Cave entrance
                'ruins': '𐄳',              # Ancient ruins
                'castle': '🏰',            # Castle
                'current_region': '*',     # Current region indicator
                'last_beacon': '🏠',       # Last rested beacon (home)
            }
            
            # Fallback symbols for terminals that may not support full Unicode
            fallback_symbols = {
                'player': '*',
                'beacon_unlocked': 'B',
                'beacon_protected': 'P',
                'npc_friendly': 'N',
                'npc_hostile': 'E',
                'discovered': '#',
                'unexplored': 'O',
                'hidden': '.',
                'boss': '!',
                'shop': '$',
                'quest': '?',
                'path': '---',
                'path_vertical': '|',
                'path_corner_tl': '+',
                'path_corner_tr': '+',
                'path_corner_bl': '+',
                'path_corner_br': '+',
                'path_t_down': '+',
                'path_t_up': '+',
                'path_t_right': '+',
                'path_t_left': '+',
                'path_cross': '+',
                'locked': 'L',
                'danger': '!',
                'item': 'I',
                'water': '~~~',
                'bridge': '=+=',
                'fog': '...',
                'viewpoint': 'V',
                'portal': 'O',
                'cave': 'C',
                'ruins': 'R',
                'castle': 'K',
                'current_region': '*',
                'last_beacon': 'H',
            }
            
            # Check if world has predefined ASCII maps, otherwise dynamically generate them
            has_region_maps = hasattr(world, 'region_maps') and world.region_maps
            
            # Display world map or region-specific map based on what the player has discovered
            if current_region:
                print("═══════════ REGION MAP ═══════════")
                
                # Check if this region has a predefined ASCII map
                if has_region_maps and current_region in world.region_maps:
                    region_map = world.region_maps[current_region]
                    
                    # Process the map to highlight current location and show/hide unexplored areas
                    processed_map = []
                    for line in region_map.split('\n'):
                        # Highlight player's current location
                        for location in player.discovered_locations:
                            if location.region == current_region:
                                if location == player.current_location and location.name in line:
                                    line = line.replace('□', symbols['player'])
                                elif location.is_beacon and location.name in line:
                                    # Use different beacon symbols based on status
                                    if hasattr(location, 'beacon_status'):
                                        if location.beacon_status == "unlocked":
                                            # Distinguish last rested beacon
                                            if player.last_beacon == location:
                                                line = line.replace('□', symbols['last_beacon'])
                                            else:
                                                line = line.replace('□', symbols['beacon_unlocked'])
                                        elif location.beacon_status == "protected":
                                            line = line.replace('□', symbols['beacon_protected'])
                                        else:
                                            # Default beacon (should be protected but just in case)
                                            line = line.replace('□', symbols['beacon_protected'])
                                    else:
                                        # Legacy beacon handling (should be protected)
                                        line = line.replace('□', symbols['beacon_protected'])
                                elif location.is_boss_area and location.name in line:
                                    line = line.replace('□', symbols['boss'])
                                elif location.is_shop and location.name in line:
                                    line = line.replace('□', symbols['shop'])
                                elif "castle" in location.name.lower() and location.name in line:
                                    line = line.replace('□', symbols['castle'])
                                elif "cave" in location.name.lower() and location.name in line:
                                    line = line.replace('□', symbols['cave'])
                                
                                # Add NPC indicators
                                if location.npcs and location.name in line:
                                    has_quest_giver = False
                                    has_merchant = False
                                    for npc_id in location.npcs:
                                        npc = world.get_npc_by_id(npc_id)
                                        if npc and npc.quest_giver:
                                            has_quest_giver = True
                                        if npc and npc.merchant:
                                            has_merchant = True
                                    
                                    if has_quest_giver and '□' in line:
                                        line = line.replace('□', symbols['quest'])
                                    elif has_merchant and '□' in line:
                                        line = line.replace('□', symbols['shop'])
                                    elif '□' in line:
                                        line = line.replace('□', symbols['npc_friendly'])
                                
                                # Show if location has items
                                if location.items and location.name in line and '□' in line:
                                    line = line.replace('□', symbols['item'])
                        
                        processed_map.append(line)
                    
                    # Print the map with consistent alignment
                    for line in processed_map:
                        if line.strip():  # Only print non-empty lines
                            # Handle emoji width by padding spaces appropriately
                            print(line)
                else:
                    # Generate a simple grid map for the region
                    UISystem._generate_region_grid_map(world, current_region, player, symbols, fallback_symbols)
            
            # Now show the overall world map with all regions
            print("\n═══════════ WORLD MAP ═══════════")
            
            # If a custom full world map exists, use it
            if has_region_maps and 'world' in world.region_maps:
                world_map = world.region_maps['world']
                # Process to highlight current region and show/hide unexplored regions
                processed_map = []
                for line in world_map.split('\n'):
                    # Highlight player's current region
                    if current_region and current_region.upper() in line:
                        line = line + " " + symbols['current_region']
                    
                    # Replace generic location symbols with appropriate icons
                    for location in player.discovered_locations:
                        if location.name in line:
                            if location == player.current_location and '□' in line:
                                line = line.replace('□', symbols['player'])
                            elif location.is_beacon and '□' in line:
                                if hasattr(location, 'beacon_status') and location.beacon_status == "unlocked":
                                    # Show last rested beacon differently
                                    if player.last_beacon == location:
                                        line = line.replace('□', symbols['last_beacon'])
                                    else:
                                        line = line.replace('□', symbols['beacon_unlocked'])
                                else:
                                    line = line.replace('□', symbols['beacon_protected'])
                            elif location.is_boss_area and '□' in line:
                                line = line.replace('□', symbols['boss'])
                            elif location.is_shop and '□' in line:
                                line = line.replace('□', symbols['shop'])
                    
                    # Check for connections to unexplored areas
                    if player.current_location:
                        for dir, loc_id in player.current_location.connections.items():
                            dest = world.get_location_by_id(loc_id)
                            if dest and dest.name in line and dest not in player.discovered_locations:
                                line = line.replace('□', symbols['unexplored'])
                    
                    processed_map.append(line)
                
                # Print the map with consistent alignment
                for line in processed_map:
                    if line.strip():  # Only print non-empty lines
                        print(line)
            else:
                # Generate a simple overview map showing all regions
                UISystem._generate_world_overview_map(world, player, all_regions, symbols, fallback_symbols)
        
        # Map legend - expanded with new symbols
        print("\n═══════════ MAP LEGEND ═══════════")
        print(f"{symbols['player']} : Your Location      {symbols['beacon_unlocked']} : Unlocked Beacon")
        print(f"{symbols['beacon_protected']} : Protected Beacon   {symbols['last_beacon']} : Last Rested Beacon")
        print(f"{symbols['npc_friendly']} : Friendly NPC      {symbols['npc_hostile']} : Enemy/Hostile NPC")
        print(f"{symbols['discovered']} : Discovered Area    {symbols['unexplored']} : Known but Unexplored")
        print(f"{symbols['hidden']} : Hidden/Locked Area  {symbols['boss']} : Boss Area")
        print(f"{symbols['shop']} : Shop/Merchant       {symbols['quest']} : Quest Available")
        print(f"{symbols['item']} : Items Available     {symbols['locked']} : Requires Key/Item")
        print(f"{symbols['danger']} : Dangerous Area      {symbols['castle']} : Castle/Fortress")
        print(f"{symbols['cave']} : Cave/Dungeon        {symbols['ruins']} : Ruins/Ancient Site")
        
        # Display discovered locations list by region for reference
        print("\n═══════════ DISCOVERED LOCATIONS ═══════════")
        
        regions_with_discoveries = {}
        for location in player.discovered_locations:
            region = location.region if location else "Unknown"
            if region not in regions_with_discoveries:
                regions_with_discoveries[region] = []
            regions_with_discoveries[region].append(location)
        
        for region, locations in sorted(regions_with_discoveries.items()):
            print(f"\n{region}:")
            for location in locations:
                # Mark current location with a star
                current_marker = symbols['player'] + " " if location == player.current_location else "  "
                
                # Build a detailed location entry
                location_details = []
                
                # Add location type markers
                if location.is_beacon:
                    if hasattr(location, 'beacon_status') and location.beacon_status == "unlocked":
                        if player.last_beacon == location:
                            location_details.append(f"[{symbols['last_beacon']} Home Beacon]")
                        else:
                            location_details.append(f"[{symbols['beacon_unlocked']} Unlocked Beacon]")
                    else:
                        location_details.append(f"[{symbols['beacon_protected']} Protected Beacon]")
                if location.is_shop:
                    location_details.append(f"[{symbols['shop']} Shop]")
                if location.is_boss_area:
                    location_details.append(f"[{symbols['boss']} Boss]")
                
                # Add NPC information
                npc_info = []
                hostile_count = 0
                friendly_count = 0
                quest_available = False
                
                for npc_id in location.npcs:
                    npc = world.get_npc_by_id(npc_id)
                    if npc:
                        if npc.friendly:
                            friendly_count += 1
                            if npc.quest_giver:
                                quest_available = True
                        else:
                            hostile_count += 1
                
                if friendly_count > 0:
                    npc_info.append(f"{symbols['npc_friendly']}: {friendly_count}")
                if hostile_count > 0:
                    npc_info.append(f"{symbols['npc_hostile']}: {hostile_count}")
                if quest_available:
                    npc_info.append(f"{symbols['quest']}")
                
                if npc_info:
                    location_details.append(f"[NPCs: {', '.join(npc_info)}]")
                
                # Add item information
                if location.items:
                    location_details.append(f"[{symbols['item']} Items: {len(location.items)}]")
                
                # Add exit directions
                if location.connections:
                    exits = ', '.join(direction.upper() for direction in location.connections.keys())
                    location_details.append(f"[Exits: {exits}]")
                
                # Build the full location entry
                location_entry = f"{current_marker}{location.name}"
                if location_details:
                    location_entry += " " + " ".join(location_details)
                
                print(location_entry)
    
    @staticmethod
    def _generate_region_grid_map(world, region_name, player, symbols, fallback_symbols):
        """Generate a grid-based ASCII map for a specific region."""
        # Get all locations in this region
        region_locations = world.regions.get(region_name, [])
        if not region_locations:
            print("[No map data available for this region]")
            return
        
        # Create a simple grid representation
        # For simplicity, we'll create a 10x10 grid
        grid_size = 10
        grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Place locations on the grid - this is simplified
        # In a real implementation, you'd want to use the actual spatial relationships
        for i, location in enumerate(region_locations):
            row = i // grid_size
            col = i % grid_size
            
            if row < grid_size and col < grid_size:
                # Choose symbol based on location type and discovery status
                symbol = symbols['hidden']  # Default to hidden
                
                if location in player.discovered_locations:
                    if location == player.current_location:
                        symbol = symbols['player']
                    elif location.is_beacon:
                        symbol = symbols['beacon_unlocked']
                    elif location.is_boss_area:
                        symbol = symbols['boss']
                    elif location.is_shop:
                        symbol = symbols['shop']
                    elif location.npcs:
                        has_quest_giver = any(world.get_npc_by_id(npc_id) and 
                                              world.get_npc_by_id(npc_id).quest_giver 
                                              for npc_id in location.npcs)
                        if has_quest_giver:
                            symbol = symbols['quest']
                        else:
                            symbol = symbols['npc_friendly']
                    else:
                        symbol = symbols['discovered']
                else:
                    # Check if it's a known but unexplored location
                    is_connected_to_discovered = False
                    for discovered_loc in player.discovered_locations:
                        if location.id in discovered_loc.connections.values():
                            is_connected_to_discovered = True
                            break
                    
                    if is_connected_to_discovered:
                        symbol = symbols['unexplored']
                    else:
                        symbol = ' '  # Completely hidden
                
                grid[row][col] = symbol
        
        # Draw paths between connected locations - simplified for the grid layout
        for location in region_locations:
            if location in player.discovered_locations:
                for direction, connected_loc_id in location.connections.items():
                    connected_loc = world.get_location_by_id(connected_loc_id)
                    if connected_loc in region_locations and connected_loc in player.discovered_locations:
                        # Find grid positions - this is simplified
                        loc_idx = region_locations.index(location)
                        loc_row, loc_col = loc_idx // grid_size, loc_idx % grid_size
                        
                        conn_idx = region_locations.index(connected_loc)
                        conn_row, conn_col = conn_idx // grid_size, conn_idx % grid_size
                        
                        # Draw path if within grid bounds
                        if (loc_row < grid_size and loc_col < grid_size and 
                            conn_row < grid_size and conn_col < grid_size):
                            # Simplified path drawing - just mark middle cells with path symbol
                            if loc_row == conn_row:  # Same row, horizontal path
                                for c in range(min(loc_col, conn_col) + 1, max(loc_col, conn_col)):
                                    if grid[loc_row][c] == ' ':
                                        grid[loc_row][c] = symbols['path']
                            elif loc_col == conn_col:  # Same column, vertical path
                                for r in range(min(loc_row, conn_row) + 1, max(loc_row, conn_row)):
                                    if grid[r][loc_col] == ' ':
                                        grid[r][loc_col] = symbols['path_vertical']
        
        # Print the grid
        for row in grid:
            print(''.join(cell.ljust(3) for cell in row))
    
    @staticmethod
    def _generate_world_overview_map(world, player, regions, symbols, fallback_symbols):
        """Generate an overview map of the world showing all regions."""
        if not regions:
            print("[No world map data available]")
            return
        
        # Create a simple representation of regions
        # For simplicity, we'll arrange regions in a circular pattern
        num_regions = len(regions)
        
        # Center text for the map
        center_text = "ARDENVALE"
        
        # Define a circular arrangement
        radius = 10
        center_x, center_y = radius + 5, radius
        
        # Create a grid for the world map
        grid_width = (radius + 5) * 2
        grid_height = radius * 2 + 1
        grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]
        
        # Place the center text
        center_start = center_x - len(center_text) // 2
        for i, char in enumerate(center_text):
            if 0 <= center_start + i < grid_width:
                grid[center_y][center_start + i] = char
        
        # Place regions in a circular arrangement
        for i, region in enumerate(regions):
            angle = 2 * 3.14159 * i / num_regions
            x = int(center_x + radius * 0.8 * 2 * (i % 2) * (0.5 - (i // 2) % 2))
            y = int(center_y + radius * 0.8 * ((i+1) % 2) * (1 - 2 * ((i // 3) % 2)))
            
            # Ensure coordinates are within grid bounds
            x = max(0, min(x, grid_width - 1))
            y = max(0, min(y, grid_height - 1))
            
            # Mark the region on the grid
            region_char = symbols['hidden']
            if region in world.regions:
                # Check if any location in this region is discovered
                region_locations = world.regions[region]
                any_discovered = any(loc in player.discovered_locations for loc in region_locations)
                
                if any_discovered:
                    if region == player.current_location.region:
                        region_char = symbols['player']  # Current region
                    else:
                        region_char = symbols['discovered']  # Discovered region
                else:
                    # Check if any location is connected to a discovered location
                    is_connected = False
                    for loc in region_locations:
                        for discovered_loc in player.discovered_locations:
                            if loc.id in discovered_loc.connections.values():
                                is_connected = True
                                break
                        if is_connected:
                            break
                    
                    if is_connected:
                        region_char = symbols['unexplored']  # Known but unexplored
            
            grid[y][x] = region_char
            
            # Add region name if discovered
            if region_char in [symbols['player'], symbols['discovered'], symbols['unexplored']]:
                name_start = x - len(region) // 2
                for j, char in enumerate(region):
                    name_x = name_start + j
                    if 0 <= name_x < grid_width and y+1 < grid_height:
                        grid[y+1][name_x] = char
        
        # Draw connections between regions - simplified
        for region in regions:
            if region in world.regions and any(loc in player.discovered_locations for loc in world.regions[region]):
                # Find connected regions through locations
                connected_regions = set()
                for loc in world.regions[region]:
                    if loc in player.discovered_locations:
                        for _, connected_loc_id in loc.connections.items():
                            connected_loc = world.get_location_by_id(connected_loc_id)
                            if connected_loc and connected_loc.region != region:
                                connected_regions.add(connected_loc.region)
                
                # Draw paths to connected regions if they're discovered
                for connected_region in connected_regions:
                    if connected_region in regions and any(loc in player.discovered_locations for loc in world.regions[connected_region]):
                        # Find grid positions
                        region_idx = regions.index(region)
                        conn_idx = regions.index(connected_region)
                        
                        region_angle = 2 * 3.14159 * region_idx / num_regions
                        conn_angle = 2 * 3.14159 * conn_idx / num_regions
                        
                        region_x = int(center_x + radius * 0.8 * 2 * (region_idx % 2) * (0.5 - (region_idx // 2) % 2))
                        region_y = int(center_y + radius * 0.8 * ((region_idx+1) % 2) * (1 - 2 * ((region_idx // 3) % 2)))
                        
                        conn_x = int(center_x + radius * 0.8 * 2 * (conn_idx % 2) * (0.5 - (conn_idx // 2) % 2))
                        conn_y = int(center_y + radius * 0.8 * ((conn_idx+1) % 2) * (1 - 2 * ((conn_idx // 3) % 2)))
                        
                        # Ensure coordinates are within grid bounds
                        region_x = max(0, min(region_x, grid_width - 1))
                        region_y = max(0, min(region_y, grid_height - 1))
                        conn_x = max(0, min(conn_x, grid_width - 1))
                        conn_y = max(0, min(conn_y, grid_height - 1))
                        
                        # Simple path - just draw a line character halfway between
                        mid_x = (region_x + conn_x) // 2
                        mid_y = (region_y + conn_y) // 2
                        
                        if 0 <= mid_x < grid_width and 0 <= mid_y < grid_height:
                            if mid_x == region_x or mid_x == conn_x:  # Vertical path
                                grid[mid_y][mid_x] = symbols['path_vertical']
                            else:  # Horizontal or diagonal path
                                grid[mid_y][mid_x] = symbols['path'][0]
        
        # Print the grid
        for row in grid:
            print(''.join(cell for cell in row))
    
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