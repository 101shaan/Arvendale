from typing import Dict, List, Optional, Tuple, Union, Any
import random
import time
from config import DIVIDER
from utils import print_slow, display_bar

class Player:
    def __init__(self, name: str, max_health: int = 100, max_stamina: int = 100,
                 strength: int = 10, dexterity: int = 10, intelligence: int = 10,
                 level: int = 1, experience: int = 0):
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.strength = strength
        self.dexterity = dexterity
        self.intelligence = intelligence
        self.level = level
        self.experience = experience
        self.experience_required = self._calculate_xp_required()
        self.essence = 0  # Currency
        self.inventory = None  # Set in game_data
        self.current_location = None
        self.previous_location = None
        self.quest_log = []
        self.completed_quests = []
        self.discovered_locations = []
        self.buffs = []  # List of active buffs/debuffs
        self.skills = []  # List of special abilities
        self.flags = {}  # Persistent flags for quest/story progress
        self.last_beacon = None  # Last rested beacon (checkpoint)
    
    def _calculate_xp_required(self) -> int:
        """Calculate XP required for next level."""
        return self.level * 100 + (self.level * self.level * 20)
    
    def gain_experience(self, amount: int) -> bool:
        """Gain experience and check for level up. Returns True if leveled up."""
        self.experience += amount
        if self.experience >= self.experience_required:
            self.level_up()
            return True
        return False
    
    def level_up(self):
        """Level up the player and increase stats."""
        self.level += 1
        
        # Increase stats
        self.max_health += 10
        self.health = self.max_health
        self.max_stamina += 5
        self.stamina = self.max_stamina
        
        # Reset experience and calculate new requirement
        self.experience -= self.experience_required
        self.experience_required = self._calculate_xp_required()
        
        print_slow(f"\nYou've reached level {self.level}!")
        print(f"Max Health: {self.max_health}")
        print(f"Max Stamina: {self.max_stamina}")
        print(f"Experience to next level: {self.experience_required}")
    
    def heal(self, amount: int):
        """Heal the player by the specified amount."""
        self.health = min(self.health + amount, self.max_health)
    
    def take_damage(self, amount: int) -> bool:
        """Take damage and return True if player dies."""
        # Apply armor defense
        if self.inventory and hasattr(self.inventory, "get_total_defense"):
            defense = self.inventory.get_total_defense()
            reduction = defense / (defense + 50)  # Defense formula
            amount = int(amount * (1 - reduction))
        
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True  # Player died
        return False
    
    def restore_stamina(self, amount: int):
        """Restore stamina by the specified amount."""
        self.stamina = min(self.stamina + amount, self.max_stamina)
    
    def use_stamina(self, amount: int) -> bool:
        """Use stamina and return True if successful."""
        if self.stamina < amount:
            return False
        self.stamina -= amount
        return True
    
    def rest(self):
        """Rest at a beacon to fully recover."""
        self.health = self.max_health
        self.stamina = self.max_stamina
        # Clear temporary debuffs
        self.buffs = [buff for buff in self.buffs if buff["permanent"]]
    
    def apply_buff(self, buff_type: str, amount: int, duration: int, permanent: bool = False):
        """Apply a buff or debuff to the player."""
        self.buffs.append({
            "type": buff_type,
            "amount": amount,
            "duration": duration,
            "permanent": permanent
        })
    
    def update_buffs(self):
        """Update buff durations and remove expired buffs."""
        active_buffs = []
        for buff in self.buffs:
            if buff["permanent"] or buff["duration"] > 0:
                if not buff["permanent"]:
                    buff["duration"] -= 1
                active_buffs.append(buff)
        self.buffs = active_buffs
    
    def get_attack_damage(self) -> int:
        """Calculate attack damage based on equipped weapon and strength."""
        base_damage = self.strength // 2
        
        # Add weapon damage if equipped
        if self.inventory and self.inventory.equipped["weapon"]:
            weapon = self.inventory.equipped["weapon"]
            base_damage += weapon.damage
        
        # Apply buffs
        for buff in self.buffs:
            if buff["type"] == "strength" or buff["type"] == "attack":
                base_damage += buff["amount"]
        
        return max(1, base_damage)
    
    def die(self):
        """Handle player death."""
        print_slow("You have died...")
        time.sleep(1.5)
        
        # Drop essence where player died
        if self.essence > 0:
            if self.current_location:
                self.current_location.dropped_essence = self.essence
                self.current_location.dropped_essence_time = time.time()
                print_slow(f"You dropped {self.essence} essence.")
                self.essence = 0
        
        # Respawn at last beacon
        if self.last_beacon:
            print_slow(f"You awaken at the last beacon you rested at...")
            self.current_location = self.last_beacon
            self.health = self.max_health // 2  # Respawn with half health
            self.stamina = self.max_stamina
            return True
        else:
            print_slow("With no beacon to return to, your journey ends here...")
            return False  # Game over
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for saving."""
        return {
            "name": self.name,
            "max_health": self.max_health,
            "health": self.health,
            "max_stamina": self.max_stamina,
            "stamina": self.stamina,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "level": self.level,
            "experience": self.experience,
            "experience_required": self.experience_required,
            "essence": self.essence,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "current_location": self.current_location.id if self.current_location else None,
            "previous_location": self.previous_location.id if self.previous_location else None,
            "quest_log": self.quest_log.copy(),
            "completed_quests": self.completed_quests.copy(),
            "discovered_locations": [loc.id for loc in self.discovered_locations],
            "buffs": self.buffs.copy(),
            "skills": self.skills.copy(),
            "flags": self.flags.copy(),
            "last_beacon": self.last_beacon.id if self.last_beacon else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create player from dictionary."""
        player = cls(
            name=data["name"],
            max_health=data["max_health"],
            max_stamina=data["max_stamina"],
            strength=data["strength"],
            dexterity=data["dexterity"],
            intelligence=data["intelligence"],
            level=data["level"],
            experience=data["experience"]
        )
        
        player.health = data["health"]
        player.stamina = data["stamina"]
        player.experience_required = data["experience_required"]
        player.essence = data["essence"]
        player.quest_log = data["quest_log"].copy()
        player.completed_quests = data["completed_quests"].copy()
        player.buffs = data["buffs"].copy()
        player.skills = data["skills"].copy()
        player.flags = data["flags"].copy()
        
        # These references need to be resolved after world is loaded
        player._current_location_id = data["current_location"]
        player._previous_location_id = data["previous_location"]
        player._discovered_locations_ids = data["discovered_locations"]
        player._last_beacon_id = data["last_beacon"]
        
        # Create inventory
        if data["inventory"]:
            from models import Inventory
            player.inventory = Inventory.from_dict(data["inventory"])
        
        return player

class NPC:
    def __init__(self, id: str, name: str, description: str, friendly: bool = True,
                 dialogue: Dict = None, quest_giver: bool = False,
                 merchant: bool = False, inventory: Dict = None,
                 health: int = 100, attack: int = 10, defense: int = 5,
                 special_abilities: List = None, loot: Dict = None,
                 faction: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.friendly = friendly
        self.dialogue = dialogue or {"greeting": f"Hello, traveler."}
        self.quest_giver = quest_giver
        self.merchant = merchant
        self.inventory = inventory or {}
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.special_abilities = special_abilities or []
        self.loot = loot or {}
        self.faction = faction
        self.current_dialogue = "greeting"
        self.flags = {}  # NPC-specific flags
    
    def talk(self, player, response: str = None) -> Tuple[str, Dict]:
        """Handle conversation with the NPC."""
        responses = {}
        
        if response and response in self.dialogue:
            # Player selected a response option
            response_data = self.dialogue[response]
            
            # Update NPC flags if needed
            if "set_flag" in response_data:
                flag, value = response_data["set_flag"]
                self.flags[flag] = value
            
            # Update player flags if needed
            if "set_player_flag" in response_data:
                flag, value = response_data["set_player_flag"]
                player.flags[flag] = value
            
            # Handle quest starting
            if "start_quest" in response_data and response_data["start_quest"] not in player.quest_log:
                player.quest_log.append(response_data["start_quest"])
                print_slow(f"Quest started: {response_data['start_quest']}")
            
            # Set next dialogue
            self.current_dialogue = response_data.get("next", "greeting")
            dialogue_text = response_data["text"]
        else:
            # Initial or default dialogue
            if "condition" in self.dialogue.get(self.current_dialogue, {}):
                # Check condition for conditional dialogue
                condition = self.dialogue[self.current_dialogue]["condition"]
                if condition["type"] == "player_flag":
                    flag, value = condition["flag"], condition["value"]
                    branch = "success" if player.flags.get(flag) == value else "failure"
                    dialogue_text = self.dialogue[self.current_dialogue][branch]["text"]
                    self.current_dialogue = self.dialogue[self.current_dialogue][branch].get("next", "greeting")
                elif condition["type"] == "npc_flag":
                    flag, value = condition["flag"], condition["value"]
                    branch = "success" if self.flags.get(flag) == value else "failure"
                    dialogue_text = self.dialogue[self.current_dialogue][branch]["text"]
                    self.current_dialogue = self.dialogue[self.current_dialogue][branch].get("next", "greeting")
                elif condition["type"] == "quest_complete":
                    quest_id = condition["quest_id"]
                    branch = "success" if quest_id in player.completed_quests else "failure"
                    dialogue_text = self.dialogue[self.current_dialogue][branch]["text"]
                    self.current_dialogue = self.dialogue[self.current_dialogue][branch].get("next", "greeting")
                elif condition["type"] == "item":
                    item_id = condition["item_id"]
                    has_item = player.inventory and player.inventory.get_item_by_id(item_id)
                    branch = "success" if has_item else "failure"
                    dialogue_text = self.dialogue[self.current_dialogue][branch]["text"]
                    self.current_dialogue = self.dialogue[self.current_dialogue][branch].get("next", "greeting")
                else:
                    dialogue_text = self.dialogue.get(self.current_dialogue, {"text": "..."})["text"]
            else:
                dialogue_text = self.dialogue.get(self.current_dialogue, {"text": "..."})["text"]
        
        # Get response options for current dialogue
        current_dialogue_data = self.dialogue.get(self.current_dialogue, {})
        
        if "responses" in current_dialogue_data:
            # Filter responses based on conditions
            for resp_id, resp_data in current_dialogue_data["responses"].items():
                if "condition" in resp_data:
                    condition = resp_data["condition"]
                    if condition["type"] == "player_flag":
                        flag, value = condition["flag"], condition["value"]
                        if player.flags.get(flag) == value:
                            responses[resp_id] = resp_data["text"]
                    elif condition["type"] == "npc_flag":
                        flag, value = condition["flag"], condition["value"]
                        if self.flags.get(flag) == value:
                            responses[resp_id] = resp_data["text"]
                    elif condition["type"] == "quest_complete":
                        quest_id = condition["quest_id"]
                        if quest_id in player.completed_quests:
                            responses[resp_id] = resp_data["text"]
                    elif condition["type"] == "item":
                        item_id = condition["item_id"]
                        if player.inventory and player.inventory.get_item_by_id(item_id):
                            responses[resp_id] = resp_data["text"]
                else:
                    responses[resp_id] = resp_data["text"]
        
        # Add farewell option if no responses
        if not responses:
            responses["farewell"] = "Farewell."
        
        return dialogue_text, responses
    
    def get_loot(self, world) -> List:
        """Generate loot drops when NPC is defeated."""
        items = []
        essence = random.randint(self.loot.get("essence_min", 10), self.loot.get("essence_max", 50))
        
        # Check for guaranteed items
        if "guaranteed" in self.loot:
            for item_id in self.loot["guaranteed"]:
                item = world.get_item_by_id(item_id)
                if item:
                    items.append(item)
        
        # Check for random drops
        if "random" in self.loot:
            for loot_entry in self.loot["random"]:
                item_id = loot_entry["id"]
                chance = loot_entry["chance"]
                
                if random.random() < chance:
                    item = world.get_item_by_id(item_id)
                    if item:
                        items.append(item)
        
        return items, essence
    
    def attack_player(self, player) -> Tuple[int, bool, str]:
        """Attack the player and return damage, critical hit flag, and message."""
        damage = self.attack
        
        # Check for critical hit (10% chance)
        critical = random.random() < 0.1
        if critical:
            damage = int(damage * 1.5)
        
        # Apply random variance (±10%)
        variance = random.uniform(0.9, 1.1)
        damage = int(damage * variance)
        
        # Apply player defense
        defense = 0
        if player.inventory:
            defense = player.inventory.get_total_defense()
        
        reduction = defense / (defense + 50)
        damage = max(1, int(damage * (1 - reduction)))
        
        # Create message
        if critical:
            message = f"{self.name} lands a critical hit for {damage} damage!"
        else:
            message = f"{self.name} attacks you for {damage} damage."
        
        return damage, critical, message
    
    def take_damage(self, damage: int) -> Tuple[int, bool]:
        """Take damage and return actual damage dealt and whether NPC died."""
        # Apply defense reduction
        reduction = self.defense / (self.defense + 50)
        actual_damage = max(1, int(damage * (1 - reduction)))
        
        self.health -= actual_damage
        return actual_damage, self.health <= 0
    
    def to_dict(self) -> Dict:
        """Convert NPC to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "friendly": self.friendly,
            "dialogue": self.dialogue,
            "quest_giver": self.quest_giver,
            "merchant": self.merchant,
            "inventory": self.inventory,
            "health": self.health,
            "max_health": self.max_health,
            "attack": self.attack,
            "defense": self.defense,
            "special_abilities": self.special_abilities,
            "loot": self.loot,
            "faction": self.faction,
            "current_dialogue": self.current_dialogue,
            "flags": self.flags
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create NPC from dictionary."""
        npc = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            friendly=data["friendly"],
            dialogue=data["dialogue"],
            quest_giver=data["quest_giver"],
            merchant=data["merchant"],
            inventory=data["inventory"],
            health=data["health"],
            attack=data["attack"],
            defense=data["defense"],
            special_abilities=data["special_abilities"],
            loot=data["loot"],
            faction=data["faction"]
        )
        
        npc.max_health = data["max_health"]
        npc.current_dialogue = data["current_dialogue"]
        npc.flags = data["flags"].copy()
        
        return npc

class Location:
    def __init__(self, id: str, name: str, description: str, connections: Dict = None,
                 npcs: List = None, items: List = None, enemies: List = None,
                 is_beacon: bool = False, is_shop: bool = False, 
                 is_boss_area: bool = False, region: str = None,
                 visit_requirement: Dict = None, ascii_art: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.connections = connections or {}  # {direction: location_id}
        self.npcs = npcs or []  # List of NPC IDs
        self.items = items or []  # List of Item objects
        self.enemies = enemies or []  # List of possible enemy NPC IDs
        self.active_enemies = []  # List of currently spawned enemy NPCs
        self.is_beacon = is_beacon
        self.is_shop = is_shop
        self.is_boss_area = is_boss_area
        self.region = region
        self.visit_requirement = visit_requirement  # e.g., {"item": "key_id"} or {"quest_complete": "quest_id"}
        self.ascii_art = ascii_art
        self.dropped_essence = 0  # Player's dropped essence
        self.dropped_essence_time = None  # When essence was dropped
    
    def can_visit(self, player) -> Tuple[bool, str]:
        """Check if player can visit this location."""
        if not self.visit_requirement:
            return True, ""
        
        req_type = next(iter(self.visit_requirement))
        
        if req_type == "item":
            item_id = self.visit_requirement["item"]
            if player.inventory and player.inventory.get_item_by_id(item_id):
                return True, ""
            else:
                return False, "You need a specific item to enter this area."
        
        elif req_type == "quest_complete":
            quest_id = self.visit_requirement["quest_complete"]
            if quest_id in player.completed_quests:
                return True, ""
            else:
                return False, "You must complete a specific quest to enter this area."
        
        elif req_type == "player_flag":
            flag, value = self.visit_requirement["player_flag"]
            if player.flags.get(flag) == value:
                return True, ""
            else:
                return False, "You cannot enter this area yet."
        
        return True, ""
    
    def spawn_enemies(self, world) -> List:
        """Spawn enemies based on the location's enemy list."""
        # Check if boss area
        if self.is_boss_area and self.enemies:
            # Boss areas spawn a single boss
            boss_id = self.enemies[0]  # Assume first enemy in list is the boss
            boss = world.get_npc_by_id(boss_id)
            if boss:
                # Create a copy of the boss to avoid modifying the template
                import copy
                boss_copy = copy.deepcopy(boss)
                self.active_enemies = [boss_copy]
                return [boss_copy]
            return []
        
        # Regular areas can have random encounters
        self.active_enemies = []
        
        # 80% chance to spawn enemies if area has enemy types
        if self.enemies and random.random() < 0.8:
            # Determine number of enemies (1-3 typically)
            count = random.randint(1, min(3, len(self.enemies)))
            
            for _ in range(count):
                enemy_id = random.choice(self.enemies)
                enemy = world.get_npc_by_id(enemy_id)
                if enemy:
                    # Create a copy of the enemy to avoid modifying the template
                    import copy
                    enemy_copy = copy.deepcopy(enemy)
                    self.active_enemies.append(enemy_copy)
        
        return self.active_enemies
    
    def to_dict(self) -> Dict:
        """Convert location to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "connections": self.connections,
            "npcs": self.npcs,
            "items": [item.to_dict() for item in self.items],
            "enemies": self.enemies,
            "active_enemies": [enemy.to_dict() for enemy in self.active_enemies],
            "is_beacon": self.is_beacon,
            "is_shop": self.is_shop,
            "is_boss_area": self.is_boss_area,
            "region": self.region,
            "visit_requirement": self.visit_requirement,
            "ascii_art": self.ascii_art,
            "dropped_essence": self.dropped_essence,
            "dropped_essence_time": self.dropped_essence_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create location from dictionary."""
        from game_data import create_item_from_dict
        
        location = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            connections=data["connections"],
            npcs=data["npcs"],
            enemies=data["enemies"],
            is_beacon=data["is_beacon"],
            is_shop=data["is_shop"],
            is_boss_area=data["is_boss_area"],
            region=data["region"],
            visit_requirement=data["visit_requirement"],
            ascii_art=data["ascii_art"]
        )
        
        # Create items
        for item_data in data["items"]:
            item = create_item_from_dict(item_data)
            location.items.append(item)
        
        # Create active enemies
        for enemy_data in data["active_enemies"]:
            enemy = NPC.from_dict(enemy_data)
            location.active_enemies.append(enemy)
        
        location.dropped_essence = data["dropped_essence"]
        location.dropped_essence_time = data["dropped_essence_time"]
        
        return location 