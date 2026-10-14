
import random
import time
import pygame

# -------------------- INITIALIZATION --------------------

pygame.init()

WIDTH, HEIGHT = 1000, 740
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Day 13 - Sudoku")

FPS = 60
GRID_SIZE = 540
CELL_SIZE = GRID_SIZE // 9
GRID_X, GRID_Y = 30, 115

# Colors
BG = (18, 24, 38)
PANEL = (29, 38, 56)
WHITE = (240, 244, 250)
MUTED = (155, 169, 190)
BLUE = (75, 135, 245)
BLUE_LIGHT = (43, 67, 105)
GRID_COLOR = (77, 91, 115)
GIVEN_COLOR = (240, 244, 250)
USER_COLOR = (100, 190, 255)
GREEN = (76, 201, 140)
RED = (255, 100, 110)
YELLOW = (255, 205, 90)
SELECT_COLOR = (52, 91, 145)

FONT = pygame.font.SysFont("arial", 22)
SMALL_FONT = pygame.font.SysFont("arial", 17)
NUMBER_FONT = pygame.font.SysFont("arial", 30)
TITLE_FONT = pygame.font.SysFont("arial", 34, bold=True)
BUTTON_FONT = pygame.font.SysFont("arial", 18, bold=True)

CLOCK = pygame.time.Clock()

# -------------------- SUDOKU LOGIC --------------------


def generate_solution():
    """Generate a complete valid Sudoku board."""
    digits = list(range(1, 10))
    random.shuffle(digits)

    rows = []
    for band in range(3):
        group = list(range(3))
        random.shuffle(group)
        rows.extend(band * 3 + r for r in group)

    bands = [0, 1, 2]
    random.shuffle(bands)
    rows = [bands[r // 3] * 3 + r % 3 for r in rows]

    cols = []
    for stack in range(3):
        group = list(range(3))
        random.shuffle(group)
        cols.extend(stack * 3 + c for c in group)

    stacks = [0, 1, 2]
    random.shuffle(stacks)
    cols = [stacks[c // 3] * 3 + c % 3 for c in cols]

    pattern = lambda r, c: (3 * (r % 3) + r // 3 + c) % 9

    return [
        [digits[pattern(r, c)] for c in cols]
        for r in rows
    ]


def create_puzzle(solution, difficulty):
    """Remove cells to create a playable puzzle."""
    puzzle = [row[:] for row in solution]

    empty_counts = {
        "Easy": 35,
        "Medium": 45,
        "Hard": 52
    }

    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    for r, c in cells[:empty_counts[difficulty]]:
        puzzle[r][c] = 0

    return puzzle


def is_valid(board, row, col, number):
    """Check row, column, and 3x3 box constraints."""
    for c in range(9):
        if c != col and board[row][c] == number:
            return False

    for r in range(9):
        if r != row and board[r][col] == number:
            return False

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3

    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if (r, c) != (row, col) and board[r][c] == number:
                return False

    return True


def solve_board(board):
    """Solve a Sudoku board using backtracking."""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                numbers = list(range(1, 10))
                random.shuffle(numbers)

                for number in numbers:
                    if is_valid(board, row, col, number):
                        board[row][col] = number

                        if solve_board(board):
                            return True

                        board[row][col] = 0

                return False

    return True


# -------------------- GAME STATE --------------------

difficulty = "Easy"
solution = generate_solution()
puzzle = create_puzzle(solution, difficulty)
board = [row[:] for row in puzzle]

selected = None
mistakes = 0
hints_used = 0
start_time = time.time()
game_message = "Select a cell and enter a number."
message_color = MUTED
game_won = False


def new_game(level=None):
    """Start a new Sudoku puzzle."""
    global difficulty, solution, puzzle, board
    global selected, mistakes, hints_used, start_time
    global game_message, message_color, game_won

    if level:
        difficulty = level

    solution = generate_solution()
    puzzle = create_puzzle(solution, difficulty)
    board = [row[:] for row in puzzle]

    selected = None
    mistakes = 0
    hints_used = 0
    start_time = time.time()
    game_message = "Select a cell and enter a number."
    message_color = MUTED
    game_won = False


def format_time(seconds):
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02}:{seconds:02}"


def is_complete():
    return all(board[r][c] == solution[r][c]
               for r in range(9) for c in range(9))


def enter_number(number):
    """Enter a number into the selected empty cell."""
    global mistakes, game_message, message_color, game_won

    if selected is None or game_won:
        return

    row, col = selected

    if puzzle[row][col] != 0:
        game_message = "This is a fixed clue."
        message_color = YELLOW
        return

    board[row][col] = number

    if number != solution[row][col]:
        mistakes += 1
        game_message = "Incorrect number! Try again."
        message_color = RED
    else:
        game_message = "Correct!"
        message_color = GREEN

    if is_complete():
        game_won = True
        game_message = "Congratulations! Puzzle completed!"
        message_color = GREEN


def erase_selected():
    global game_message, message_color

    if selected is None or game_won:
        return

    row, col = selected

    if puzzle[row][col] == 0:
        board[row][col] = 0
        game_message = "Cell cleared."
        message_color = MUTED


def use_hint():
    global hints_used, game_message, message_color, game_won

    if selected is None or game_won:
        return

    row, col = selected

    if puzzle[row][col] != 0:
        game_message = "Choose an empty cell for a hint."
        message_color = YELLOW
        return

    board[row][col] = solution[row][col]
    hints_used += 1
    game_message = "Hint added!"
    message_color = GREEN

    if is_complete():
        game_won = True
        game_message = "Congratulations! Puzzle completed!"
        message_color = GREEN


def check_board():
    global game_message, message_color, game_won

    if is_complete():
        game_won = True
        game_message = "Excellent! Sudoku solved!"
        message_color = GREEN
    else:
        incorrect = sum(
            1 for r in range(9)
            for c in range(9)
            if board[r][c] != 0
            and board[r][c] != solution[r][c]
        )

        if incorrect:
            game_message = f"{incorrect} incorrect cell(s) found."
            message_color = RED
        else:
            game_message = "So far, so good! Keep going."
            message_color = GREEN


def solve_puzzle():
    global board, game_message, message_color, game_won

    board = [row[:] for row in solution]
    game_won = True
    game_message = "Puzzle solved by the solver!"
    message_color = GREEN


# -------------------- DRAWING HELPERS --------------------


def draw_text(text, x, y, font=FONT, color=WHITE, center=False):
    surface = font.render(str(text), True, color)
    rect = surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    SCREEN.blit(surface, rect)


def draw_button(rect, text, color=BLUE, text_color=WHITE):
    mouse_pos = pygame.mouse.get_pos()
    button_color = tuple(min(255, channel + 18) for channel in color) \
        if rect.collidepoint(mouse_pos) else color

    pygame.draw.rect(SCREEN, button_color, rect, border_radius=9)
    draw_text(text, rect.centerx, rect.centery,
              BUTTON_FONT, text_color, center=True)


# -------------------- DRAW GAME --------------------


def draw_grid():
    """Draw cells, highlights, numbers, and Sudoku borders."""
    for row in range(9):
        for col in range(9):
            rect = pygame.Rect(
                GRID_X + col * CELL_SIZE,
                GRID_Y + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            if selected:
                sr, sc = selected

                if row == sr and col == sc:
                    color = BLUE
                elif row == sr or col == sc:
                    color = BLUE_LIGHT
                elif row // 3 == sr // 3 and col // 3 == sc // 3:
                    color = BLUE_LIGHT
                else:
                    color = PANEL
            else:
                color = PANEL

            pygame.draw.rect(SCREEN, color, rect)

            number = board[row][col]

            if number != 0:
                if puzzle[row][col] != 0:
                    text_color = GIVEN_COLOR
                elif number == solution[row][col]:
                    text_color = USER_COLOR
                else:
                    text_color = RED

                draw_text(
                    number,
                    rect.centerx,
                    rect.centery,
                    NUMBER_FONT,
                    text_color,
                    center=True
                )

    # Thin cell lines and thicker 3x3 borders
    for i in range(10):
        thickness = 4 if i % 3 == 0 else 1
        color = WHITE if i % 3 == 0 else GRID_COLOR

        x = GRID_X + i * CELL_SIZE
        y = GRID_Y + i * CELL_SIZE

        pygame.draw.line(
            SCREEN, color,
            (x, GRID_Y), (x, GRID_Y + GRID_SIZE),
            thickness
        )
        pygame.draw.line(
            SCREEN, color,
            (GRID_X, y), (GRID_X + GRID_SIZE, y),
            thickness
        )


def draw_panel():
    panel_rect = pygame.Rect(605, 95, 365, 610)
    pygame.draw.rect(SCREEN, PANEL, panel_rect, border_radius=15)

    draw_text("SUDOKU", 635, 115, TITLE_FONT, WHITE)
    draw_text(f"Difficulty: {difficulty}", 635, 160, FONT, MUTED)

    elapsed = int(time.time() - start_time)
    draw_text(f"Time: {format_time(elapsed)}", 635, 200, FONT)
    draw_text(f"Mistakes: {mistakes}", 635, 235, FONT, RED)
    draw_text(f"Hints used: {hints_used}", 635, 270, FONT, YELLOW)

    draw_text("DIFFICULTY", 635, 320, SMALL_FONT, MUTED)

    draw_button(pygame.Rect(635, 350, 95, 40), "Easy",
                GREEN if difficulty == "Easy" else BLUE)
    draw_button(pygame.Rect(740, 350, 95, 40), "Medium",
                GREEN if difficulty == "Medium" else BLUE)
    draw_button(pygame.Rect(845, 350, 95, 40), "Hard",
                GREEN if difficulty == "Hard" else BLUE)

    draw_text("ACTIONS", 635, 415, SMALL_FONT, MUTED)

    draw_button(pygame.Rect(635, 445, 140, 45), "Hint", (46, 125, 90))
    draw_button(pygame.Rect(790, 445, 150, 45), "Check", BLUE)

    draw_button(pygame.Rect(635, 505, 140, 45), "Solve Puzzle",
                (112, 85, 170))
    draw_button(pygame.Rect(790, 505, 150, 45), "New Game",
                (65, 95, 140))

    draw_button(pygame.Rect(635, 565, 140, 45), "Erase", (100, 82, 65))
    draw_button(pygame.Rect(790, 565, 150, 45), "Quit", (145, 65, 75))

    draw_text("CONTROLS", 635, 625, SMALL_FONT, MUTED)
    draw_text("1-9: Enter  |  Backspace: Erase", 635, 650,
              SMALL_FONT, WHITE)
    draw_text("H: Hint  |  C: Check  |  S: Solve", 635, 675,
              SMALL_FONT, WHITE)


def draw_game():
    SCREEN.fill(BG)

    draw_text("DAY 13  |  SUDOKU CHALLENGE",
              30, 35, TITLE_FONT, WHITE)

    draw_grid()
    draw_panel()

    draw_text(game_message, 30, 675, SMALL_FONT, message_color)

    if game_won:
        overlay = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        overlay.fill((18, 24, 38, 35))
        SCREEN.blit(overlay, (GRID_X, GRID_Y))

    pygame.display.flip()


# -------------------- MAIN GAME LOOP --------------------

running = True

while running:
    CLOCK.tick(FPS)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Grid selection
            if (GRID_X <= mx < GRID_X + GRID_SIZE
                    and GRID_Y <= my < GRID_Y + GRID_SIZE):
                col = (mx - GRID_X) // CELL_SIZE
                row = (my - GRID_Y) // CELL_SIZE
                selected = (row, col)

            # Difficulty buttons
            elif 350 <= my <= 390:
                if 635 <= mx <= 730:
                    new_game("Easy")
                elif 740 <= mx <= 835:
                    new_game("Medium")
                elif 845 <= mx <= 940:
                    new_game("Hard")

            # Action buttons
            elif 445 <= my <= 490:
                if 635 <= mx <= 775:
                    use_hint()
                elif 790 <= mx <= 940:
                    check_board()

            elif 505 <= my <= 550:
                if 635 <= mx <= 775:
                    solve_puzzle()
                elif 790 <= mx <= 940:
                    new_game()

            elif 565 <= my <= 610:
                if 635 <= mx <= 775:
                    erase_selected()
                elif 790 <= mx <= 940:
                    running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_h:
                use_hint()

            elif event.key == pygame.K_c:
                check_board()

            elif event.key == pygame.K_s:
                solve_puzzle()

            elif event.key == pygame.K_r:
                new_game()

            elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0):
                erase_selected()

            elif pygame.K_1 <= event.key <= pygame.K_9:
                enter_number(event.key - pygame.K_0)

            elif pygame.K_KP1 <= event.key <= pygame.K_KP9:
                enter_number(event.key - pygame.K_KP0)

    draw_game()

pygame.quit()
