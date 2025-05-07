from typing import Dict, List, Optional, Tuple, Union, Any
import random
import json
from config import DIVIDER

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
        
        # Example: Buff item
        elif self.item_type == "consumable" and "buff" in self.stats:
            buff_type = self.stats["buff"]["type"]
            buff_amount = self.stats["buff"]["amount"]
            buff_duration = self.stats["buff"]["duration"]
            player.apply_buff(buff_type, buff_amount, buff_duration)
            result = f"You use the {self.name} and gain {buff_amount} {buff_type} for {buff_duration} turns."
        
        # Reduce quantity after use
        self.quantity -= 1
        if self.quantity <= 0:
            player.inventory.remove(self)
        
        return result
    
    def to_dict(self) -> Dict:
        """Convert the item to a dictionary for saving."""
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
    def from_dict(cls, data: Dict):
        """Create an item from a dictionary."""
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
                 attack_speed: float, weapon_type: str, range_type: str = "melee", 
                 special_effects: Dict = None, value: int = 0, weight: float = 0.0, 
                 durability: int = 100, stamina_cost: int = 10, stats: Dict = None):
        super().__init__(id, name, description, "weapon", value, weight, stats, False, True)
        self.damage = damage
        self.attack_speed = attack_speed
        self.weapon_type = weapon_type  # sword, axe, bow, etc.
        self.range_type = range_type  # melee or ranged
        self.special_effects = special_effects or {}
        self.durability = durability
        self.max_durability = durability
        self.stamina_cost = stamina_cost
    
    def to_dict(self) -> Dict:
        """Convert the weapon to a dictionary for saving."""
        data = super().to_dict()
        data.update({
            "damage": self.damage,
            "attack_speed": self.attack_speed,
            "weapon_type": self.weapon_type,
            "range_type": self.range_type,
            "special_effects": self.special_effects,
            "durability": self.durability,
            "max_durability": self.max_durability,
            "stamina_cost": self.stamina_cost
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create a weapon from a dictionary."""
        weapon = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            damage=data["damage"],
            attack_speed=data["attack_speed"],
            weapon_type=data["weapon_type"],
            range_type=data["range_type"],
            special_effects=data["special_effects"],
            value=data["value"],
            weight=data["weight"],
            durability=data["durability"],
            stamina_cost=data["stamina_cost"],
            stats=data["stats"]
        )
        weapon.max_durability = data["max_durability"]
        weapon.equipped = data["equipped"]
        weapon.quantity = data["quantity"]
        return weapon

class Armor(Item):
    def __init__(self, id: str, name: str, description: str, defense: int, 
                 armor_type: str, resistance: Dict = None, value: int = 0, 
                 weight: float = 0.0, durability: int = 100, stats: Dict = None):
        super().__init__(id, name, description, "armor", value, weight, stats, False, True)
        self.defense = defense
        self.armor_type = armor_type  # head, chest, legs, etc.
        self.resistance = resistance or {}  # fire, ice, poison, etc.
        self.durability = durability
        self.max_durability = durability
    
    def to_dict(self) -> Dict:
        """Convert the armor to a dictionary for saving."""
        data = super().to_dict()
        data.update({
            "defense": self.defense,
            "armor_type": self.armor_type,
            "resistance": self.resistance,
            "durability": self.durability,
            "max_durability": self.max_durability
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create armor from a dictionary."""
        armor = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            defense=data["defense"],
            armor_type=data["armor_type"],
            resistance=data["resistance"],
            value=data["value"],
            weight=data["weight"],
            durability=data["durability"],
            stats=data["stats"]
        )
        armor.max_durability = data["max_durability"]
        armor.equipped = data["equipped"]
        armor.quantity = data["quantity"]
        return armor

class Consumable(Item):
    def __init__(self, id: str, name: str, description: str, effect_type: str, 
                 effect_value: int, duration: int = 0, value: int = 0, 
                 weight: float = 0.0, stats: Dict = None):
        super().__init__(id, name, description, "consumable", value, weight, stats, True, False)
        self.effect_type = effect_type  # heal, buff, cure, etc.
        self.effect_value = effect_value
        self.duration = duration  # 0 for instant effects
    
    def to_dict(self) -> Dict:
        """Convert the consumable to a dictionary for saving."""
        data = super().to_dict()
        data.update({
            "effect_type": self.effect_type,
            "effect_value": self.effect_value,
            "duration": self.duration
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create a consumable from a dictionary."""
        consumable = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            effect_type=data["effect_type"],
            effect_value=data["effect_value"],
            duration=data["duration"],
            value=data["value"],
            weight=data["weight"],
            stats=data["stats"]
        )
        consumable.equipped = data["equipped"]
        consumable.quantity = data["quantity"]
        return consumable

class Inventory:
    def __init__(self, capacity: int = 20):
        self.items = []
        self.capacity = capacity
        self.equipped = {
            "weapon": None,
            "head": None,
            "chest": None,
            "legs": None,
            "accessory": None
        }
    
    def add_item(self, item: Item) -> bool:
        """Add an item to the inventory."""
        # Check if item already exists (for stackable items)
        if item.quantity > 0 and not item.equippable:
            for existing_item in self.items:
                if existing_item.id == item.id and not existing_item.equippable:
                    existing_item.quantity += item.quantity
                    return True
        
        # Check capacity
        if len(self.items) >= self.capacity:
            return False
        
        self.items.append(item)
        return True
    
    def remove_item(self, item: Item) -> bool:
        """Remove an item from the inventory."""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def get_item_by_id(self, item_id: str) -> Optional[Item]:
        """Get an item by its ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def equip_item(self, item: Item) -> str:
        """Equip an item and return a message."""
        if not item.equippable:
            return f"You cannot equip the {item.name}."
        
        slot = None
        if item.item_type == "weapon":
            slot = "weapon"
        elif item.item_type == "armor":
            if item.armor_type in ["head", "chest", "legs", "accessory"]:
                slot = item.armor_type
        
        if slot is None:
            return f"You cannot equip the {item.name}."
        
        # Unequip current item in slot
        if self.equipped[slot]:
            self.equipped[slot].equipped = False
        
        # Equip new item
        self.equipped[slot] = item
        item.equipped = True
        
        return f"You equipped the {item.name}."
    
    def unequip_item(self, slot: str) -> str:
        """Unequip an item from a slot and return a message."""
        if slot not in self.equipped or not self.equipped[slot]:
            return f"You have nothing equipped on your {slot}."
        
        item = self.equipped[slot]
        item.equipped = False
        self.equipped[slot] = None
        
        return f"You unequipped the {item.name}."
    
    def get_total_defense(self) -> int:
        """Calculate total defense from equipped armor."""
        total = 0
        for slot in ["head", "chest", "legs"]:
            if self.equipped[slot]:
                total += self.equipped[slot].defense
        return total
    
    def get_resistance(self, damage_type: str) -> float:
        """Calculate resistance to a specific damage type."""
        total = 0.0
        for slot in ["head", "chest", "legs", "accessory"]:
            if self.equipped[slot] and hasattr(self.equipped[slot], "resistance"):
                resistance = self.equipped[slot].resistance.get(damage_type, 0.0)
                total += resistance
        return min(total, 0.75)  # Cap resistance at 75%
    
    def to_dict(self) -> Dict:
        """Convert the inventory to a dictionary for saving."""
        equipped_dict = {}
        for slot, item in self.equipped.items():
            equipped_dict[slot] = item.to_dict() if item else None
        
        return {
            "items": [item.to_dict() for item in self.items],
            "capacity": self.capacity,
            "equipped": equipped_dict
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create an inventory from a dictionary."""
        from game_data import create_item_from_dict
        
        inventory = cls(capacity=data["capacity"])
        
        # Add items
        for item_data in data["items"]:
            item = create_item_from_dict(item_data)
            inventory.items.append(item)
        
        # Set equipped items
        for slot, item_data in data["equipped"].items():
            if item_data:
                item = inventory.get_item_by_id(item_data["id"])
                if item:
                    inventory.equipped[slot] = item
                    item.equipped = True
        
        return inventory 