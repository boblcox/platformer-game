# Hex Fantasy Strategy Game

A comprehensive hex-based turn-based fantasy strategy game built with Python and Pygame.

## Hex Strategy Game Features

- **Hex Grid Map** – flat-top hexagonal grid (20×15) with five terrain types: Grass, Forest, Mountain, Water, Desert
- **Five Unit Types** – Warrior, Archer, Mage, Cavalry, Catapult, each with unique stats
- **Buildings** – Castle, Village, Barracks, Tower with gold income and recruitment
- **Combat System** – melee and ranged combat with terrain defence bonuses and damage variance
- **Resource Management** – gold income from buildings, upkeep costs for units
- **Fog of War** – dynamic visibility per player based on unit/building vision ranges
- **A\* Pathfinding** – optimal movement paths respecting terrain costs
- **AI Opponent** – AI attacks, pursues enemies, and recruits new units automatically
- **Camera** – pan with WASD/arrows, zoom with mouse scroll wheel
- **Procedural Sprites** – all 64×64 PNG sprites generated with Pillow

## Hex Game Setup

```bash
pip install -r requirements.txt
python hex_game.py
```

Sprites are auto-generated in `assets/sprites/` on first run via `game/sprite_gen.py`.

## Hex Game Controls

| Action | Input |
|--------|-------|
| Select unit / building | Left-click |
| Move / Attack | Right-click target |
| End turn | `E` |
| Recruit unit at castle | `R` |
| Deselect | `Esc` |
| Pan camera | `W A S D` or arrow keys |
| Zoom | Mouse scroll wheel |

## Hex Game Project Structure

```
platformer-game/
├── hex_game.py          # Hex strategy entry point
├── requirements.txt
├── assets/sprites/      # Auto-generated PNG sprites
└── game/
    ├── hex_grid.py      # Cube-coordinate hex grid
    ├── units.py         # Unit classes and types
    ├── buildings.py     # Building classes
    ├── map_gen.py       # Procedural map generation
    ├── combat.py        # Combat resolution
    ├── pathfinding.py   # A* pathfinding
    ├── fog_of_war.py    # Per-player fog of war
    ├── resources.py     # Gold / resource management
    ├── ai.py            # AI decision making
    ├── camera.py        # Viewport / camera system
    ├── renderer.py      # Pygame rendering
    ├── ui.py            # UI panel and buttons
    ├── game_state.py    # Central game state
    └── sprite_gen.py    # Programmatic sprite generation
```

---

# Platformer Adventure

A Python side-scrolling platformer with procedurally generated levels, built with Pygame.

## Features

- **Procedurally Generated Maps** – every level is unique with randomised platforms, gaps, enemies, weapon pickups, and an exit ladder
- **Player Character** – smooth physics, jumping, and collision detection; controllable via keyboard *or* mouse
- **Weapons System** – pick up and equip Fists, Dagger, Sword, Bow, and Fireball Staff, each with unique stats and attack behaviour
- **Enemy AI** – enemies patrol, chase, and attack using a state machine; difficulty scales with level
- **Ranged & Melee Combat** – melee weapons use a hitbox; ranged/magic weapons fire projectiles aimed at the mouse cursor
- **Level Progression** – reach the yellow exit ladder at the far end of the level to advance
- **Menu System** – main menu, pause menu (with save), game-over screen, and level-complete screen
- **Save / Load** – progress is persisted to `saves/game_save.json` and can be resumed at any time
- **Camera** – smooth camera that follows the player and clamps to the map bounds

## Controls

| Action | Keys / Mouse |
|--------|-------------|
| Move left / right | `A` / `D` or `←` / `→` |
| Jump | `W`, `↑`, or `Space` |
| Attack | Left mouse button or `Z` / `X` |
| Aim (ranged weapons) | Mouse cursor |
| Pause | `Esc` |

## Requirements

- Python 3.8+
- Pygame 2.0+

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Project Structure

```
platformer-game/
├── main.py              # Entry point
├── requirements.txt
├── saves/               # Save files (auto-created)
└── src/
    ├── settings.py      # All constants and configuration
    ├── camera.py        # Scrolling camera
    ├── map_generator.py # Procedural level generation
    ├── player.py        # Player physics, input, and combat
    ├── enemy.py         # Enemy AI (patrol / chase / attack)
    ├── sprites.py       # WeaponPickup, Projectile, Ladder sprites
    ├── ui.py            # Menus and HUD
    ├── save_load.py     # JSON save / load
    └── game.py          # Game state machine and main loop
```
