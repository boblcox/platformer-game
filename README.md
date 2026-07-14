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
