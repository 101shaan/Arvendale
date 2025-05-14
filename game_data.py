from models import Item, Weapon, Armor, Consumable, Inventory
from models_part2 import Player, NPC, Location
from models_part3 import World, Quest

def create_item_from_dict(item_data):
    """Create the appropriate item type from a dictionary."""
    item_type = item_data.get("item_type", "")
    
    if item_type == "weapon":
        return Weapon.from_dict(item_data)
    elif item_type == "armor":
        return Armor.from_dict(item_data)
    elif item_type == "consumable":
        return Consumable.from_dict(item_data)
    else:
        return Item.from_dict(item_data)

def initialize_game_data():
    """Initialize all game data and return a World object."""
    world = World()
    
    # Initialize items
    initialize_items(world)
    
    # Initialize NPCs
    initialize_npcs(world)
    
    # Initialize locations
    initialize_locations(world)
    
    # Initialize quests
    initialize_quests(world)
    
    # Initialize region maps
    initialize_maps(world)
    
    return world

def initialize_items(world):
    """Initialize all items in the game."""
    # Weapons
    ember_blade = Weapon(
        id="ember_blade",
        name="Ember Blade",
        description="A sword forged in ember essence. Burns with a subtle flame.",
        damage=25,
        attack_speed=1.2,
        weapon_type="sword",
        special_effects={"fire_damage": 5},
        value=500,
        weight=3.5,
        durability=100,
        stamina_cost=12
    )
    world.add_item(ember_blade)
    
    frost_mace = Weapon(
        id="frost_mace",
        name="Vordt's Frostmace",
        description="A massive ice-infused mace. Slow but devastating.",
        damage=40,
        attack_speed=0.7,
        weapon_type="mace",
        special_effects={"frost_damage": 8, "stun_chance": 0.15},
        value=800,
        weight=8.0,
        durability=150,
        stamina_cost=20
    )
    world.add_item(frost_mace)
    
    shadow_dagger = Weapon(
        id="shadow_dagger",
        name="Shadow Dagger",
        description="A swift blade that barely reflects light. Perfect for quick strikes.",
        damage=15,
        attack_speed=2.0,
        weapon_type="dagger",
        special_effects={"bleed_chance": 0.25},
        value=450,
        weight=1.0,
        durability=70,
        stamina_cost=8
    )
    world.add_item(shadow_dagger)
    
    # Armors
    knight_armor = Armor(
        id="knight_armor",
        name="Knight's Plate",
        description="Heavy but reliable plate armor.",
        defense=30,
        armor_type="chest",
        resistance={"physical": 0.2, "fire": 0.1},
        value=600,
        weight=12.0,
        durability=200
    )
    world.add_item(knight_armor)
    
    ranger_hood = Armor(
        id="ranger_hood",
        name="Ranger's Hood",
        description="A lightweight hood offering moderate protection.",
        defense=10,
        armor_type="head",
        resistance={"frost": 0.15},
        value=300,
        weight=1.5,
        durability=100
    )
    world.add_item(ranger_hood)
    
    ashen_leggings = Armor(
        id="ashen_leggings",
        name="Ashen Leggings",
        description="Leggings infused with ember essence. Resistant to fire.",
        defense=15,
        armor_type="legs",
        resistance={"fire": 0.3},
        value=450,
        weight=6.0,
        durability=120
    )
    world.add_item(ashen_leggings)
    
    # Consumables
    healing_potion = Consumable(
        id="healing_potion",
        name="Healing Potion",
        description="A red potion that restores health.",
        effect_type="heal",
        effect_value=50,
        value=100,
        weight=0.5,
        stats={"healing": 50}
    )
    world.add_item(healing_potion)
    
    stamina_elixir = Consumable(
        id="stamina_elixir",
        name="Stamina Elixir",
        description="A green elixir that restores stamina.",
        effect_type="stamina",
        effect_value=40,
        value=80,
        weight=0.5,
        stats={"stamina": 40}
    )
    world.add_item(stamina_elixir)
    
    strength_tonic = Consumable(
        id="strength_tonic",
        name="Strength Tonic",
        description="Temporarily increases strength.",
        effect_type="buff",
        effect_value=10,
        duration=5,
        value=150,
        weight=0.5,
        stats={"buff": {"type": "strength", "amount": 10, "duration": 5}}
    )
    world.add_item(strength_tonic)
    
    # Key items
    ashen_key = Item(
        id="ashen_key",
        name="Ashen Key",
        description="A key forged from ashen metal. Opens something important.",
        item_type="key",
        value=0,
        weight=0.1
    )
    world.add_item(ashen_key)
    
    blue_signet = Item(
        id="blue_signet",
        name="Blue Signet Ring",
        description="A ring bearing the crest of a noble house.",
        item_type="key",
        value=200,
        weight=0.1
    )
    world.add_item(blue_signet)
    
    # Materials
    ember_essence = Item(
        id="ember_essence",
        name="Ember Essence",
        description="A glowing red essence extracted from the Ashen Woods.",
        item_type="material",
        value=150,
        weight=0.2
    )
    world.add_item(ember_essence)
    
    frost_essence = Item(
        id="frost_essence",
        name="Frost Essence",
        description="A chilling blue essence that never seems to melt.",
        item_type="material",
        value=150,
        weight=0.2
    )
    world.add_item(frost_essence)

def initialize_npcs(world):
    """Initialize all NPCs in the game."""
    # Friendly NPCs
    blacksmith = NPC(
        id="blacksmith_andre",
        name="Andre the Blacksmith",
        description="A muscular smith with a kind face, working tirelessly at his forge.",
        friendly=True,
        dialogue={
            "greeting": {
                "text": "Welcome to my forge, traveler. Need something smithed or repaired?",
                "responses": {
                    "smith": {
                        "text": "Can you forge me a weapon?",
                        "response_text": "I could forge you something special if you bring me the right materials. I need ember essence from the Ashen Woods.",
                        "next": "smith_options"
                    },
                    "repair": {
                        "text": "I need something repaired.",
                        "response_text": "Let me see what you've got. Hmm, I can fix this for 50 essence.",
                        "next": "repair_options"
                    },
                    "quest": {
                        "text": "I'm looking for work.",
                        "next": "quest"
                    },
                    "farewell": {
                        "text": "Just looking around. Farewell.",
                        "response_text": "Come back when you need something forged."
                    }
                }
            },
            "smith_options": {
                "text": "I could forge you something special if you bring me the right materials. I need ember essence from the Ashen Woods.",
                "responses": {
                    "accept_quest": {
                        "text": "I'll find this ember essence for you.",
                        "response_text": "Excellent! The Ashen Woods are to the northeast. Be careful, the forest guardians are fierce protectors.",
                        "start_quest": "ember_quest",
                        "next": "greeting"
                    },
                    "reject": {
                        "text": "Maybe another time.",
                        "response_text": "As you wish. The offer stands if you change your mind.",
                        "next": "greeting"
                    }
                }
            },
            "repair_options": {
                "text": "Let me see what you've got. Hmm, I can fix this for 50 essence.",
                "responses": {
                    "accept_repair": {
                        "text": "Please repair it.",
                        "response_text": "Good as new! Your equipment should serve you well now.",
                        "next": "greeting"
                    },
                    "reject": {
                        "text": "That's too expensive.",
                        "response_text": "That's my price. Quality work doesn't come cheap.",
                        "next": "greeting"
                    }
                }
            },
            "quest": {
                "condition": {
                    "type": "quest_complete",
                    "quest_id": "ember_quest"
                },
                "success": {
                    "text": "You've already helped me with the ember essence. I'm grateful.",
                    "next": "greeting"
                },
                "failure": {
                    "text": "If you bring me ember essence from the Ashen Woods, I can forge you a special weapon.",
                    "responses": {
                        "accept": {
                            "text": "I'll find this ember essence for you.",
                            "response_text": "Excellent! The Ashen Woods are to the northeast. Be careful, the forest guardians are fierce protectors.",
                            "start_quest": "ember_quest",
                            "next": "greeting"
                        },
                        "reject": {
                            "text": "Maybe another time.",
                            "response_text": "As you wish. The offer stands if you change your mind.",
                            "next": "greeting"
                        }
                    }
                }
            }
        },
        quest_giver=True,
        merchant=True,
        inventory={
            "items": ["healing_potion", "stamina_elixir"],
            "sell_rate": 1.0,
            "buy_rate": 0.5
        }
    )
    world.add_npc(blacksmith)
    
    merchant = NPC(
        id="merchant_ulrich",
        name="Ulrich the Merchant",
        description="A shrewd-looking trader with a large backpack full of wares.",
        friendly=True,
        dialogue={
            "greeting": {
                "text": "Ah, a customer! What can Ulrich provide for you today?",
                "responses": {
                    "buy": {
                        "text": "Show me your wares.",
                        "response_text": "Take a look at my fine collection. Only the best for my customers!",
                        "next": "shop"
                    },
                    "sell": {
                        "text": "I have items to sell.",
                        "response_text": "Let's see what treasures you've found. I'll give you a fair price... mostly.",
                        "next": "shop"
                    },
                    "quest": {
                        "text": "Is there anything you need help with?",
                        "next": "quest"
                    },
                    "farewell": {
                        "text": "Just passing by. Farewell.",
                        "response_text": "Safe travels! Remember, Ulrich always has the finest goods when you return."
                    }
                }
            },
            "shop": {
                "text": "Here's what I have for sale today. Quality goods at reasonable prices!",
                "responses": {
                    "buy_item": {
                        "text": "I'll take this.",
                        "response_text": "Excellent choice! This will serve you well.",
                        "next": "greeting"
                    },
                    "haggle": {
                        "text": "Your prices are too high.",
                        "response_text": "My friend, these items are worth every essence! But perhaps we can negotiate...",
                        "next": "greeting"
                    },
                    "back": {
                        "text": "Let me think about it.",
                        "response_text": "Take your time. Quality merchandise is worth careful consideration.",
                        "next": "greeting"
                    }
                }
            },
            "quest": {
                "condition": {
                    "type": "quest_complete",
                    "quest_id": "signet_quest"
                },
                "success": {
                    "text": "Thank you again for finding my signet ring. I've been able to resume my business properly.",
                    "next": "greeting"
                },
                "failure": {
                    "text": "Actually, I lost my signet ring in the Blighted Marshes during my last expedition. It's quite valuable to me. If you find it, I'd reward you handsomely.",
                    "responses": {
                        "accept": {
                            "text": "I'll look for your ring.",
                            "response_text": "Splendid! The ring has a blue gemstone with my family crest. Last I had it was near the old watchtower in the marshes.",
                            "start_quest": "signet_quest",
                            "next": "greeting"
                        },
                        "reject": {
                            "text": "I don't have time for that.",
                            "response_text": "Unfortunate, but I understand. The marshes are dangerous. Perhaps another time.",
                            "next": "greeting"
                        }
                    }
                }
            }
        },
        quest_giver=True,
        merchant=True,
        inventory={
            "items": ["healing_potion", "stamina_elixir", "strength_tonic", "shadow_dagger", "ranger_hood"],
            "sell_rate": 1.2,
            "buy_rate": 0.4
        }
    )
    world.add_npc(merchant)
    
    # Enemy NPCs
    hollow_soldier = NPC(
        id="hollow_soldier",
        name="Hollow Soldier",
        description="A once-proud warrior, now a mindless husk with decaying armor.",
        friendly=False,
        health=60,
        attack=12,
        defense=8,
        loot={
            "essence_min": 30,
            "essence_max": 80,
            "random": [
                {"id": "healing_potion", "chance": 0.3}
            ]
        }
    )
    world.add_npc(hollow_soldier)
    
    forest_guardian = NPC(
        id="forest_guardian",
        name="Forest Guardian",
        description="A twisted being of bark and leaves, protector of the ancient woods.",
        friendly=False,
        health=100,
        attack=15,
        defense=12,
        special_abilities=[
            {
                "name": "Root Entangle",
                "type": "status",
                "effect": "slow",
                "potency": -5,
                "duration": 3
            }
        ],
        loot={
            "essence_min": 100,
            "essence_max": 180,
            "guaranteed": ["ember_essence"],
            "random": [
                {"id": "strength_tonic", "chance": 0.5}
            ]
        }
    )
    world.add_npc(forest_guardian)
    
    # Boss NPCs
    vordt = NPC(
        id="vordt",
        name="Vordt, the Frost Guardian",
        description="A massive armored beast wielding a frost-imbued mace. Its breath freezes the air around it.",
        friendly=False,
        health=300,
        attack=25,
        defense=20,
        special_abilities=[
            {
                "name": "Frost Breath",
                "type": "aoe_attack",
                "damage": 30
            },
            {
                "name": "Charge",
                "type": "status",
                "effect": "stun",
                "potency": 1,
                "duration": 1
            }
        ],
        loot={
            "essence_min": 500,
            "essence_max": 800,
            "guaranteed": ["frost_mace", "frost_essence"]
        }
    )
    world.add_npc(vordt)
    
    ashen_lord = NPC(
        id="ashen_lord",
        name="The Ashen Lord",
        description="A tall figure wreathed in embers and ash, with a crown of flames.",
        friendly=False,
        health=400,
        attack=30,
        defense=15,
        special_abilities=[
            {
                "name": "Flame Eruption",
                "type": "aoe_attack",
                "damage": 35
            },
            {
                "name": "Ember Restoration",
                "type": "heal",
                "amount": 50
            }
        ],
        loot={
            "essence_min": 700,
            "essence_max": 1000,
            "guaranteed": ["ember_blade", "ashen_key"]
        }
    )
    world.add_npc(ashen_lord)
    
    king_morgaeth = NPC(
        id="king_morgaeth",
        name="King Morgaeth, the Hollow Crown",
        description="Once a proud king, now a hollow shell of madness in royal garb.",
        friendly=False,
        health=500,
        attack=35,
        defense=25,
        special_abilities=[
            {
                "name": "Decree of Death",
                "type": "aoe_attack",
                "damage": 40
            },
            {
                "name": "Summon Knights",
                "type": "summon",
                "entity": "hollow_soldier",
                "count": 2
            }
        ],
        loot={
            "essence_min": 1000,
            "essence_max": 1500,
            "guaranteed": ["ashen_key", "royal_seal"]
        }
    )
    world.add_npc(king_morgaeth)

def initialize_locations(world):
    """Initialize all locations in the game."""
    # Starting area
    firelink = Location(
        id="firelink_shrine",
        name="Firelink Shrine",
        description="A dilapidated shrine centered around a bonfire. The flames provide comfort in this bleak world.",
        is_beacon=True,
        region="Shrine Grounds",
        connections={
            "north": "high_wall",
            "east": "cemetery"
        },
        npcs=["blacksmith_andre"],
        ascii_art="""
             /\\
            /  \\
           /    \\
          /      \\
         /   ^   \\
        /__________\\
        |  SHRINE  |
        |__________|
        """
    )
    world.add_location(firelink)
    
    high_wall = Location(
        id="high_wall",
        name="High Wall of Lothric",
        description="A massive stone wall that protected the kingdom in better days. Now patrolled by hollow soldiers.",
        region="Shrine Grounds",
        connections={
            "south": "firelink_shrine",
            "north": "undead_settlement",
            "east": "lothric_castle"
        },
        enemies=["hollow_soldier"],
        is_beacon=True
    )
    world.add_location(high_wall)
    
    cemetery = Location(
        id="cemetery",
        name="Untended Graves",
        description="A forgotten cemetery shrouded in perpetual twilight. The graves seem to watch you.",
        region="Shrine Grounds",
        connections={
            "west": "firelink_shrine",
            "north": "cathedral"
        },
        enemies=["hollow_soldier"],
        is_beacon=True
    )
    world.add_location(cemetery)
    
    undead_settlement = Location(
        id="undead_settlement",
        name="Undead Settlement",
        description="A decrepit village where the undead were once corralled. Now abandoned to rot.",
        region="Outer Lands",
        connections={
            "south": "high_wall",
            "east": "road_of_sacrifices",
            "west": "blighted_marshes"
        },
        npcs=["merchant_ulrich"],
        is_shop=True,
        is_beacon=True
    )
    world.add_location(undead_settlement)
    
    cathedral = Location(
        id="cathedral",
        name="Cathedral of the Deep",
        description="A grand cathedral corrupted by dark forces. Its bell tower looms ominously.",
        region="Outer Lands",
        connections={
            "south": "cemetery",
            "west": "road_of_sacrifices"
        },
        enemies=["hollow_soldier"],
        is_beacon=True
    )
    world.add_location(cathedral)
    
    road_of_sacrifices = Location(
        id="road_of_sacrifices",
        name="Road of Sacrifices",
        description="A grim path where sacrifices were led to the Cathedral. The road is lined with cages and crosses.",
        region="Outer Lands",
        connections={
            "west": "undead_settlement",
            "east": "cathedral",
            "north": "farron_keep"
        },
        enemies=["hollow_soldier"],
        is_beacon=True
    )
    world.add_location(road_of_sacrifices)
    
    blighted_marshes = Location(
        id="blighted_marshes",
        name="Blighted Marshes",
        description="A poisonous swamp where nothing grows but twisted vegetation. The air is thick with miasma.",
        region="Outer Lands",
        connections={
            "east": "undead_settlement"
        },
        enemies=["hollow_soldier"],
        items=[world.get_item_by_id("blue_signet")],
        is_beacon=True
    )
    world.add_location(blighted_marshes)
    
    farron_keep = Location(
        id="farron_keep",
        name="Farron Keep",
        description="A crumbling fortress overtaken by the swamp. Once home to the Abyss Watchers.",
        region="Ashen Woods",
        connections={
            "south": "road_of_sacrifices",
            "north": "ashen_woods"
        },
        enemies=["hollow_soldier", "forest_guardian"],
        is_beacon=True
    )
    world.add_location(farron_keep)
    
    ashen_woods = Location(
        id="ashen_woods",
        name="Ashen Woods",
        description="A forest perpetually burning yet never consumed. The trees glow with ember essence.",
        region="Ashen Woods",
        connections={
            "south": "farron_keep",
            "north": "ashen_lord_arena"
        },
        enemies=["forest_guardian"],
        items=[world.get_item_by_id("ember_essence")],
        is_beacon=True
    )
    world.add_location(ashen_woods)
    
    ashen_lord_arena = Location(
        id="ashen_lord_arena",
        name="Kiln of the First Flame",
        description="The heart of the Ashen Woods, where the Ashen Lord rules from his throne of cinders.",
        region="Ashen Woods",
        connections={
            "south": "ashen_woods"
        },
        is_boss_area=True,
        enemies=["ashen_lord"]
    )
    world.add_location(ashen_lord_arena)
    
    lothric_castle = Location(
        id="lothric_castle",
        name="Lothric Castle",
        description="The once-proud castle of the royal family, now a shell of its former glory.",
        region="Northern Realm",
        connections={
            "west": "high_wall",
            "north": "vordt_arena"
        },
        enemies=["hollow_soldier"],
        visit_requirement={"quest_complete": "frost_guardian"},
        is_beacon=True
    )
    world.add_location(lothric_castle)
    
    vordt_arena = Location(
        id="vordt_arena",
        name="Vordt's Chamber",
        description="A grand hall covered in frost. The air is freezing and visibility is poor due to the mist.",
        region="Northern Realm",
        connections={
            "south": "lothric_castle",
            "north": "irithyll"
        },
        is_boss_area=True,
        enemies=["vordt"]
    )
    world.add_location(vordt_arena)
    
    irithyll = Location(
        id="irithyll",
        name="Irithyll of the Boreal Valley",
        description="A hauntingly beautiful city bathed in moonlight and covered in frost.",
        region="Northern Realm",
        connections={
            "south": "vordt_arena",
            "north": "anor_londo"
        },
        enemies=["hollow_soldier"],
        is_beacon=True,
        visit_requirement={"item": "frost_essence"}
    )
    world.add_location(irithyll)
    
    anor_londo = Location(
        id="anor_londo",
        name="Anor Londo",
        description="The legendary city of the gods, now abandoned and frozen in time.",
        region="Northern Realm",
        connections={
            "south": "irithyll",
            "east": "kings_chamber"
        },
        enemies=["hollow_soldier"],
        is_beacon=True
    )
    world.add_location(anor_londo)
    
    kings_chamber = Location(
        id="kings_chamber",
        name="King's Chamber",
        description="The throne room where King Morgaeth sits, driven mad by the fading of the flame.",
        region="Northern Realm",
        connections={
            "west": "anor_londo"
        },
        is_boss_area=True,
        enemies=["king_morgaeth"],
        visit_requirement={"item": "ashen_key"}
    )
    world.add_location(kings_chamber)

def initialize_quests(world):
    """Initialize all quests in the game."""
    # Basic quests
    ember_quest = Quest(
        id="ember_quest",
        name="The Smith's Request",
        description="Andre needs ember essence from the Ashen Woods to rekindle his forge.",
        objectives=[
            {"type": "item", "target": "ember_essence", "quantity": 1}
        ],
        rewards={
            "item": "ember_blade",
            "essence": 200
        }
    )
    world.add_quest(ember_quest)
    
    signet_quest = Quest(
        id="signet_quest",
        name="The Merchant's Signet",
        description="Find Ulrich's missing signet ring in the Blighted Marshes.",
        objectives=[
            {"type": "item", "target": "blue_signet", "quantity": 1}
        ],
        rewards={
            "item": "strength_tonic",
            "essence": 300
        }
    )
    world.add_quest(signet_quest)
    
    frost_guardian = Quest(
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
    world.add_quest(frost_guardian)
    
    ashen_heart = Quest(
        id="ashen_heart",
        name="Heart of the Ashen Woods",
        description="Confront the Ashen Lord in his domain and decide the fate of the burning forest.",
        objectives=[
            {"type": "kill", "target": "ashen_lord", "quantity": 1}
        ],
        rewards={
            "item": "ashen_key",
            "essence": 800
        }
    )
    world.add_quest(ashen_heart)
    
    kings_fall = Quest(
        id="kings_fall",
        name="The Hollowed Crown",
        description="Discover the fate of King Morgaeth and put an end to his suffering.",
        objectives=[
            {"type": "kill", "target": "king_morgaeth", "quantity": 1}
        ],
        rewards={
            "essence": 1500,
            "experience": 2000
        }
    )
    world.add_quest(kings_fall)

def create_player(name: str) -> Player:
    """Create a new player character."""
    player = Player(name=name)
    
    # Create inventory
    player.inventory = Inventory()
    
    # Add starting items
    starting_weapon = Weapon(
        id="broken_sword",
        name="Broken Sword",
        description="A damaged sword with limited effectiveness.",
        damage=10,
        attack_speed=1.0,
        weapon_type="sword",
        value=50,
        weight=2.0,
        durability=50,
        stamina_cost=10
    )
    player.inventory.add_item(starting_weapon)
    player.inventory.equip_item(starting_weapon)
    
    estus_flask = Consumable(
        id="estus_flask",
        name="Estus Flask",
        description="A mysterious flask that restores health. Refills at beacons.",
        effect_type="heal",
        effect_value=50,
        value=0,
        weight=0.5,
        stats={"healing": 50}
    )
    player.inventory.add_item(estus_flask)
    
    player.inventory.add_item(Consumable(
        id="stamina_elixir",
        name="Stamina Elixir",
        description="A green elixir that restores stamina.",
        effect_type="stamina",
        effect_value=40,
        value=80,
        weight=0.5,
        stats={"stamina": 40}
    ))
    
    return player

def initialize_maps(world):
    """Initialize ASCII art maps for all regions in the game."""
    # Define the Shrine Grounds region map
    firelink_map = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                         ┃
┃       Undead Asylum                     ┃
┃            □                            ┃
┃            ┃                            ┃
┃            ┃                            ┃
┃            ┃                            ┃
┃            ┃         High Wall          ┃
┃            ┗━━━━━━━━━□━━━━━━━━━━━━┓     ┃
┃                      ┃            ┃     ┃
┃                      ┃            ┃     ┃
┃      Cemetery        ┃            ┃     ┃
┃      of Ash          ┃            ┃     ┃
┃         □━━━━━━━━━━━━╋━━━━━━━━━━━━┫     ┃
┃         ┃            ┃            ┃     ┃
┃         ┃     FIRELINK SHRINE     ┃     ┃
┃    Bell ┃           □             ┃     ┃
┃    Tower┃           ┃             ┃     ┃
┃      □━━╋━━━━━━━━━━━┛             ┃     ┃
┃         ┃                         ┃     ┃
┃         ┃                         ┃     ┃
┃     New Londo                     ┃     ┃
┃     Ruins □                       ┃     ┃
┃                                   ┃     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━┛
"""
    
    # Define the Ashen Woods region map
    ashen_woods_map = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                         ┃
┃      Ashen Lord Arena                   ┃
┃        □                                ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃     Witch's             Giant's         ┃
┃     Cottage             Clearing        ┃
┃        □━━━━━━━━━━━━━━━━□               ┃
┃        ┃                ┃               ┃
┃        ┃                ┃               ┃
┃        ┃                ┃               ┃
┃        ┃      Ashen     ┃               ┃
┃     Forgotten         Woods             ┃
┃     Graves  □━━━━━━━━━━□                ┃
┃        □━━━━┛                           ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃      Farron Keep                        ┃
┃        □                                ┃
┃        ┃                                ┃
┗━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
    
    # Define the Northern Realm region map
    northern_realm_map = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                         ┃
┃      King's Chamber                     ┃
┃        □                                ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃     Anor Londo                          ┃
┃        □━━━━━━━━━━                      ┃
┃        ┃          ┃                     ┃
┃        ┃          ┃                     ┃
┃        ┃          ┃                     ┃
┃        ┃          ┃                     ┃
┃        ┃          ┃                     ┃
┃        ┃      Irithyll                  ┃
┃        ┣━━━━━━━━━□                      ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃     Vordt's Chamber                     ┃
┃        □                                ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃     Lothric Castle                      ┃
┃        □                                ┃
┃        ┃                                ┃
┗━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
    
    # Define the Outer Lands region map
    outer_lands_map = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                         ┃
┃      Farron Keep                        ┃
┃        □                                ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃        ┃       ≈≈≈≈≈≈≈≈≈≈≈≈             ┃
┃        ┃       ≈         ≈              ┃
┃        ┃       ≈         ≈              ┃
┃        ┃       ≈         ≈              ┃
┃        ┃       ≈≈≈≈≈≈≈≈≈≈               ┃
┃        ┃                                ┃
┃     Blighted            Cathedral       ┃
┃     Marshes             of the Deep     ┃
┃        □━━━━━━━━━━━━━━━━□               ┃
┃                  ┃      ┃               ┃
┃                  ┃      ┃               ┃
┃            Road of      ┃               ┃
┃            Sacrifices   ┃               ┃
┃                  □━━━━━━┛               ┃
┃                  ┃                      ┃
┃                  ┃                      ┃
┃      Undead Settlement                  ┃
┃        □                                ┃
┃        ┃                                ┃
┃        ┃                                ┃
┃     High Wall of Lothric                ┃
┃        □                                ┃
┃        ┃                                ┃
┗━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
    
    # Define the world map
    world_map = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                           ┃
┃                            NORTHERN REALM                                 ┃
┃                             King's Chamber                                ┃
┃                                  □                                        ┃
┃                                  │                                        ┃
┃                              Anor Londo                                   ┃
┃                                  □                                        ┃
┃                                  │                                        ┃
┃                               Irithyll                                    ┃
┃                                  □                                        ┃
┃                                  │                                        ┃
┃                             Vordt's Chamber                               ┃
┃                                  □                                        ┃
┃                                  │                                        ┃
┃                             Lothric Castle                                ┃
┃                                  □                                        ┃
┃                                  │                                        ┃
┃                    ┏━━━━━━━━━━━━━┻━━━━━━━━━━━━━━┓                        ┃
┃                    │                            │                        ┃
┃                    │                            │                        ┃
┃                ASHEN WOODS                  OUTER LANDS                  ┃
┃                 Ashen Lord                    Farron Keep                ┃
┃                     □                             □                       ┃
┃                     │                             │                       ┃
┃                 Ashen Woods                       │                       ┃
┃                     □                             │                       ┃
┃                     │                             │                       ┃
┃                 Farron Keep                       ┣━━━━━━━┓               ┃
┃                     □━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛       │               ┃
┃                                                           │               ┃
┃                                                     Cathedral             ┃
┃                                                       □                   ┃
┃                                                       │                   ┃
┃                                                       │                   ┃
┃                                   Road of             │                   ┃
┃                  Blighted         Sacrifices          │                   ┃
┃                  Marshes              □━━━━━━━━━━━━━━━┛                   ┃
┃                     □━━━━━━━━━━━━━━━━━┛                                   ┃
┃                                       │                                   ┃
┃                               Undead Settlement                          ┃
┃                                     □                                    ┃
┃                                     │                                    ┃
┃                               High Wall                                  ┃
┃                                     □                                    ┃
┃                            ┏━━━━━━━━┻━━━━━━━━━┓                          ┃
┃                    Cemetery │                 │                          ┃
┃                        □━━━━┛                 │                          ┃
┃                                               │                          ┃
┃                             FIRELINK SHRINE   │                          ┃
┃                                   □           │                          ┃
┃                                   SHRINE GROUNDS                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""
    
    # Add maps to the world
    world.region_maps = {
        'Shrine Grounds': firelink_map,
        'Ashen Woods': ashen_woods_map,
        'Northern Realm': northern_realm_map,
        'Outer Lands': outer_lands_map,
        'world': world_map
    } 