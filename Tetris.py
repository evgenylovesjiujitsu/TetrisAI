import pygame
import random
import time

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_MARGIN = 1

# Screen dimensions
SIDEBAR_WIDTH = 200
SCREEN_WIDTH = GRID_WIDTH * (BLOCK_SIZE + GRID_MARGIN) + SIDEBAR_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT * (BLOCK_SIZE + GRID_MARGIN)

# Tetromino shapes
SHAPES = [
    # I piece
    [
        ['0000',
         '1111',
         '0000',
         '0000'],
        ['0010',
         '0010',
         '0010',
         '0010'],
    ],
    # J piece
    [
        ['100',
         '111',
         '000'],
        ['011',
         '010',
         '010'],
        ['000',
         '111',
         '001'],
        ['010',
         '010',
         '110'],
    ],
    # L piece
    [
        ['001',
         '111',
         '000'],
        ['010',
         '010',
         '011'],
        ['000',
         '111',
         '100'],
        ['110',
         '010',
         '010'],
    ],
    # O piece
    [
        ['011',
         '011',
         '000'],
    ],
    # S piece
    [
        ['011',
         '110',
         '000'],
        ['010',
         '011',
         '001'],
    ],
    # T piece
    [
        ['010',
         '111',
         '000'],
        ['010',
         '011',
         '010'],
        ['000',
         '111',
         '010'],
        ['010',
         '110',
         '010'],
    ],
    # Z piece
    [
        ['110',
         '011',
         '000'],
        ['001',
         '011',
         '010'],
    ]
]

# Colors for pieces
SHAPE_COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, MAGENTA, RED]

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape) % len(SHAPE_COLORS)]
        self.rotation = 0

    def get_layout(self):
        return self.shape[self.rotation]

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 25)
        self.reset_game()

    def reset_game(self):
        self.board = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.last_drop_time = time.time()
        self.drop_speed = 0.5  # seconds between automatic drops

    def new_piece(self):
        shape = random.choice(SHAPES)
        # Start from the middle top of the board
        return Tetromino(GRID_WIDTH // 2 - len(shape[0][0]) // 2, 0, shape)

    def valid_move(self, piece, x_offset=0, y_offset=0, rotation=None):
        future_rotation = rotation if rotation is not None else piece.rotation
        layout = piece.shape[future_rotation]
        
        for i, row in enumerate(layout):
            for j, cell in enumerate(row):
                if cell == '0':
                    continue
                
                x = piece.x + j + x_offset
                y = piece.y + i + y_offset
                
                if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                    return False
                    
                if y >= 0 and self.board[y][x] != BLACK:
                    return False
        
        return True

    def lock_piece(self, piece):
        layout = piece.get_layout()
        for i, row in enumerate(layout):
            for j, cell in enumerate(row):
                if cell == '1':
                    if piece.y + i < 0:
                        self.game_over = True
                        return
                    self.board[piece.y + i][piece.x + j] = piece.color
        
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        if not self.valid_move(self.current_piece):
            self.game_over = True

    def rotate_piece(self):
        next_rotation = (self.current_piece.rotation + 1) % len(self.current_piece.shape)
        if self.valid_move(self.current_piece, rotation=next_rotation):
            self.current_piece.rotation = next_rotation

    def clear_lines(self):
        lines_to_clear = []
        for i, row in enumerate(self.board):
            if all(cell != BLACK for cell in row):
                lines_to_clear.append(i)
        
        for line in lines_to_clear:
            del self.board[line]
            self.board.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        lines_cleared = len(lines_to_clear)
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            self.score += [0, 40, 100, 300, 1200][lines_cleared] * self.level
            self.level = min(10, 1 + self.lines_cleared // 10)
            self.drop_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)

    def draw_board(self):
        self.screen.fill(BLACK)
        
        # Draw board grid and pieces
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(
                    self.screen, 
                    self.board[y][x], 
                    [x * (BLOCK_SIZE + GRID_MARGIN), 
                     y * (BLOCK_SIZE + GRID_MARGIN), 
                     BLOCK_SIZE, 
                     BLOCK_SIZE]
                )
                
                # Draw grid lines
                pygame.draw.rect(
                    self.screen,
                    GRAY,
                    [x * (BLOCK_SIZE + GRID_MARGIN), 
                     y * (BLOCK_SIZE + GRID_MARGIN), 
                     BLOCK_SIZE, 
                     BLOCK_SIZE],
                    1
                )
        
        # Draw current piece
        if not self.game_over:
            self.draw_piece(self.current_piece)
        
        # Draw sidebar
        sidebar_x = GRID_WIDTH * (BLOCK_SIZE + GRID_MARGIN) + 10
        
        # Draw next piece preview
        next_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_text, [sidebar_x, 20])
        
        preview_x = sidebar_x + 30
        preview_y = 60
        
        for i, row in enumerate(self.next_piece.get_layout()):
            for j, cell in enumerate(row):
                if cell == '1':
                    pygame.draw.rect(
                        self.screen,
                        self.next_piece.color,
                        [preview_x + j * (BLOCK_SIZE // 2), 
                         preview_y + i * (BLOCK_SIZE // 2),
                         BLOCK_SIZE // 2, 
                         BLOCK_SIZE // 2]
                    )
        
        # Draw score and level
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, [sidebar_x, 160])
        
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, [sidebar_x, 200])
        
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, [sidebar_x, 240])
        
        if self.game_over:
            game_over_font = pygame.font.SysFont('Arial', 48)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)

    def draw_piece(self, piece):
        layout = piece.get_layout()
        for i, row in enumerate(layout):
            for j, cell in enumerate(row):
                if cell == '1':
                    pygame.draw.rect(
                        self.screen,
                        piece.color,
                        [(piece.x + j) * (BLOCK_SIZE + GRID_MARGIN),
                         (piece.y + i) * (BLOCK_SIZE + GRID_MARGIN),
                         BLOCK_SIZE,
                         BLOCK_SIZE]
                    )

    def run(self):
        running = True
        
        while running:
            current_time = time.time()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if not self.game_over:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            if self.valid_move(self.current_piece, x_offset=-1):
                                self.current_piece.x -= 1
                        
                        elif event.key == pygame.K_RIGHT:
                            if self.valid_move(self.current_piece, x_offset=1):
                                self.current_piece.x += 1
                        
                        elif event.key == pygame.K_DOWN:
                            if self.valid_move(self.current_piece, y_offset=1):
                                self.current_piece.y += 1
                        
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                        
                        elif event.key == pygame.K_SPACE:
                            # Hard drop
                            while self.valid_move(self.current_piece, y_offset=1):
                                self.current_piece.y += 1
                            self.lock_piece(self.current_piece)
                            self.last_drop_time = current_time
                
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.reset_game()
            
            # Auto drop
            if not self.game_over and current_time - self.last_drop_time > self.drop_speed:
                if self.valid_move(self.current_piece, y_offset=1):
                    self.current_piece.y += 1
                else:
                    self.lock_piece(self.current_piece)
                self.last_drop_time = current_time
            
            # Draw everything
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
    