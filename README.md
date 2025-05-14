# Ardenvale

A text-based fantasy RPG inspired by Dark Souls 3. Explore a dark fantasy world, battle formidable enemies, complete quests, and discover the lore of a realm shattered by a fading flame.

## Table of Contents
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Game Features](#game-features)
- [Game World](#game-world)
- [Game Mechanics](#game-mechanics)
- [Combat System](#combat-system)
- [Beacon System](#beacon-system)
- [Character Development](#character-development)
- [Items and Equipment](#items-and-equipment)
- [NPCs and Dialogue](#npcs-and-dialogue)
- [Command Reference](#command-reference)
- [Tips for Beginners](#tips-for-beginners)
- [Technical Information](#technical-information)
- [Credits](#credits)

## Installation

### Requirements
- Python 3.6 or higher
- No additional packages required (uses standard library)

### Steps
1. Clone this repository:
   ```
   git clone https://github.com/101shaan/Arvendale
   ```
2. Navigate to the directory:
   ```
   cd Arvendale
   ```
3. Run the game:
   ```
   python main.py
   ```

## Getting Started

When you start the game, you'll be presented with the main menu where you can:
- Start a new game
- Load a saved game
- View credits
- Quit the game

If starting a new game, you'll be asked to name your character. After that, you'll begin your journey in Firelink Shrine, the central hub of Ardenvale.

## Game Features

- **Rich Interactive World**: Explore over 15 unique locations across 4 distinct regions
- **Immersive Combat**: Strategic combat system with timing mechanics, stances, and special abilities
- **Quest System**: Complete quests for rewards and to uncover the world's lore
- **Item System**: Collect, equip, and use various weapons, armor, and consumables
- **NPC Interaction**: Engage with characters through branching dialogue trees
- **Beacon System**: Unlock fast travel points protected by powerful guardians
- **Save/Load**: Save your progress and continue your adventure anytime
- **ASCII Visualization**: Detailed ASCII art maps and character visuals
- **Character Progression**: Level up your character and improve your stats
- **Merchant System**: Buy and sell items from vendors across the world

## Game World

Ardenvale is divided into four major regions:

1. **Shrine Grounds**: The starting area centered around Firelink Shrine, including:
   - Firelink Shrine - Central hub of the game
   - High Wall of Lothric - Ancient ramparts guarding the kingdom
   - Untended Graves - A forgotten cemetery shrouded in twilight

2. **Outer Lands**: A collection of disconnected territories, including:
   - Undead Settlement - A decrepit village where the undead were once corralled
   - Cathedral of the Deep - A grand cathedral corrupted by dark forces
   - Blighted Marshes - A poisonous swamp with valuable treasures

3. **Ashen Woods**: A forest perpetually burning yet never consumed, including:
   - Farron Keep - A crumbling fortress overtaken by the swamp
   - Ashen Woods - Trees glowing with ember essence
   - Kiln of the First Flame - Where the Ashen Lord rules

4. **Northern Realm**: The frozen territories beyond Lothric, including:
   - Lothric Castle - The once-proud castle of the royal family
   - Irithyll of the Boreal Valley - A hauntingly beautiful frost-covered city
   - Anor Londo - The legendary city of the gods

## Game Mechanics

### Character Stats
- **Health**: Determines how much damage you can take before dying
- **Stamina**: Required for attacks, dodges, and special moves
- **Strength**: Increases physical attack damage
- **Dexterity**: Improves attack speed and dodge chance
- **Intelligence**: Enhances magic effectiveness and dialogue options

### Experience and Leveling
- Defeat enemies to gain experience points
- Level up to increase your stats and become more powerful
- Higher levels unlock more powerful equipment and areas

### Essence
Essence is the currency in Ardenvale. It can be used for:
- Purchasing items from merchants
- Repairing damaged equipment
- Unlocking certain dialogues or areas
- Upgrading equipment (at blacksmiths)

You drop all your essence when you die, but can recover it by returning to where you died.

## Combat System

Combat in Ardenvale is turn-based with strategic elements:

### Basic Combat Actions
- **Attack**: Basic attack with equipped weapon
- **Special Moves**:
  - **Parry**: Timing-based counter that stuns enemies and allows counter-attacks
  - **Charged Attack**: High damage but leaves you vulnerable
  - **Dodge**: Avoid an enemy's attack completely if successful
- **Combat Stances**:
  - **Neutral**: Balanced offense and defense
  - **Aggressive**: Increased damage but lower defense
  - **Defensive**: Better protection but reduced damage output
- **Items**: Use consumables like health potions during combat
- **Flee**: Attempt to escape combat (success based on Dexterity)

### Combat Mechanics
- **Stamina Management**: Attacks and special moves consume stamina
- **Combo System**: Chain attacks for increased damage
- **Critical Hits**: Random chance based on weapon and dexterity
- **Enemy Abilities**: Bosses and special enemies have unique abilities

## Beacon System

Beacons are special locations that function as checkpoints and fast travel points:

### Beacon States
- **Protected (🛡️)**: Guarded by a Protector Illuminator that must be defeated
- **Unlocked (🔥)**: Available for resting and fast travel
- **Home Beacon (🏠)**: The last beacon where you rested

### Beacon Functions
- **Rest**: Restore health and stamina
- **Fast Travel**: Travel between unlocked beacons
- **Respawn Point**: Return here when you die

### Protector Illuminators
Each beacon is initially guarded by a Protector Illuminator:
- Their strength scales with your level
- Defeat them to unlock the beacon
- They possess unique abilities like Flame Shield and Light Burst

## Character Development

### Leveling
- Each level requires progressively more experience
- Leveling up increases your health and stamina
- Each level makes you more formidable in combat

### Skills and Abilities
- Unlock special abilities as you progress
- Learn new combat techniques from NPCs
- Discover hidden techniques in the world

### Equipment Progression
- Start with basic equipment
- Find and purchase better gear
- Unique weapons have special abilities

## Items and Equipment

### Item Types
- **Weapons**: Swords, maces, daggers with different attack styles
- **Armor**: Head, chest, and leg protection with various resistances
- **Consumables**: Potions, elixirs, and buff items
- **Key Items**: Quest-related and progression items

### Equipment Attributes
- **Damage/Defense**: Base protection or attack power
- **Durability**: Equipment degrades with use
- **Special Effects**: Unique properties like fire damage or status effects
- **Weight**: Affects movement and stamina consumption

### Inventory Management
- Limited inventory space (20 slots by default)
- Stackable consumable items
- Equipment can be sold to merchants for essence

## NPCs and Dialogue

### NPC Types
- **Merchants**: Buy and sell items
- **Quest Givers**: Provide tasks and rewards
- **Lore Characters**: Reveal world history and secrets
- **Enemies**: Hostile characters you must defeat

### Dialogue System
- Branching conversations based on choices
- Dialogue affected by your character's progression
- Hidden dialogue options based on items or knowledge
- Relationship system with certain NPCs

## Command Reference

- `look`: Examine your surroundings
- `go [direction]`: Travel north, south, east, or west
- `talk [character]`: Speak with an NPC
- `take [item]`: Pick up an item from your location
- `inventory`: View your items
- `equip [item]`: Equip a weapon or armor piece
- `use [item]`: Use a consumable item
- `status`: View your character stats
- `quests`: Check your active quests
- `map`: View the world map with your current location
- `rest`: Rest at a beacon to restore health and stamina
- `save`: Save your game progress
- `help`: Display available commands
- `quit`: Exit the game

## Tips for Beginners

1. **Talk to Everyone**: NPCs provide valuable information and quests
2. **Rest at Beacons**: Unlocking beacons provides fast travel and recovery points
3. **Manage Your Stamina**: Running out of stamina in combat can be deadly
4. **Learn Enemy Patterns**: Each enemy type has distinct attack patterns
5. **Upgrade Equipment**: Better gear makes combat much easier
6. **Save Frequently**: Use the save command often to avoid losing progress
7. **Explore Thoroughly**: Hidden items can be found in most locations
8. **Practice Parrying**: Mastering parry timing is rewarded with powerful counters
9. **Collect Essence**: Save essence for important purchases and upgrades
10. **Watch Your Health**: Heal when your health gets low to avoid death

## Technical Information

### Game Architecture
The game is organized into several modules for maintainability:

- `main.py`: Entry point to start the game
- `config.py`: Game constants and ASCII art
- `utils.py`: Utility functions for the game
- `models.py`: Core item and inventory classes
- `models_part2.py`: Player, NPC, and Location classes
- `models_part3.py`: World and Quest classes
- `game_systems.py`: Combat, UI, and Quest systems
- `game_data.py`: Game data initialization
- `game_engine.py`: Main game loop and command processing

### Save System
- Games are saved in the `saves` directory
- Automatic saving occurs every 10 turns
- Manual saving is available through the `save` command
- Save files store your character, inventory, progress, and world state

### Developer Notes
- The codebase is designed to be modular and expandable
- New locations, items, NPCs, and quests can be added in `game_data.py`
- Combat mechanics can be adjusted in `game_systems.py`

## Credits

- **Design & Development**: Shaan
- **Inspiration**: Dark Souls series
- **Special Thanks**: To all playtesters and the community

Enjoy your journey through the shattered realm of Ardenvale! 
