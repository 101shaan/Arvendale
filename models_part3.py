from typing import Dict, List, Optional, Tuple, Union, Any
import random
import time
from config import DIVIDER
from utils import print_slow, display_bar

class Quest:
    def __init__(self, id: str, name: str, description: str, objectives: List[Dict],
                 rewards: Dict, completed: bool = False, progress: Dict = None):
        self.id = id
        self.name = name
        self.description = description
        self.objectives = objectives
        self.rewards = rewards
        self.completed = completed
        self.progress = progress or self._initialize_progress()
    
    def _initialize_progress(self) -> Dict:
        """Initialize progress tracking for objectives."""
        progress = {}
        for i, objective in enumerate(self.objectives):
            objective_id = f"obj_{i}"
            progress[objective_id] = {
                "type": objective["type"],
                "target": objective["target"],
                "quantity": 0,
                "required": objective["quantity"],
                "completed": False
            }
        return progress
    
    def update_progress(self, objective_type: str, target: str, amount: int = 1) -> bool:
        """Update progress on an objective and check if completed."""
        any_updated = False
        all_complete = True
        
        for obj_id, progress in self.progress.items():
            if progress["type"] == objective_type and progress["target"] == target and not progress["completed"]:
                progress["quantity"] += amount
                if progress["quantity"] >= progress["required"]:
                    progress["quantity"] = progress["required"]
                    progress["completed"] = True
                any_updated = True
            
            if not progress["completed"]:
                all_complete = False
        
        self.completed = all_complete
        return any_updated
    
    def get_progress_text(self) -> str:
        """Get a formatted string showing quest progress."""
        text = f"{self.name}\n{self.description}\n\nObjectives:\n"
        
        for obj_id, progress in self.progress.items():
            status = "✓" if progress["completed"] else " "
            if progress["type"] == "kill":
                text += f"[{status}] Defeat {progress['target'].replace('_', ' ').title()}: {progress['quantity']}/{progress['required']}\n"
            elif progress["type"] == "item":
                text += f"[{status}] Collect {progress['target'].replace('_', ' ').title()}: {progress['quantity']}/{progress['required']}\n"
            elif progress["type"] == "location":
                text += f"[{status}] Discover {progress['target'].replace('_', ' ').title()}\n"
            elif progress["type"] == "talk":
                text += f"[{status}] Speak with {progress['target'].replace('_', ' ').title()}\n"
        
        return text
    
    def to_dict(self) -> Dict:
        """Convert quest to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "objectives": self.objectives,
            "rewards": self.rewards,
            "completed": self.completed,
            "progress": self.progress
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create quest from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            objectives=data["objectives"],
            rewards=data["rewards"],
            completed=data["completed"],
            progress=data["progress"]
        )

class World:
    def __init__(self):
        self.locations = {}
        self.npcs = {}
        self.items = {}
        self.quests = {}
        self.regions = {}
        self.time_passed = 0  # Game time tracker (in-game days)
        self.global_flags = {}  # World state flags
    
    def add_location(self, location):
        """Add a location to the world."""
        self.locations[location.id] = location
        
        # Add to region if specified
        if location.region:
            if location.region not in self.regions:
                self.regions[location.region] = []
            if location not in self.regions[location.region]:
                self.regions[location.region].append(location)
    
    def add_npc(self, npc):
        """Add an NPC to the world."""
        self.npcs[npc.id] = npc
    
    def add_item(self, item):
        """Add an item template to the world."""
        self.items[item.id] = item
    
    def add_quest(self, quest):
        """Add a quest to the world."""
        self.quests[quest.id] = quest
    
    def get_location_by_id(self, location_id: str):
        """Get a location by its ID."""
        return self.locations.get(location_id)
    
    def get_npc_by_id(self, npc_id: str):
        """Get an NPC by its ID."""
        return self.npcs.get(npc_id)
    
    def get_item_by_id(self, item_id: str):
        """Get an item template by its ID."""
        item_template = self.items.get(item_id)
        if item_template:
            # Create a copy of the item template
            import copy
            return copy.deepcopy(item_template)
        return None
    
    def get_quest_by_id(self, quest_id: str):
        """Get a quest by its ID."""
        return self.quests.get(quest_id)
    
    def get_npcs_at_location(self, location_id: str) -> List:
        """Get all NPCs at a specific location."""
        location = self.get_location_by_id(location_id)
        if not location:
            return []
        
        npcs = []
        for npc_id in location.npcs:
            npc = self.get_npc_by_id(npc_id)
            if npc:
                npcs.append(npc)
        
        return npcs
    
    def update_world_state(self, player):
        """Update the world state based on time, player actions, etc."""
        # Update dropped essence timers
        for location in self.locations.values():
            if location.dropped_essence > 0 and location.dropped_essence_time:
                # Essence disappears after 1 hour (real time)
                elapsed = time.time() - location.dropped_essence_time
                if elapsed > 3600:  # 1 hour in seconds
                    location.dropped_essence = 0
                    location.dropped_essence_time = None
        
        # Update active enemies in locations
        for location in self.locations.values():
            # Remove dead enemies
            location.active_enemies = [enemy for enemy in location.active_enemies if enemy.health > 0]
    
    def resolve_location_ids(self, player):
        """Resolve location IDs stored during loading."""
        if hasattr(player, "_current_location_id") and player._current_location_id:
            player.current_location = self.get_location_by_id(player._current_location_id)
        
        if hasattr(player, "_previous_location_id") and player._previous_location_id:
            player.previous_location = self.get_location_by_id(player._previous_location_id)
        
        if hasattr(player, "_last_beacon_id") and player._last_beacon_id:
            player.last_beacon = self.get_location_by_id(player._last_beacon_id)
        
        if hasattr(player, "_discovered_locations_ids"):
            player.discovered_locations = [
                self.get_location_by_id(loc_id) 
                for loc_id in player._discovered_locations_ids
                if self.get_location_by_id(loc_id)
            ]
    
    def to_dict(self) -> Dict:
        """Convert world to dictionary for saving."""
        return {
            "locations": {loc_id: loc.to_dict() for loc_id, loc in self.locations.items()},
            "npcs": {npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()},
            "items": {item_id: item.to_dict() for item_id, item in self.items.items()},
            "quests": {quest_id: quest.to_dict() for quest_id, quest in self.quests.items()},
            "time_passed": self.time_passed,
            "global_flags": self.global_flags.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create world from dictionary."""
        from models import Item, Weapon, Armor, Consumable
        from models_part2 import NPC, Location
        
        world = cls()
        
        # Create items first (needed for other objects)
        for item_id, item_data in data["items"].items():
            if item_data["item_type"] == "weapon":
                item = Weapon.from_dict(item_data)
            elif item_data["item_type"] == "armor":
                item = Armor.from_dict(item_data)
            elif item_data["item_type"] == "consumable":
                item = Consumable.from_dict(item_data)
            else:
                item = Item.from_dict(item_data)
            
            world.items[item_id] = item
        
        # Create NPCs
        for npc_id, npc_data in data["npcs"].items():
            npc = NPC.from_dict(npc_data)
            world.npcs[npc_id] = npc
        
        # Create quests
        for quest_id, quest_data in data["quests"].items():
            quest = Quest.from_dict(quest_data)
            world.quests[quest_id] = quest
        
        # Create locations (after NPCs and items since they reference them)
        for loc_id, loc_data in data["locations"].items():
            location = Location.from_dict(loc_data)
            world.locations[loc_id] = location
            
            # Add to region
            if location.region:
                if location.region not in world.regions:
                    world.regions[location.region] = []
                world.regions[location.region].append(location)
        
        world.time_passed = data["time_passed"]
        world.global_flags = data["global_flags"].copy()
        
        return world 