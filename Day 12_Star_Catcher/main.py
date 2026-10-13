
import json
import random
from pathlib import Path

import pygame

# ---------- Configuration ----------
WIDTH, HEIGHT = 900, 650
FPS = 60
BG = (18, 18, 38)
WHITE = (245, 245, 255)
PURPLE = (150, 100, 255)
YELLOW = (255, 210, 65)
RED = (255, 80, 100)
CYAN = (80, 220, 255)
GREEN = (90, 230, 160)

BASE_DIR = Path(__file__).resolve().parent
HIGH_SCORE_FILE = BASE_DIR / "highscore.json"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Star Catcher | Day 12")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 25, bold=True)
SMALL = pygame.font.SysFont("Arial", 18)
TITLE = pygame.font.SysFont("Arial", 58, bold=True)


def load_high_score():
    try:
        data = json.loads(HIGH_SCORE_FILE.read_text())
        return max(0, int(data.get("best", 0)))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def save_high_score(score):
    try:
        HIGH_SCORE_FILE.write_text(json.dumps({"best": score}, indent=2))
    except OSError:
        pass


def text(message, font, color, x, y, center=True):
    image = font.render(message, True, color)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(image, rect)


def draw_star(x, y, radius, color):
    points = []
    for i in range(10):
        angle = -pygame.math.Vector2(0, 1).angle_to(
            pygame.math.Vector2(1, 0)
        ) if False else -90 + i * 36
        r = radius if i % 2 == 0 else radius * 0.45
        import math
        rad = math.radians(angle)
        points.append((x + r * math.cos(rad), y + r * math.sin(rad)))
    pygame.draw.polygon(screen, color, points)


def make_object(level):
    is_bomb = random.random() < min(0.20 + level * 0.025, 0.40)
    return {
        "x": random.randint(25, WIDTH - 25),
        "y": -30,
        "speed": random.uniform(2.2, 3.7) + level * 0.35,
        "radius": random.randint(13, 20),
        "type": "bomb" if is_bomb else "star",
    }


def new_game():
    return {
        "basket_x": WIDTH // 2,
        "score": 0,
        "lives": 3,
        "objects": [],
        "spawn_timer": 0,
        "level": 1,
        "state": "playing",
    }


def draw_basket(x, y):
    # Basket body
    points = [(x - 45, y - 18), (x + 45, y - 18),
              (x + 32, y + 20), (x - 32, y + 20)]
    pygame.draw.polygon(screen, PURPLE, points)
    pygame.draw.lines(screen, WHITE, True, points, 3)
    pygame.draw.line(screen, CYAN, (x - 40, y - 23),
                     (x + 40, y - 23), 5)


def draw_background():
    screen.fill(BG)
    # Decorative stars
    for x, y, r in background_stars:
        pygame.draw.circle(screen, (65, 65, 105), (x, y), r)


random.seed()
background_stars = [
    (random.randrange(WIDTH), random.randrange(HEIGHT),
     random.choice([1, 2]))
    for _ in range(85)
]

best_score = load_high_score()
game = new_game()
running = True

while running:
    dt = clock.tick(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if game["state"] == "start":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game = new_game()

            elif game["state"] == "playing":
                if event.key == pygame.K_p:
                    game["state"] = "paused"

            elif game["state"] == "paused":
                if event.key in (pygame.K_p, pygame.K_RETURN):
                    game["state"] = "playing"
                elif event.key == pygame.K_q:
                    game["state"] = "start"

            elif game["state"] == "gameover":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game = new_game()
                elif event.key == pygame.K_q:
                    game["state"] = "start"

    draw_background()

    if game["state"] == "start":
        text("STAR CATCHER", TITLE, YELLOW, WIDTH // 2, 190)
        text("Catch stars. Dodge bombs. Beat your best!", FONT,
             WHITE, WIDTH // 2, 270)
        text("Move: LEFT / RIGHT or A / D", SMALL, CYAN,
             WIDTH // 2, 340)
        text("Pause: P     Quit: ESC", SMALL, WHITE,
             WIDTH // 2, 375)
        text("Press ENTER to play", FONT, GREEN,
             WIDTH // 2, 450)
        text(f"Best score: {best_score}", SMALL, YELLOW,
             WIDTH // 2, 500)

    elif game["state"] in ("playing", "paused", "gameover"):
        if game["state"] == "playing":
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                game["basket_x"] -= 7
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                game["basket_x"] += 7

            game["basket_x"] = max(
                48, min(WIDTH - 48, game["basket_x"])
            )

            game["spawn_timer"] += dt
            spawn_delay = max(260, 750 - game["level"] * 35)

            if game["spawn_timer"] >= spawn_delay:
                game["objects"].append(make_object(game["level"]))
                game["spawn_timer"] = 0

            basket_rect = pygame.Rect(
                game["basket_x"] - 43, HEIGHT - 82, 86, 45
            )

            for obj in game["objects"][:]:
                obj["y"] += obj["speed"]

                object_rect = pygame.Rect(
                    obj["x"] - obj["radius"],
                    obj["y"] - obj["radius"],
                    obj["radius"] * 2,
                    obj["radius"] * 2,
                )

                if basket_rect.colliderect(object_rect):
                    if obj["type"] == "star":
                        game["score"] += 10
                        game["level"] = 1 + game["score"] // 100
                    else:
                        game["lives"] -= 1

                    game["objects"].remove(obj)

                elif obj["y"] > HEIGHT + 25:
                    game["objects"].remove(obj)

        # Draw falling objects
        for obj in game["objects"]:
            if obj["type"] == "star":
                draw_star(obj["x"], int(obj["y"]),
                          obj["radius"], YELLOW)
            else:
                pygame.draw.circle(
                    screen, RED,
                    (obj["x"], int(obj["y"])), obj["radius"]
                )
                pygame.draw.circle(
                    screen, WHITE,
                    (obj["x"] - 4, int(obj["y"]) - 4), 3
                )

        draw_basket(game["basket_x"], HEIGHT - 62)

        text(f"Score: {game['score']}", FONT, WHITE, 22, 18, False)
        text(f"Lives: {game['lives']}", FONT, RED, 22, 53, False)
        text(f"Level: {game['level']}", FONT, CYAN, 22, 88, False)
        text(f"Best: {max(best_score, game['score'])}",
             FONT, YELLOW, WIDTH - 170, 18, False)

        if game["state"] == "playing" and game["lives"] <= 0:
            game["state"] = "gameover"
            best_score = max(best_score, game["score"])
            save_high_score(best_score)

        if game["state"] == "paused":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 175))
            screen.blit(overlay, (0, 0))
            text("PAUSED", TITLE, YELLOW, WIDTH // 2, 270)
            text("Press P or ENTER to resume", FONT,
                 WHITE, WIDTH // 2, 350)
            text("Press Q to return to menu", SMALL,
                 CYAN, WIDTH // 2, 395)

        if game["state"] == "gameover":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 185))
            screen.blit(overlay, (0, 0))
            text("GAME OVER", TITLE, RED, WIDTH // 2, 230)
            text(f"Your score: {game['score']}", FONT,
                 WHITE, WIDTH // 2, 315)
            text(f"Best score: {best_score}", FONT,
                 YELLOW, WIDTH // 2, 360)
            text("Press ENTER to play again", SMALL,
                 GREEN, WIDTH // 2, 425)
            text("Press Q for menu | ESC to quit", SMALL,
                 WHITE, WIDTH // 2, 465)

    pygame.display.flip()

pygame.quit()
