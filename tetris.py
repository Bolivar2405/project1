import pygame
import random
import sys

pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
COLORS = [
    (0, 240, 240),   # I - cyan
    (240, 240, 0),   # O - yellow
    (160, 0, 240),   # T - purple
    (0, 240, 0),     # S - green
    (240, 0, 0),     # Z - red
    (0, 0, 240),     # J - blue
    (240, 160, 0),   # L - orange
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],                          # I
    [[1, 1], [1, 1]],                        # O
    [[0, 1, 0], [1, 1, 1]],                  # T
    [[0, 1, 1], [1, 1, 0]],                  # S
    [[1, 1, 0], [0, 1, 1]],                  # Z
    [[1, 0, 0], [1, 1, 1]],                  # J
    [[0, 0, 1], [1, 1, 1]],                  # L
]

COLS = 10
ROWS = 20
CELL = 30
PANEL_W = 160

SCREEN_W = COLS * CELL + PANEL_W
SCREEN_H = ROWS * CELL

FALL_SPEED = 500      # ms per row
FAST_FALL = 50
MOVE_DELAY = 150
MOVE_REPEAT = 50


def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]


def valid(board, shape, ox, oy):
    for r, row in enumerate(shape):
        for c, cell in enumerate(row):
            if cell:
                nr, nc = oy + r, ox + c
                if nr < 0 or nr >= ROWS or nc < 0 or nc >= COLS:
                    return False
                if board[nr][nc]:
                    return False
    return True


def place(board, shape, ox, oy, color_idx):
    for r, row in enumerate(shape):
        for c, cell in enumerate(row):
            if cell:
                board[oy + r][ox + c] = color_idx


def clear_lines(board):
    full = [r for r in range(ROWS) if all(board[r])]
    for r in full:
        del board[r]
        board.insert(0, [0] * COLS)
    return len(full)


def draw_cell(surface, r, c, color_idx, ox=0, oy=0):
    color = COLORS[color_idx - 1]
    x = ox + c * CELL
    y = oy + r * CELL
    pygame.draw.rect(surface, color, (x + 1, y + 1, CELL - 2, CELL - 2))
    pygame.draw.rect(surface, tuple(min(v + 60, 255) for v in color), (x + 1, y + 1, CELL - 2, 4))
    pygame.draw.rect(surface, tuple(max(v - 60, 0) for v in color), (x + 1, y + CELL - 5, CELL - 2, 4))


def draw_board(surface, board):
    pygame.draw.rect(surface, DARK_GRAY, (0, 0, COLS * CELL, ROWS * CELL))
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]:
                draw_cell(surface, r, c, board[r][c])
            else:
                pygame.draw.rect(surface, (20, 20, 20), (c * CELL + 1, r * CELL + 1, CELL - 2, CELL - 2))


def draw_piece(surface, shape, ox, oy, color_idx, alpha=255):
    for r, row in enumerate(shape):
        for c, cell in enumerate(row):
            if cell:
                draw_cell(surface, r, c, color_idx, ox * CELL, oy * CELL)


def draw_ghost(surface, board, shape, ox, oy, color_idx):
    ghost_y = oy
    while valid(board, shape, ox, ghost_y + 1):
        ghost_y += 1
    if ghost_y == oy:
        return
    color = COLORS[color_idx - 1]
    ghost_color = tuple(max(v - 120, 20) for v in color)
    for r, row in enumerate(shape):
        for c, cell in enumerate(row):
            if cell:
                x = (ox + c) * CELL
                y = (ghost_y + r) * CELL
                pygame.draw.rect(surface, ghost_color, (x + 1, y + 1, CELL - 2, CELL - 2), 2)


def draw_panel(surface, score, level, lines, next_shape, next_color):
    px = COLS * CELL
    font_lg = pygame.font.SysFont("monospace", 20, bold=True)
    font_sm = pygame.font.SysFont("monospace", 16)

    pygame.draw.rect(surface, (20, 20, 40), (px, 0, PANEL_W, SCREEN_H))

    def label(text, y, font=font_sm, color=WHITE):
        surface.blit(font.render(text, True, color) if font == font_lg else font_sm.render(text, True, color), (px + 10, y))

    label("TETRIS", 10, font_lg, (0, 240, 240))
    label(f"SCORE", 50)
    label(f"{score}", 68, font_lg, (240, 240, 0))
    label(f"LEVEL", 100)
    label(f"{level}", 118, font_lg, (0, 240, 0))
    label(f"LINES", 150)
    label(f"{lines}", 168, font_lg, (240, 160, 0))

    label("NEXT", 210)
    pygame.draw.rect(surface, DARK_GRAY, (px + 10, 230, 130, 80))
    nw = len(next_shape[0])
    nh = len(next_shape)
    nx = px + 10 + (130 - nw * CELL) // 2
    ny = 230 + (80 - nh * CELL) // 2
    for r, row in enumerate(next_shape):
        for c, cell in enumerate(row):
            if cell:
                draw_cell(surface, 0, 0, next_color, nx + c * CELL, ny + r * CELL)

    label("CONTROLS", 330)
    for i, line in enumerate(["← → Move", "↑  Rotate", "↓  Soft drop", "Space Hard drop", "P  Pause", "R  Restart"]):
        surface.blit(pygame.font.SysFont("monospace", 13).render(line, True, GRAY), (px + 8, 350 + i * 18))


def new_piece():
    idx = random.randint(0, len(SHAPES) - 1)
    shape = SHAPES[idx]
    color = idx + 1
    ox = COLS // 2 - len(shape[0]) // 2
    return shape, color, ox, 0


def game_loop():
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    board = [[0] * COLS for _ in range(ROWS)]
    score = 0
    level = 1
    total_lines = 0
    paused = False
    game_over = False

    shape, color, ox, oy = new_piece()
    next_shape, next_color, _, _ = new_piece()

    fall_timer = 0
    move_timer = 0
    move_held = None

    LINE_SCORES = [0, 100, 300, 500, 800]

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r:
                    return  # restart
                if game_over:
                    continue
                if paused:
                    continue
                if event.key == pygame.K_UP:
                    rotated = rotate(shape)
                    if valid(board, rotated, ox, oy):
                        shape = rotated
                    elif valid(board, rotated, ox - 1, oy):
                        shape, ox = rotated, ox - 1
                    elif valid(board, rotated, ox + 1, oy):
                        shape, ox = rotated, ox + 1
                if event.key == pygame.K_SPACE:
                    while valid(board, shape, ox, oy + 1):
                        oy += 1
                    place(board, shape, ox, oy, color)
                    cleared = clear_lines(board)
                    total_lines += cleared
                    score += LINE_SCORES[cleared] * level
                    level = total_lines // 10 + 1
                    shape, color = next_shape, next_color
                    next_shape, next_color, _, _ = new_piece()
                    ox = COLS // 2 - len(shape[0]) // 2
                    oy = 0
                    if not valid(board, shape, ox, oy):
                        game_over = True
                if event.key == pygame.K_LEFT:
                    move_held = pygame.K_LEFT
                    move_timer = -MOVE_DELAY
                    if valid(board, shape, ox - 1, oy):
                        ox -= 1
                if event.key == pygame.K_RIGHT:
                    move_held = pygame.K_RIGHT
                    move_timer = -MOVE_DELAY
                    if valid(board, shape, ox + 1, oy):
                        ox += 1
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    move_held = None

        if paused or game_over:
            pass
        else:
            keys = pygame.key.get_pressed()
            fast = keys[pygame.K_DOWN]
            fall_interval = FAST_FALL if fast else max(FALL_SPEED - (level - 1) * 40, 80)

            fall_timer += dt
            if fall_timer >= fall_interval:
                fall_timer = 0
                if valid(board, shape, ox, oy + 1):
                    oy += 1
                else:
                    place(board, shape, ox, oy, color)
                    cleared = clear_lines(board)
                    total_lines += cleared
                    score += LINE_SCORES[cleared] * level
                    if fast:
                        score += 1
                    level = total_lines // 10 + 1
                    shape, color = next_shape, next_color
                    next_shape, next_color, _, _ = new_piece()
                    ox = COLS // 2 - len(shape[0]) // 2
                    oy = 0
                    if not valid(board, shape, ox, oy):
                        game_over = True

            if move_held:
                move_timer += dt
                if move_timer >= MOVE_REPEAT:
                    move_timer = 0
                    if move_held == pygame.K_LEFT and valid(board, shape, ox - 1, oy):
                        ox -= 1
                    elif move_held == pygame.K_RIGHT and valid(board, shape, ox + 1, oy):
                        ox += 1

        # Draw
        screen.fill(BLACK)
        draw_board(screen, board)

        if not game_over:
            draw_ghost(screen, board, shape, ox, oy, color)
            draw_piece(screen, shape, ox, oy, color)

        draw_panel(screen, score, level, total_lines, next_shape, next_color)

        # Grid lines
        for r in range(ROWS + 1):
            pygame.draw.line(screen, (30, 30, 30), (0, r * CELL), (COLS * CELL, r * CELL))
        for c in range(COLS + 1):
            pygame.draw.line(screen, (30, 30, 30), (c * CELL, 0), (c * CELL, ROWS * CELL))
        pygame.draw.rect(screen, GRAY, (0, 0, COLS * CELL, ROWS * CELL), 2)

        if paused:
            overlay = pygame.Surface((COLS * CELL, ROWS * CELL), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            font = pygame.font.SysFont("monospace", 36, bold=True)
            txt = font.render("PAUSED", True, WHITE)
            screen.blit(txt, (COLS * CELL // 2 - txt.get_width() // 2, ROWS * CELL // 2 - 20))

        if game_over:
            overlay = pygame.Surface((COLS * CELL, ROWS * CELL), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            font_big = pygame.font.SysFont("monospace", 32, bold=True)
            font_sm = pygame.font.SysFont("monospace", 18)
            t1 = font_big.render("GAME OVER", True, (240, 0, 0))
            t2 = font_sm.render(f"Score: {score}", True, WHITE)
            t3 = font_sm.render("R to restart", True, GRAY)
            cx = COLS * CELL // 2
            cy = ROWS * CELL // 2
            screen.blit(t1, (cx - t1.get_width() // 2, cy - 50))
            screen.blit(t2, (cx - t2.get_width() // 2, cy))
            screen.blit(t3, (cx - t3.get_width() // 2, cy + 30))

        pygame.display.flip()


def main():
    while True:
        game_loop()


if __name__ == "__main__":
    main()
