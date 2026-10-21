
import math
import random
import sys

import pygame

pygame.init()

# -------------------- Configuration --------------------

WIDTH, HEIGHT = 1180, 760
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AstroView | Interactive Solar System")

CLOCK = pygame.time.Clock()

BG = (7, 10, 25)
PANEL = (17, 24, 45)
BORDER = (47, 61, 91)
WHITE = (235, 240, 255)
MUTED = (153, 168, 197)
BLUE = (100, 175, 255)
GOLD = (255, 210, 100)
GREEN = (113, 220, 170)

FONT = pygame.font.SysFont("arial", 16)
SMALL = pygame.font.SysFont("arial", 13)
MEDIUM = pygame.font.SysFont("arial", 20, bold=True)
LARGE = pygame.font.SysFont("arial", 27, bold=True)
TITLE = pygame.font.SysFont("arial", 34, bold=True)

# The orbit sizes and planet sizes are illustrative,
# not to scale with actual astronomical measurements.

SUN = (WIDTH // 2 - 125, HEIGHT // 2 + 5)

PLANETS = [
    {
        "name": "Mercury",
        "orbit": 48,
        "radius": 5,
        "color": (175, 170, 164),
        "speed": 1.60,
        "distance": "57.9 million km",
        "diameter": "4,879 km",
        "day": "58.6 Earth days",
        "year": "88 Earth days",
        "fact": "The smallest planet, closest to the Sun.",
    },
    {
        "name": "Venus",
        "orbit": 79,
        "radius": 8,
        "color": (235, 190, 125),
        "speed": 1.20,
        "distance": "108.2 million km",
        "diameter": "12,104 km",
        "day": "243 Earth days",
        "year": "225 Earth days",
        "fact": "Its dense atmosphere makes it the hottest planet.",
    },
    {
        "name": "Earth",
        "orbit": 112,
        "radius": 9,
        "color": (70, 145, 255),
        "speed": 0.95,
        "distance": "149.6 million km",
        "diameter": "12,742 km",
        "day": "24 hours",
        "year": "365.25 days",
        "fact": "Our home planet is known to support life.",
    },
    {
        "name": "Mars",
        "orbit": 148,
        "radius": 7,
        "color": (226, 105, 78),
        "speed": 0.76,
        "distance": "227.9 million km",
        "diameter": "6,779 km",
        "day": "24.6 hours",
        "year": "687 Earth days",
        "fact": "A cold, rocky world with giant volcanoes.",
    },
    {
        "name": "Jupiter",
        "orbit": 188,
        "radius": 16,
        "color": (215, 177, 140),
        "speed": 0.48,
        "distance": "778.6 million km",
        "diameter": "139,820 km",
        "day": "9.9 hours",
        "year": "11.86 Earth years",
        "fact": "The largest planet, famous for its Great Red Spot.",
    },
    {
        "name": "Saturn",
        "orbit": 229,
        "radius": 13,
        "color": (226, 207, 151),
        "speed": 0.35,
        "distance": "1.43 billion km",
        "diameter": "116,460 km",
        "day": "10.7 hours",
        "year": "29.45 Earth years",
        "fact": "Its spectacular rings contain ice and rocky debris.",
    },
    {
        "name": "Uranus",
        "orbit": 266,
        "radius": 10,
        "color": (132, 218, 222),
        "speed": 0.26,
        "distance": "2.87 billion km",
        "diameter": "50,724 km",
        "day": "17.2 hours",
        "year": "84 Earth years",
        "fact": "An ice giant that rotates almost on its side.",
    },
    {
        "name": "Neptune",
        "orbit": 299,
        "radius": 10,
        "color": (81, 113, 240),
        "speed": 0.20,
        "distance": "4.50 billion km",
        "diameter": "49,244 km",
        "day": "16.1 hours",
        "year": "165 Earth years",
        "fact": "A distant blue world with extremely strong winds.",
    },
]

for index, planet in enumerate(PLANETS):
    planet["angle"] = index * 0.82 + 0.4

selected_planet = "Earth"
paused = False
show_orbits = True
show_labels = True
speed_multiplier = 1.0
elapsed = 0.0

random.seed(19)
STARS = [
    (
        random.randrange(WIDTH),
        random.randrange(HEIGHT),
        random.choice([1, 1, 1, 2]),
        random.randrange(70, 180),
    )
    for _ in range(190)
]


# -------------------- Helper Functions --------------------

def draw_text(text, font, color, position):
    image = font.render(str(text), True, color)
    SCREEN.blit(image, position)


def draw_centered(text, font, color, position):
    image = font.render(str(text), True, color)
    SCREEN.blit(image, image.get_rect(center=position))


def draw_panel(rect, color=PANEL):
    pygame.draw.rect(SCREEN, color, rect, border_radius=15)
    pygame.draw.rect(SCREEN, BORDER, rect, 1, border_radius=15)


def button(rect, label, active=False):
    color = (39, 66, 105) if active else (27, 37, 62)
    border = BLUE if active else BORDER

    pygame.draw.rect(SCREEN, color, rect, border_radius=8)
    pygame.draw.rect(SCREEN, border, rect, 1, border_radius=8)
    draw_centered(label, SMALL, WHITE, rect.center)


def get_selected_planet():
    for planet in PLANETS:
        if planet["name"] == selected_planet:
            return planet
    return PLANETS[2]


def planet_position(planet):
    angle = planet["angle"]
    orbit = planet["orbit"]

    return (
        int(SUN[0] + math.cos(angle) * orbit),
        int(SUN[1] + math.sin(angle) * orbit * 0.72),
    )


# -------------------- Background and Solar System --------------------

def draw_background():
    SCREEN.fill(BG)

    for x, y, radius, brightness in STARS:
        twinkle = int(15 * math.sin(elapsed * 1.8 + x))
        value = max(40, min(230, brightness + twinkle))

        pygame.draw.circle(
            SCREEN,
            (value, value, min(255, value + 15)),
            (x, y),
            radius,
        )


def draw_sun():
    x, y = SUN

    # Layered glow
    pygame.draw.circle(SCREEN, (46, 34, 28), (x, y), 33)
    pygame.draw.circle(SCREEN, (110, 69, 29), (x, y), 26)
    pygame.draw.circle(SCREEN, (235, 154, 49), (x, y), 20)
    pygame.draw.circle(SCREEN, (255, 214, 110), (x, y), 15)
    pygame.draw.circle(SCREEN, (255, 241, 184), (x - 4, y - 4), 6)

    if show_labels:
        draw_centered("SUN", SMALL, GOLD, (x, y + 43))


def draw_solar_system():
    if show_orbits:
        for planet in PLANETS:
            orbit = planet["orbit"]
            rect = pygame.Rect(
                SUN[0] - orbit,
                SUN[1] - int(orbit * 0.72),
                orbit * 2,
                int(orbit * 1.44),
            )
            pygame.draw.ellipse(SCREEN, (39, 49, 75), rect, 1)

    draw_sun()

    for planet in PLANETS:
        x, y = planet_position(planet)
        radius = planet["radius"]
        color = planet["color"]

        pygame.draw.circle(SCREEN, color, (x, y), radius)

        highlight = tuple(min(255, component + 35) for component in color)
        pygame.draw.circle(
            SCREEN,
            highlight,
            (x - max(1, radius // 3), y - max(1, radius // 3)),
            max(2, radius // 3),
        )

        if planet["name"] == "Saturn":
            ring = pygame.Rect(
                x - radius - 8,
                y - 4,
                radius * 2 + 16,
                8,
            )
            pygame.draw.ellipse(SCREEN, (195, 177, 132), ring, 2)

        if planet["name"] == selected_planet:
            pygame.draw.circle(
                SCREEN, WHITE, (x, y), radius + 5, 1
            )
            pygame.draw.circle(
                SCREEN, BLUE, (x, y), radius + 8, 1
            )

        if show_labels:
            draw_text(
                planet["name"],
                SMALL,
                WHITE,
                (x + radius + 5, y - 8),
            )


# -------------------- Information Panel --------------------

def draw_information_panel():
    rect = pygame.Rect(WIDTH - 300, 112, 270, 410)
    draw_panel(rect)

    planet = get_selected_planet()

    draw_text(
        "PLANET PROFILE",
        SMALL,
        BLUE,
        (rect.x + 17, rect.y + 17),
    )

    draw_text(
        planet["name"],
        LARGE,
        WHITE,
        (rect.x + 17, rect.y + 42),
    )

    pygame.draw.circle(
        SCREEN,
        planet["color"],
        (rect.right - 33, rect.y + 59),
        planet["radius"] + 2,
    )

    # Wrap the planet fact across multiple lines.
    words = planet["fact"].split()
    lines = []
    line = ""

    for word in words:
        candidate = f"{line} {word}".strip()
        if FONT.size(candidate)[0] > 232:
            lines.append(line)
            line = word
        else:
            line = candidate

    if line:
        lines.append(line)

    for index, line in enumerate(lines):
        draw_text(
            line,
            SMALL,
            MUTED,
            (rect.x + 17, rect.y + 91 + index * 19),
        )

    pygame.draw.line(
        SCREEN,
        BORDER,
        (rect.x + 17, rect.y + 143),
        (rect.right - 17, rect.y + 143),
        1,
    )

    details = [
        ("DISTANCE FROM SUN", planet["distance"]),
        ("DIAMETER", planet["diameter"]),
        ("DAY LENGTH", planet["day"]),
        ("ORBITAL PERIOD", planet["year"]),
    ]

    y = rect.y + 158

    for label, value in details:
        draw_text(label, SMALL, MUTED, (rect.x + 17, y))
        draw_text(value, FONT, WHITE, (rect.x + 17, y + 18))
        y += 51

    draw_text(
        "Click another planet to explore it.",
        SMALL,
        MUTED,
        (rect.x + 17, rect.bottom - 27),
    )


# -------------------- Controls --------------------

def draw_controls():
    rect = pygame.Rect(WIDTH - 300, 538, 270, 182)
    draw_panel(rect)

    draw_text("CONTROLS", MEDIUM, WHITE, (rect.x + 17, rect.y + 13))

    button(
        pygame.Rect(rect.x + 17, rect.y + 47, 108, 31),
        "Resume" if paused else "Pause",
        active=paused,
    )

    button(
        pygame.Rect(rect.x + 137, rect.y + 47, 116, 31),
        f"Speed: {speed_multiplier:g}x",
    )

    button(
        pygame.Rect(rect.x + 17, rect.y + 88, 108, 31),
        "Orbits: ON" if show_orbits else "Orbits: OFF",
        active=show_orbits,
    )

    button(
        pygame.Rect(rect.x + 137, rect.y + 88, 116, 31),
        "Labels: ON" if show_labels else "Labels: OFF",
        active=show_labels,
    )

    draw_text("SPACE  Pause / resume", SMALL, MUTED, (rect.x + 17, rect.y + 130))
    draw_text("+ / -  Change speed", SMALL, MUTED, (rect.x + 17, rect.y + 148))


def draw_planet_selector():
    rect = pygame.Rect(28, HEIGHT - 82, WIDTH - 348, 54)
    draw_panel(rect)

    draw_text("SELECT", SMALL, MUTED, (rect.x + 12, rect.y + 19))

    start_x = rect.x + 75

    for index, planet in enumerate(PLANETS):
        button_rect = pygame.Rect(
            start_x + index * 89,
            rect.y + 11,
            84,
            32,
        )

        button(
            button_rect,
            f"{index + 1}. {planet['name']}",
            active=(planet["name"] == selected_planet),
        )


def draw_header():
    draw_text("ASTROVIEW", TITLE, WHITE, (28, 20))
    draw_text(
        "Explore our Solar System",
        FONT,
        MUTED,
        (31, 61),
    )

    pygame.draw.line(
        SCREEN,
        BORDER,
        (28, 94),
        (WIDTH - 28, 94),
        1,
    )


def draw_footer():
    draw_text(
        "Planet sizes and orbital distances are illustrative, not to scale.",
        SMALL,
        MUTED,
        (30, HEIGHT - 19),
    )

    status = (
        "PAUSED"
        if paused
        else f"RUNNING  |  {speed_multiplier:g}x SPEED"
    )

    draw_text(
        status,
        SMALL,
        BLUE if paused else GREEN,
        (WIDTH - 295, HEIGHT - 19),
    )


# -------------------- Input Handling --------------------

def handle_click(position):
    global selected_planet
    global paused, show_orbits, show_labels, speed_multiplier

    # Select a planet by clicking it.
    for planet in PLANETS:
        x, y = planet_position(planet)

        if math.hypot(position[0] - x, position[1] - y) <= max(
            planet["radius"] + 10, 15
        ):
            selected_planet = planet["name"]
            return

    panel_x = WIDTH - 300
    panel_y = 538

    # Pause / resume button
    if (
        panel_x + 17 <= position[0] <= panel_x + 125
        and panel_y + 47 <= position[1] <= panel_y + 78
    ):
        paused = not paused
        return

    # Simulation speed button
    if (
        panel_x + 137 <= position[0] <= panel_x + 253
        and panel_y + 47 <= position[1] <= panel_y + 78
    ):
        speeds = [0.5, 1.0, 2.0, 4.0]
        current_index = speeds.index(speed_multiplier)
        speed_multiplier = speeds[(current_index + 1) % len(speeds)]
        return

    # Orbit visibility button
    if (
        panel_x + 17 <= position[0] <= panel_x + 125
        and panel_y + 88 <= position[1] <= panel_y + 119
    ):
        show_orbits = not show_orbits
        return

    # Planet label visibility button
    if (
        panel_x + 137 <= position[0] <= panel_x + 253
        and panel_y + 88 <= position[1] <= panel_y + 119
    ):
        show_labels = not show_labels
        return

    # Select a planet using the bottom buttons.
    selector_x = 28 + 75
    selector_y = HEIGHT - 82 + 11

    for index, planet in enumerate(PLANETS):
        rect = pygame.Rect(
            selector_x + index * 89,
            selector_y,
            84,
            32,
        )

        if rect.collidepoint(position):
            selected_planet = planet["name"]
            return


# -------------------- Main Application Loop --------------------

def main():
    global elapsed, paused, show_orbits, show_labels
    global selected_planet, speed_multiplier

    running = True

    while running:
        delta_time = min(CLOCK.tick(FPS) / 1000.0, 0.05)

        if not paused:
            elapsed += delta_time

            for planet in PLANETS:
                planet["angle"] += (
                    delta_time
                    * planet["speed"]
                    * speed_multiplier
                )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    paused = not paused

                elif event.key == pygame.K_o:
                    show_orbits = not show_orbits

                elif event.key == pygame.K_l:
                    show_labels = not show_labels

                elif pygame.K_1 <= event.key <= pygame.K_8:
                    index = event.key - pygame.K_1
                    selected_planet = PLANETS[index]["name"]

                elif event.key in (
                    pygame.K_EQUALS,
                    pygame.K_PLUS,
                    pygame.K_KP_PLUS,
                ):
                    speed_multiplier = min(4.0, speed_multiplier * 2)

                elif event.key in (
                    pygame.K_MINUS,
                    pygame.K_KP_MINUS,
                ):
                    speed_multiplier = max(0.5, speed_multiplier / 2)

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                handle_click(event.pos)

        draw_background()
        draw_header()
        draw_solar_system()
        draw_information_panel()
        draw_controls()
        draw_planet_selector()
        draw_footer()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
