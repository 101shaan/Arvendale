# Ardenvale

A text-based fantasy RPG inspired by Dark Souls and Lord of the Rings. Explore a dark fantasy world, battle formidable enemies, complete quests, and discover the lore of a realm shattered by a fading flame.

## Features

- **Rich World**: Explore diverse locations across multiple regions
- **Combat System**: Strategic combat with timing mechanics, stances, and special moves
- **Quest System**: Complete quests for rewards and to uncover the world's lore
- **Item System**: Collect, equip, and use various weapons, armor, and consumables
- **NPC Dialogue**: Interact with characters through branching conversations
- **Save/Load**: Save your progress and continue your adventure later

## Game Structure

The game is organized into several modules for maintainability:

- `main.py`: Entry point to start the game
- `config.py`: Game constants and ASCII art
- `utils.py`: Utility functions for the game
- `models.py`, `models_part2.py`, `models_part3.py`: Core game classes
- `game_systems.py`: Combat, UI, and Quest systems
- `game_data.py`: Game data initialization
- `game_engine.py`: Main game loop and command processing

## How to Play

1. Run the game by executing:
   ```
   python main.py
   ```

2. Use text commands to control your character:
   - `look`: Examine your surroundings
   - `go [direction]`: Travel in a direction (north, south, east, west)
   - `talk [character]`: Speak with a character
   - `take [item]`: Pick up an item
   - `inventory`: Check your inventory
   - `equip [item]`: Equip an item
   - `use [item]`: Use an item
   - `status`: View your character stats
   - `quests`: View your active quests
   - `map`: View the world map
   - `rest`: Rest at a beacon to recover health and stamina
   - `save`: Save your game
   - `quit`: Exit the game

## Game Mechanics

### Combat
Combat is turn-based with timing mechanics. You can:
- Use basic attacks
- Execute special moves (parry, charged attack, dodge)
- Change your stance (neutral, aggressive, defensive)
- Use items
- Attempt to flee

### Progress
- Explore the world and discover new locations
- Defeat enemies to gain experience and level up
- Complete quests to earn rewards and advance the story
- Find beacons (checkpoints) to rest and restore health
- Collect essence (currency) to trade with merchants

### Death Mechanics
If you die, you'll respawn at the last beacon you rested at, but you'll drop your essence where you died. You can recover it by returning to that location.

## Tips for Beginners

1. Talk to NPCs to discover quests and lore
2. Rest at beacons frequently to save your progress
3. Upgrade your equipment whenever possible
4. Learn enemy attack patterns to time your parries
5. Explore thoroughly to find valuable items

Enjoy your journey through the shattered realm of Ardenvale! 