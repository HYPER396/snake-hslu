import pygame
import random
import sys

CELL = 40
COLS = 16
ROWS = 16
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 64
FPS = 10

BG        = (13,  15,  23)
GRID_DARK = (20,  23,  35)
GRID_LINE = (28,  32,  48)
HEAD      = (72,  224, 130)
BODY      = (40,  150,  80)
FOOD_OUT  = (255,  90,  90)
FOOD_IN   = (255, 170, 120)
DIM       = (160, 170, 200)
BRIGHT    = (220, 230, 250)
BAR       = (18,  20,  32)


def spawn_food(snake):
    occupied = set(snake)
    while True:
        p = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if p not in occupied:
            return p


def new_game():
    snake = [(COLS // 2, ROWS // 2), (COLS // 2 - 1, ROWS // 2)]
    return snake, (1, 0), 0, spawn_food(snake)


def draw_rounded_cell(surface, color, gx, gy, inset=2, radius=6):
    r = pygame.Rect(gx * CELL + inset, gy * CELL + inset, CELL - inset * 2, CELL - inset * 2)
    pygame.draw.rect(surface, color, r, border_radius=radius)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("monospace", 36, bold=True)
    font_info  = pygame.font.SysFont("monospace", 17)

    snake, direction, score, food = new_game()
    queued_dir = direction
    game_over  = False
    high_score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        snake, direction, score, food = new_game()
                        queued_dir = direction
                        game_over  = False
                else:
                    if event.key in (pygame.K_UP,    pygame.K_w) and direction != (0,  1):
                        queued_dir = (0, -1)
                    elif event.key in (pygame.K_DOWN,  pygame.K_s) and direction != (0, -1):
                        queued_dir = (0,  1)
                    elif event.key in (pygame.K_LEFT,  pygame.K_a) and direction != (1,  0):
                        queued_dir = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                        queued_dir = (1,  0)

        # --- update ---
        if not game_over:
            direction = queued_dir
            hx, hy   = snake[0][0] + direction[0], snake[0][1] + direction[1]

            if hx < 0 or hx >= COLS or hy < 0 or hy >= ROWS or (hx, hy) in snake:
                game_over  = True
                high_score = max(high_score, score)
            else:
                snake.insert(0, (hx, hy))
                if (hx, hy) == food:
                    score += 1
                    food   = spawn_food(snake)
                else:
                    snake.pop()

        # --- draw background ---
        screen.fill(BG)

        for gx in range(COLS):
            for gy in range(ROWS):
                pygame.draw.rect(screen, GRID_DARK,
                    (gx * CELL + 1, gy * CELL + 1, CELL - 2, CELL - 2),
                    border_radius=4)

        # subtle grid lines
        for i in range(COLS + 1):
            pygame.draw.line(screen, GRID_LINE, (i * CELL, 0), (i * CELL, ROWS * CELL))
        for j in range(ROWS + 1):
            pygame.draw.line(screen, GRID_LINE, (0, j * CELL), (WIDTH, j * CELL))

        # --- draw food ---
        fx = food[0] * CELL + CELL // 2
        fy = food[1] * CELL + CELL // 2
        pygame.draw.circle(screen, FOOD_OUT, (fx, fy), CELL // 2 - 2)
        pygame.draw.circle(screen, FOOD_IN,  (fx, fy), CELL // 2 - 6)

        # --- draw snake ---
        total = len(snake)
        for i, (gx, gy) in enumerate(snake):
            t     = i / max(total - 1, 1)
            r     = int(HEAD[0] + (BODY[0] - HEAD[0]) * t)
            g     = int(HEAD[1] + (BODY[1] - HEAD[1]) * t)
            b     = int(HEAD[2] + (BODY[2] - HEAD[2]) * t)
            color = (r, g, b)
            draw_rounded_cell(screen, color, gx, gy, inset=3 if i == 0 else 4, radius=7 if i == 0 else 5)

        # head eyes
        hgx, hgy = snake[0]
        ex, ey   = hgx * CELL + CELL // 2, hgy * CELL + CELL // 2
        dx, dy   = direction
        ox, oy   = -dy * 5, dx * 5   # perpendicular offset
        for sign in (+1, -1):
            ex2 = ex + dx * 4 + sign * ox
            ey2 = ey + dy * 4 + sign * oy
            pygame.draw.circle(screen, BG,    (ex2, ey2), 4)
            pygame.draw.circle(screen, BRIGHT,(ex2, ey2), 2)

        # --- score bar ---
        pygame.draw.rect(screen, BAR, (0, ROWS * CELL, WIDTH, 64))
        pygame.draw.line(screen, GRID_LINE, (0, ROWS * CELL), (WIDTH, ROWS * CELL))

        score_surf = font_info.render(f"SCORE  {score}", True, BRIGHT)
        best_surf  = font_info.render(f"BEST  {high_score}", True, DIM)
        keys_surf  = font_info.render("WASD / arrow keys", True, DIM)
        screen.blit(score_surf, (16,            ROWS * CELL + 22))
        screen.blit(best_surf,  (16 + 160,      ROWS * CELL + 22))
        screen.blit(keys_surf,  (WIDTH - keys_surf.get_width() - 16, ROWS * CELL + 22))

        # --- game over overlay ---
        if game_over:
            overlay = pygame.Surface((WIDTH, ROWS * CELL), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            go_surf  = font_title.render("GAME OVER", True, FOOD_OUT)
            sub_surf = font_info.render(f"Score: {score}     Press R to restart", True, DIM)
            screen.blit(go_surf,  (WIDTH // 2 - go_surf.get_width()  // 2, ROWS * CELL // 2 - 36))
            screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, ROWS * CELL // 2 + 18))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
