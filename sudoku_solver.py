import pygame
import numpy as np
from time import sleep


SCREEN_WIDTH = 480
SCREEN_HEIGHT = 480

BIG_LINE_WIDTH = 4
BIG_LINE_COLOR = (200, 200, 200)
BIG_LINE_OFFSET = 0

SMALL_LINE_WIDTH = 2
SMALL_LINE_COLOR = (150, 150, 150)
SMALL_LINE_OFFSET = 6

CHANGES_PER_SECOND = 50


class SudokuSolver():
    """The sudoku solver app class"""

    def __init__(self, board):
        """Create a sudoku problem based on the board (a numpy matrix)"""
        self.running = True
        pygame.init()
        pygame.display.set_caption("Sudoku Solver")

        self.define_grid()
        self.define_number_positions()
        self.board = board
        self.font = pygame.font.Font('ubuntu.ttf', 24)
        self.sleep_time = 1 / CHANGES_PER_SECOND

    def execute(self):
        """Start the app and run the game loop"""
        self.init()

        self.solve()

        while self.running:
            self.render()
            self.events()

        pygame.quit()

    def init(self):
        """Prepare running the game"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.running = True

    def solve(self):
        """Solve the puzzle updating the screen every step"""
        if not self.running:
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

            self.update_state(target, value)

            if self.solve():
                return True

        # In case of failure, reset and return False
        self.update_state(target, 0)

        return False

    def render(self):
        """Render the current image on the screen"""
        # Background
        self.screen.fill((20, 20, 20))

        # Grid
        for line in self.small_lines:
            pygame.draw.rect(self.screen, SMALL_LINE_COLOR, line)
        for line in self.big_lines:
            pygame.draw.rect(self.screen, BIG_LINE_COLOR, line)

        # Board
        for i in range(9):
            for j in range(9):
                if self.board[i, j] == 0:
                    continue

                text = self.font.render(
                    str(self.board[i, j]),
                    True,
                    (255, 255, 255)
                )
                textRect = text.get_rect()
                textRect.center = self.number_positions[i, j]
                self.screen.blit(text, textRect)

        if not self.running:
            pygame.draw.rect(
                self.screen,
                (0, 0, 0),
                pygame.Rect(
                    SCREEN_WIDTH // 2 - 100,
                    SCREEN_HEIGHT // 2 - 25,
                    200,
                    50
                )
            )
            text = self.font.render("Quitting...", True, (255, 255, 255))
            textRect = text.get_rect()
            textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.screen.blit(text, textRect)

        pygame.display.update()

    def events(self):
        """Deals with user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.sleep_time = 0
                return

    def update_state(self, position, value):
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
                SCREEN_HEIGHT - 2 * BIG_LINE_OFFSET
            ))

            # Horizontal line
            self.big_lines.append(pygame.Rect(
                BIG_LINE_OFFSET,
                i * SCREEN_HEIGHT // 3 - BIG_LINE_WIDTH // 2,
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
                SCREEN_HEIGHT - 2 * SMALL_LINE_OFFSET
            ))

            # Horizontal line
            self.small_lines.append(pygame.Rect(
                SMALL_LINE_OFFSET,
                i * SCREEN_HEIGHT // 9 - SMALL_LINE_WIDTH // 2,
                SCREEN_WIDTH - 2 * SMALL_LINE_OFFSET,
                SMALL_LINE_WIDTH
            ))

    def define_number_positions(self):
        """Define the positions the number will take on the board"""
        self.number_positions = np.array([
            [(
                int((j + 0.5) * SCREEN_HEIGHT // 9),
                int((i + 0.5) * SCREEN_WIDTH // 9)
            ) for j in range(9)]
            for i in range(9)
        ])

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
