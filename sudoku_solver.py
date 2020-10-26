import pygame
import numpy as np
from time import sleep


SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600

BIG_LINE_WIDTH = 4
# BIG_LINE_COLOR = (33, 109, 148)
BIG_LINE_OFFSET = 0

SMALL_LINE_WIDTH = 2
# SMALL_LINE_COLOR = (3, 29, 66)
SMALL_LINE_OFFSET = 6

GRID_COLOR_SOLVING = (3, 29, 66)
GRID_COLOR_SOLVED = (20, 227, 62)
GRID_COLOR_FAILED = (212, 19, 42)

NUMBERS_SIZE = 24
NUMBERS_COLOR = (255, 255, 255)

BUTTON_WIDTH = 280
BUTTON_HEIGHT = 60
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR_SOLVE = (30, 30, 60)
BUTTON_COLOR_STOP = (220, 50, 50)

CHANGES_PER_SECOND = 50


class SudokuSolver():
    """The sudoku solver app class"""

    def __init__(self, board):
        """Create a sudoku problem based on the board (a numpy matrix)"""
        self.running = True
        self.state = "waiting"
        pygame.init()
        pygame.display.set_caption("Sudoku Solver")

        self.define_grid()
        self.define_number_positions()
        self.define_button()
        self.board = board
        self.font = pygame.font.Font('ubuntu.ttf', NUMBERS_SIZE)
        self.sleep_time = 1 / CHANGES_PER_SECOND

        self.original_board = board.copy()

    def execute(self):
        """Start the app and run the game loop"""
        self.init()

        while self.running:
            self.render()
            self.events()

        pygame.quit()

    def init(self):
        """Prepare running the game"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.running = True
        self.state = "waiting"

        self.button_text = "Solve!"
        self.button_color = BUTTON_COLOR_SOLVE
        self.puzzle_state = "unsolved"

        if not self.checkBoardValid():
            self.state = "failed"
            self.puzzle_state = "failed"
            self.button_text = "Impossible puzzle!"

    def solve(self):
        """Solve the puzzle updating the screen every step"""
        if not self.running or self.state == "stopping":
            return False

        # Find first empty tile
        target = ()
        for i in range(9**2):
            if self.board[i // 9, i % 9] == 0:
                target = (i // 9, i % 9)
                break

        # If there are no empty tiles, the puzzle is solved
        if not target:
            return True

        # Tests all possible values
        for value in range(1, 10):
            if not self.isPossibleAssign(target, value):
                continue

            self.update_board(target, value)

            if self.solve():
                return True

        # In case of failure, reset and return False
        self.update_board(target, 0)

        return False

    def render(self):
        """Render the current image on the screen"""
        # Background
        self.screen.fill((20, 20, 20))

        # Grid
        grid_color = GRID_COLOR_SOLVING
        if self.puzzle_state == "solved":
            grid_color = GRID_COLOR_SOLVED
        if self.puzzle_state == "failed":
            grid_color = GRID_COLOR_FAILED

        for line in self.small_lines:
            pygame.draw.rect(self.screen, grid_color, line)
        for line in self.big_lines:
            pygame.draw.rect(self.screen, grid_color, line)

        # Board
        for i in range(9):
            for j in range(9):
                if self.board[i, j] == 0:
                    continue

                text = self.font.render(
                    str(self.board[i, j]),
                    True,
                    NUMBERS_COLOR
                )
                textRect = text.get_rect()
                textRect.center = self.number_positions[i, j]
                self.screen.blit(text, textRect)

        # Quitting message
        if not self.running:
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(
                SCREEN_WIDTH // 2 - 100,
                SCREEN_WIDTH // 2 - 25,
                200,
                50
            ))
            text = self.font.render("Quitting...", True, (255, 255, 255))
            textRect = text.get_rect()
            textRect.center = (SCREEN_WIDTH // 2, SCREEN_WIDTH // 2)
            self.screen.blit(text, textRect)

        # Separator
        pygame.draw.rect(self.screen, GRID_COLOR_SOLVING, self.separator1)
        pygame.draw.rect(self.screen, (180, 180, 180), self.separator2)

        # Button
        pygame.draw.rect(self.screen, self.button_color, self.button)
        text = self.font.render(self.button_text, True, BUTTON_TEXT_COLOR)
        textRect = text.get_rect()
        textRect.center = (
            SCREEN_WIDTH // 2,
            (SCREEN_WIDTH + SCREEN_HEIGHT) // 2,
        )
        self.screen.blit(text, textRect)

        pygame.display.update()

    def events(self):
        """Deals with user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.sleep_time = 0
                return

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()

                if self.button.collidepoint(pos):
                    if self.state == "solving":
                        self.state = "stopping"

                    if self.state == "solved":
                        self.state = "waiting"
                        self.puzzle_state = "solving"
                        self.button_text = "Solve!"
                        self.board = self.original_board.copy()

                    elif self.state == "waiting":
                        self.state = "solving"
                        self.button_text = "Stop!"
                        self.button_color = BUTTON_COLOR_STOP

                        isSolved = self.solve()

                        self.button_color = BUTTON_COLOR_SOLVE
                        if isSolved:
                            self.state = "solved"
                            self.button_text = "Clear"
                            self.puzzle_state = "solved"
                        else:
                            if self.state == "stopping":
                                self.state = "waiting"
                                self.button_text = "Solve!"
                                self.puzzle_state = "solving"
                            else:
                                self.state = "solved"
                                self.button_text = "Clear"
                                self.puzzle_state = "failed"

    def update_board(self, position, value):
        """Change a value of the board and refresh the screen"""
        self.board[position] = value
        self.render()
        self.events()
        sleep(self.sleep_time)

    def define_grid(self):
        """Define the Rects that compose the grid"""
        # Big lines
        self.big_lines = []
        for i in range(1, 3):
            # Vertical line
            self.big_lines.append(pygame.Rect(
                i * SCREEN_WIDTH // 3 - BIG_LINE_WIDTH // 2,
                BIG_LINE_OFFSET,
                BIG_LINE_WIDTH,
                SCREEN_WIDTH - 2 * BIG_LINE_OFFSET
            ))

            # Horizontal line
            self.big_lines.append(pygame.Rect(
                BIG_LINE_OFFSET,
                i * SCREEN_WIDTH // 3 - BIG_LINE_WIDTH // 2,
                SCREEN_WIDTH - 2 * BIG_LINE_OFFSET,
                BIG_LINE_WIDTH
            ))

        # Small lines
        self.small_lines = []
        for i in range(1, 9):
            if i % 3 == 0:
                continue

            # Vertical line
            self.small_lines.append(pygame.Rect(
                i * SCREEN_WIDTH // 9 - SMALL_LINE_WIDTH // 2,
                SMALL_LINE_OFFSET,
                SMALL_LINE_WIDTH,
                SCREEN_WIDTH - 2 * SMALL_LINE_OFFSET
            ))

            # Horizontal line
            self.small_lines.append(pygame.Rect(
                SMALL_LINE_OFFSET,
                i * SCREEN_WIDTH // 9 - SMALL_LINE_WIDTH // 2,
                SCREEN_WIDTH - 2 * SMALL_LINE_OFFSET,
                SMALL_LINE_WIDTH
            ))

    def define_number_positions(self):
        """Define the positions the number will take on the board"""
        self.number_positions = np.array([
            [(
                int((j + 0.5) * SCREEN_WIDTH // 9),
                int((i + 0.5) * SCREEN_WIDTH // 9)
            ) for j in range(9)]
            for i in range(9)
        ])

    def define_button(self):
        """Define the separator and button sprites"""
        self.separator1 = pygame.Rect(
            0,
            SCREEN_WIDTH,
            SCREEN_WIDTH,
            BIG_LINE_WIDTH,
        )
        self.separator2 = pygame.Rect(
            0,
            SCREEN_WIDTH + BIG_LINE_WIDTH // 2,
            SCREEN_WIDTH,
            BIG_LINE_WIDTH,
        )

        self.button = pygame.Rect(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            (SCREEN_HEIGHT + SCREEN_WIDTH) // 2 - BUTTON_HEIGHT // 2,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
        )

    def isPossibleAssign(self, position, value):
        """Check if assigning value to the position results in a valid board"""

        # Check horizontal
        for i, x in enumerate(self.board[position[0], :]):
            if i != position[1] and x == value:
                return False

        # Check vertical
        for i, x in enumerate(self.board[:, position[1]]):
            if i != position[0] and x == value:
                return False

        # Check square
        square = [
            self.board[
                (position[0] // 3) * 3 + i,
                (position[1] // 3) * 3 + j
            ]
            for i in range(3) for j in range(3)
        ]
        for i, x in enumerate(square):
            if i != (position[0] % 3 * 3 + position[1] % 3) and x == value:
                return False

        return True

    def checkBoardValid(self):
        """Check if the(possibly incomplete) board is a valid sudoku board"""
        for i in range(9):
            for j in range(9):
                if self.board[i, j] == 0:
                    continue

                if not self.isPossibleAssign((i, j), self.board[i, j]):
                    return False

        return True


if __name__ == "__main__":
    board = np.array([
        [0, 0, 8, 0, 0, 2, 0, 0, 0],
        [0, 2, 0, 4, 0, 1, 0, 5, 0],
        [0, 0, 4, 0, 5, 0, 2, 0, 7],
        [4, 6, 0, 0, 7, 0, 0, 3, 0],
        [0, 0, 3, 5, 0, 9, 4, 0, 0],
        [0, 8, 0, 0, 3, 0, 0, 2, 5],
        [6, 0, 9, 0, 8, 0, 5, 0, 0],
        [0, 3, 0, 9, 0, 5, 0, 7, 0],
        [0, 0, 0, 1, 0, 0, 8, 0, 0]
    ])

    app = SudokuSolver(board)
    app.execute()
