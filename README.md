# project1

A classic Tetris game built with Python and Pygame.

## Requirements

- Python 3.x
- Pygame

```bash
pip install pygame
```

## Running the Game

```bash
python tetris.py
```

## How to Play

Seven tetromino shapes (I, O, T, S, Z, J, L) fall one at a time onto a 10×20 grid. Move and rotate each piece to fill complete horizontal lines. When a line is full, it clears and you score points. The game ends when pieces stack up to the top of the board.

## Controls

| Key         | Action                        |
|-------------|-------------------------------|
| Left Arrow  | Move piece left               |
| Right Arrow | Move piece right              |
| Up Arrow    | Rotate piece                  |
| Down Arrow  | Soft drop (faster fall)       |
| Space       | Hard drop (instant to bottom) |
| P           | Pause / Resume                |
| R           | Restart game                  |

## Scoring

| Lines Cleared | Points (× level) |
|---------------|------------------|
| 1             | 100              |
| 2             | 300              |
| 3             | 500              |
| 4             | 800              |

- Soft drop grants 1 bonus point per row.
- Level increases every 10 lines cleared.
- Pieces fall faster each level (starts at 500 ms, minimum 80 ms).

## Features

- **Ghost piece** — preview where the current piece will land
- **Next piece preview** — see the upcoming tetromino
- **Wall kicks** — rotation attempts adjacent positions if blocked
