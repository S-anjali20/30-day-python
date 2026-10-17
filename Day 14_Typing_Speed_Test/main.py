import json
import random
import sys
import textwrap
from pathlib import Path

import pygame

# ------------------------------------------------------------
# Typing Speed Test - Python + Pygame
# ------------------------------------------------------------

pygame.init()
pygame.display.set_caption("Typing Speed Test")

WIDTH, HEIGHT = 1200, 850
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
CLOCK = pygame.time.Clock()
FPS = 60

# Colors
BG = (18, 24, 39)
CARD = (30, 41, 59)
CARD_LIGHT = (38, 50, 72)
WHITE = (239, 243, 250)
MUTED = (155, 169, 190)
BLUE = (68, 132, 247)
GREEN = (65, 201, 145)
RED = (245, 93, 104)
YELLOW = (245, 190, 65)
DARK_TEXT = (255, 255, 255)

FONT_PATH = None  # Set to a .ttf path if you want a custom font.
DATA_FILE = Path(__file__).with_name("typing_stats.json")

PASSAGES = [
    "Programming is not only about writing code. It is about solving problems, "
    "thinking clearly, and turning ideas into useful tools. Small improvements "
    "made every day can lead to remarkable progress over time.",
    "Technology changes the way people learn, work, and communicate. Building "
    "good habits, staying curious, and practicing consistently help us adapt "
    "to new challenges and discover better solutions.",
    "A journey of a thousand miles begins with a single step. Focus on progress "
    "rather than perfection, learn from mistakes, and keep moving forward even "
    "when a task feels difficult.",
    "Python is a readable and versatile programming language. It is used for "
    "automation, web development, data analysis, artificial intelligence, and "
    "many other tasks that make everyday work easier.",
    "The best way to improve a skill is to practice with patience and purpose. "
    "Pay attention to accuracy first, then gradually increase your speed as "
    "your confidence and muscle memory improve."
]

def font(size, bold=False):
    # pygame's default font is reliable on all platforms.
    return pygame.font.SysFont("arial", size, bold=bold)

F_TITLE = font(42, True)
F_SUBTITLE = font(23)
F_HEADING = font(28, True)
F_BODY = font(20)
F_SMALL = font(17)
F_PASSAGE = font(25)
F_BUTTON = font(23, True)
F_STAT = font(32, True)

def load_stats():
    try:
        if DATA_FILE.exists():
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            return {
                "best_wpm": max(0, int(data.get("best_wpm", 0))),
                "best_accuracy": max(0.0, min(100.0, float(data.get("best_accuracy", 0.0))))
            }
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass
    return {"best_wpm": 0, "best_accuracy": 0.0}

def save_stats(stats):
    try:
        DATA_FILE.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    except OSError:
        print("Warning: Could not save personal-best statistics.")

def draw_text(surface, text, used_font, color, center, max_width=None):
    """Draw text centered; wrap it into lines when max_width is provided."""
    if max_width is None:
        rendered = used_font.render(text, True, color)
        surface.blit(rendered, rendered.get_rect(center=center))
        return center[1] + rendered.get_height()

    words = text.split()
    lines, line = [], ""
    for word in words:
        candidate = word if not line else line + " " + word
        if used_font.size(candidate)[0] <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)

    line_height = used_font.get_linesize() + 5
    total_height = len(lines) * line_height
    y = center[1] - total_height // 2
    for item in lines:
        rendered = used_font.render(item, True, color)
        surface.blit(rendered, rendered.get_rect(center=(center[0], y + line_height // 2)))
        y += line_height
    return y

def rounded_rect(surface, color, rect, radius=18, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, width=border, border_radius=radius)

def button(surface, rect, label, color, mouse_pos, enabled=True):
    actual = color
    if not enabled:
        actual = tuple(int(c * 0.45) for c in color)
    elif rect.collidepoint(mouse_pos):
        actual = tuple(min(255, int(c * 1.12)) for c in color)
    rounded_rect(surface, actual, rect, 15)
    rendered = F_BUTTON.render(label, True, WHITE)
    surface.blit(rendered, rendered.get_rect(center=rect.center))

def calculate_stats(typed, passage, elapsed):
    correct = sum(1 for i, char in enumerate(typed) if i < len(passage) and char == passage[i])
    incorrect = len(typed) - correct
    accuracy = (correct / len(typed) * 100) if typed else 0.0
    minutes = max(elapsed, 0.01) / 60
    # Standard WPM: correct characters / 5 / elapsed minutes.
    wpm = int((correct / 5) / minutes)
    return wpm, accuracy, correct, incorrect

class TypingTest:
    def __init__(self):
        self.stats = load_stats()
        self.state = "home"
        self.duration = 30
        self.reset_test()

    def reset_test(self):
        self.passage = random.choice(PASSAGES)
        self.typed = ""
        self.started_at = None
        self.end_at = None
        self.remaining = float(self.duration)
        self.final_result = None

    def start(self, duration):
        self.duration = duration
        self.reset_test()
        self.state = "test"

    def finish(self):
        if self.state != "test":
            return
        elapsed = self.duration - max(0, self.remaining)
        result = calculate_stats(self.typed, self.passage, elapsed)
        self.final_result = {
            "wpm": result[0],
            "accuracy": result[1],
            "correct": result[2],
            "incorrect": result[3],
            "typed": len(self.typed)
        }
        if result[0] > self.stats["best_wpm"]:
            self.stats["best_wpm"] = result[0]
        if self.typed and result[1] > self.stats["best_accuracy"]:
            self.stats["best_accuracy"] = round(result[1], 1)
        save_stats(self.stats)
        self.state = "results"

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.VIDEORESIZE:
            global SCREEN, WIDTH, HEIGHT
            WIDTH, HEIGHT = max(760, event.w), max(650, event.h)
            SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == "test":
                    self.state = "home"
                    self.reset_test()
                else:
                    pygame.quit()
                    sys.exit()
            elif self.state == "test":
                if event.key == pygame.K_BACKSPACE:
                    self.typed = self.typed[:-1]
                elif event.key == pygame.K_RETURN:
                    # Enter is treated as a space for passages with line breaks.
                    if len(self.typed) < len(self.passage):
                        expected = self.passage[len(self.typed)]
                        if expected == "\n":
                            self.typed += "\n"
                elif event.unicode and event.unicode.isprintable():
                    if len(self.typed) < len(self.passage):
                        if self.started_at is None:
                            self.started_at = pygame.time.get_ticks() / 1000
                            self.end_at = self.started_at + self.duration
                        self.typed += event.unicode
                if len(self.typed) >= len(self.passage):
                    self.finish()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.state == "home":
                if self.button_30.collidepoint(pos):
                    self.start(30)
                elif self.button_60.collidepoint(pos):
                    self.start(60)
            elif self.state == "results":
                if self.restart_button.collidepoint(pos):
                    self.start(self.duration)
                elif self.home_button.collidepoint(pos):
                    self.state = "home"
            elif self.state == "test":
                if self.home_button.collidepoint(pos):
                    self.state = "home"
                    self.reset_test()

    def update(self):
        if self.state == "test" and self.started_at is not None:
            now = pygame.time.get_ticks() / 1000
            self.remaining = max(0, self.end_at - now)
            if self.remaining <= 0:
                self.finish()

    def draw_home(self, surface):
        surface.fill(BG)
        mouse = pygame.mouse.get_pos()
        draw_text(surface, "TYPING SPEED TEST", F_TITLE, WHITE, (WIDTH // 2, 78))
        draw_text(surface, "Measure your speed. Improve your accuracy.", F_SUBTITLE, MUTED,
                  (WIDTH // 2, 126))

        card_w, card_h = min(720, WIDTH - 60), 440
        card = pygame.Rect((WIDTH-card_w)//2, 175, card_w, card_h)
        rounded_rect(surface, CARD, card, 26)

        draw_text(surface, "How fast can you type?", F_HEADING, WHITE, (WIDTH//2, 225))
        draw_text(surface, "Type the displayed passage before time runs out.",
                  F_BODY, MUTED, (WIDTH//2, 278))
        draw_text(surface, "Correct characters increase your WPM.", F_BODY, GREEN,
                  (WIDTH//2, 322))
        draw_text(surface, "Accuracy and mistakes are tracked too.", F_BODY, YELLOW,
                  (WIDTH//2, 360))
        draw_text(surface, f"Personal best: {self.stats['best_wpm']} WPM",
                  F_HEADING, BLUE, (WIDTH//2, 425))
        draw_text(surface, f"Best accuracy: {self.stats['best_accuracy']:.1f}%",
                  F_SUBTITLE, MUTED, (WIDTH//2, 468))

        bw, bh, gap = 205, 72, 48
        total = bw * 2 + gap
        left = (WIDTH - total) // 2
        self.button_30 = pygame.Rect(left, 665, bw, bh)
        self.button_60 = pygame.Rect(left + bw + gap, 665, bw, bh)
        button(surface, self.button_30, "30 Seconds", BLUE, mouse)
        button(surface, self.button_60, "60 Seconds", GREEN, mouse)
        draw_text(surface, "Choose a duration to begin", F_SMALL, MUTED,
                  (WIDTH//2, 760))
        draw_text(surface, "Press ESC to quit", F_SMALL, MUTED, (WIDTH//2, HEIGHT-25))

    def draw_passage(self, surface, x, y, max_width):
        """Draw expected passage, coloring typed characters by correctness."""
        words = self.passage.split(" ")
        tokens = []
        cursor = 0
        for wi, word in enumerate(words):
            tokens.append((word, cursor))
            cursor += len(word) + (1 if wi < len(words)-1 else 0)

        line_y = y
        line_x = x
        line_height = F_PASSAGE.get_linesize() + 12
        for word, start_index in tokens:
            chunk = word + (" " if start_index + len(word) < len(self.passage) else "")
            chunk_width = F_PASSAGE.size(chunk)[0]
            if line_x + chunk_width > x + max_width:
                line_x = x
                line_y += line_height
            for j, char in enumerate(chunk):
                index = start_index + j
                color = MUTED
                if index < len(self.typed):
                    color = GREEN if self.typed[index] == self.passage[index] else RED
                char_surface = F_PASSAGE.render(char, True, color)
                surface.blit(char_surface, (line_x, line_y))
                line_x += char_surface.get_width()
            # Draw caret at the next character.
            if len(self.typed) == start_index + len(word):
                pass

        # Cursor at the current typing position.
        if self.typed:
            caret_index = min(len(self.typed), len(self.passage))
            prefix = self.passage[:caret_index]
            # Locate the caret by reproducing the same wrapping calculation.
            cx, cy = x, y
            for i, char in enumerate(prefix):
                if char == " ":
                    char_w = F_PASSAGE.size(char)[0]
                else:
                    char_w = F_PASSAGE.size(char)[0]
                if cx + char_w > x + max_width:
                    cx, cy = x, cy + line_height
                cx += char_w
            pygame.draw.line(surface, BLUE, (cx, cy-2), (cx, cy+F_PASSAGE.get_height()+2), 3)

    def draw_test(self, surface):
        surface.fill(BG)
        mouse = pygame.mouse.get_pos()
        draw_text(surface, "TYPING SPEED TEST", F_TITLE, WHITE, (WIDTH//2, 55))
        draw_text(surface, "Type the passage below. Your timer starts with your first key.",
                  F_SMALL, MUTED, (WIDTH//2, 98))

        card_w = min(1000, WIDTH - 60)
        card = pygame.Rect((WIDTH-card_w)//2, 135, card_w, 280)
        rounded_rect(surface, CARD, card, 22)
        self.draw_passage(surface, card.x+30, card.y+35, card.width-60)

        elapsed = self.duration - self.remaining
        wpm, accuracy, correct, incorrect = calculate_stats(self.typed, self.passage, elapsed)
        stats_y = 475
        stat_w = min(205, (WIDTH-100)//4)
        gap = 18
        total = stat_w*4 + gap*3
        start_x = (WIDTH-total)//2
        values = [
            ("TIME LEFT", f"{int(self.remaining + 0.999)}s", BLUE),
            ("WPM", str(wpm), GREEN),
            ("ACCURACY", f"{accuracy:.1f}%", YELLOW),
            ("MISTAKES", str(incorrect), RED),
        ]
        for i, (label, value, color) in enumerate(values):
            rect = pygame.Rect(start_x+i*(stat_w+gap), stats_y, stat_w, 110)
            rounded_rect(surface, CARD, rect, 16)
            draw_text(surface, label, F_SMALL, MUTED, (rect.centerx, rect.y+25))
            draw_text(surface, value, F_STAT, color, (rect.centerx, rect.y+70))

        progress_w = min(800, WIDTH-100)
        progress_rect = pygame.Rect((WIDTH-progress_w)//2, 625, progress_w, 12)
        rounded_rect(surface, CARD_LIGHT, progress_rect, 6)
        ratio = len(self.typed) / max(1, len(self.passage))
        if ratio > 0:
            rounded_rect(surface, BLUE, pygame.Rect(progress_rect.x, progress_rect.y,
                         int(progress_rect.width*ratio), progress_rect.height), 6)

        draw_text(surface, f"Characters: {len(self.typed)}/{len(self.passage)}   "
                  f"Correct: {correct}   Incorrect: {incorrect}",
                  F_BODY, MUTED, (WIDTH//2, 680))
        self.home_button = pygame.Rect((WIDTH-180)//2, 720, 180, 54)
        button(surface, self.home_button, "Back to Home", CARD_LIGHT, mouse)
        draw_text(surface, "Backspace corrects your typing  •  ESC returns home",
                  F_SMALL, MUTED, (WIDTH//2, HEIGHT-22))

    def draw_results(self, surface):
        surface.fill(BG)
        mouse = pygame.mouse.get_pos()
        draw_text(surface, "TEST COMPLETE!", F_TITLE, WHITE, (WIDTH//2, 75))
        draw_text(surface, "Here is how you performed.", F_SUBTITLE, MUTED,
                  (WIDTH//2, 120))

        card_w = min(780, WIDTH-60)
        card = pygame.Rect((WIDTH-card_w)//2, 165, card_w, 430)
        rounded_rect(surface, CARD, card, 25)
        result = self.final_result or {"wpm": 0, "accuracy": 0, "correct": 0,
                                       "incorrect": 0, "typed": 0}
        draw_text(surface, f"{result['wpm']} WPM", F_TITLE, BLUE, (WIDTH//2, 235))
        draw_text(surface, f"Accuracy: {result['accuracy']:.1f}%", F_HEADING, GREEN,
                  (WIDTH//2, 292))

        metrics = [
            ("Correct characters", str(result["correct"]), GREEN),
            ("Incorrect characters", str(result["incorrect"]), RED),
            ("Total characters typed", str(result["typed"]), WHITE),
            ("Personal best", f"{self.stats['best_wpm']} WPM", BLUE),
        ]
        for i, (label, value, color) in enumerate(metrics):
            yy = 355 + i*48
            draw_text(surface, label, F_BODY, MUTED, (WIDTH//2-135, yy))
            draw_text(surface, value, F_BODY, color, (WIDTH//2+190, yy))

        bw, bh, gap = 205, 62, 25
        total = bw*2+gap
        left = (WIDTH-total)//2
        self.restart_button = pygame.Rect(left, 640, bw, bh)
        self.home_button = pygame.Rect(left+bw+gap, 640, bw, bh)
        button(surface, self.restart_button, "Try Again", GREEN, mouse)
        button(surface, self.home_button, "Home", BLUE, mouse)
        draw_text(surface, "Press ESC to quit", F_SMALL, MUTED, (WIDTH//2, HEIGHT-25))

    def draw(self):
        if self.state == "home":
            self.draw_home(SCREEN)
        elif self.state == "test":
            self.draw_test(SCREEN)
        else:
            self.draw_results(SCREEN)
        pygame.display.flip()

def main():
    app = TypingTest()
    while True:
        for event in pygame.event.get():
            app.handle_event(event)
        app.update()
        app.draw()
        CLOCK.tick(FPS)

if __name__ == "__main__":
    main()
