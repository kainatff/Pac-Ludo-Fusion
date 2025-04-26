import pygame
import numpy as np
import heapq
import tensorflow as tf
from pygame.locals import *
import random

# Initialize Pygame and colors
pygame.init()
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)  # For destination
GHOST_COLORS = [(255, 0, 0), (0, 255, 255), (255, 192, 203)]  # Blinky, Inky, Pinky

# =====================
# Core Game Classes
# =====================

class HexTile:
    def __init__(self, x, y, has_pellet=False, is_obstacle=False):
        self.grid_pos = (x, y)
        self.pixel_pos = (0, 0)
        self.pellets = 1 if has_pellet else 0
        self.obstacle = is_obstacle
        self.neighbors = []

class DynamicMaze:
    def __init__(self, size=15):  # Larger maze size
        self.size = size
        # Fewer obstacles and more pellets
        self.tiles = [[HexTile(x, y, has_pellet=(np.random.random() > 0.3), 
                      is_obstacle=(np.random.random() < 0.15))  # More open space
                     for y in range(size)] for x in range(size)]
        # Ensure starting positions are clear
        self.tiles[1][1].obstacle = False
        self.tiles[size-2][size-2].obstacle = False
        self._init_connections()
        
    def _init_connections(self):
        # Connect hexagonal neighbors
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
        for x in range(self.size):
            for y in range(self.size):
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        self.tiles[x][y].neighbors.append(self.tiles[nx][ny])

    def shift_tiles(self):
        # Simple rotation implementation
        self.tiles = np.rot90(self.tiles).tolist()
        self._init_connections()
        
    def count_pellets(self):
        return sum(tile.pellets for row in self.tiles for tile in row)
    
    def get_random_position(self):
        """Get a random non-obstacle position"""
        while True:
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            if not self.tiles[x][y].obstacle:
                return (x, y)

class Player:
    def __init__(self, color):
        self.tokens = []
        self.score = 0
        self.color = color
        self.home_position = (0, 0)
        self.lives = 5  # More lives for easier gameplay
        self.invincible = 0  # Invincibility frames after respawn
        self.pellets_collected = 0  # Track pellets for bonuses

class Ghost:
    def __init__(self, ai_type, color_index):
        self.ai_type = ai_type
        self.color = GHOST_COLORS[color_index]
        self.position = (0, 0)
        self.ai = self._init_ai()
        self.speed = 0.5  # Slower movement speed
        
    def _init_ai(self):
        if self.ai_type == 'minimax':
            return MinimaxAI(depth=1)  # Reduced difficulty
        elif self.ai_type == 'a_star':
            return AStarPathfinder()
        elif self.ai_type == 'rl':
            return QLearningAI()
        return None
        
    def make_move(self, game_state):
        # Only move every other frame (slower movement)
        if pygame.time.get_ticks() % 2 == 0 and self.ai:
            return self.ai.decide_move(game_state, self.position)
        return self.position

class PopUpText:
    def __init__(self, text, position, color, duration=60, size=24):
        self.text = text
        self.position = position
        self.color = color
        self.duration = duration
        self.timer = 0
        self.size = size
        self.font = pygame.font.SysFont('Arial', size)
        self.alpha = 255
        
    def update(self):
        self.timer += 1
        # Move up slightly
        self.position = (self.position[0], self.position[1] - 1)
        # Fade out
        if self.timer > self.duration // 2:
            self.alpha = max(0, self.alpha - 10)
        return self.timer < self.duration
        
    def draw(self, screen):
        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(self.alpha)
        screen.blit(text_surface, self.position)

# =====================
# AI Implementations
# =====================

class AStarPathfinder:
    @staticmethod
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def find_path(self, start, end, maze):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {start: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == end:
                break
                
            for neighbor in maze.tiles[current[0]][current[1]].neighbors:
                if neighbor.obstacle:
                    continue
                next_pos = (neighbor.grid_pos[0], neighbor.grid_pos[1])
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(end, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
                    
        return self._reconstruct_path(came_from, start, end) if end in came_from else []
    
    def _reconstruct_path(self, came_from, start, end):
        current = end
        path = []
        while current != start:
            path.append(current)
            current = came_from.get(current, start)
        path.reverse()
        return path
    
    def decide_move(self, game_state, current_pos):
        if not game_state['players'][0].tokens:
            return current_pos
            
        player_pos = game_state['players'][0].tokens[0].grid_pos
        path = self.find_path(current_pos, player_pos, game_state['maze'])
        return path[0] if path else current_pos

class MinimaxAI:
    def __init__(self, depth=1):  # Reduced depth for easier gameplay
        self.depth = depth
        
    def decide_move(self, game_state, current_pos):
        if not game_state['players'][0].tokens:
            return current_pos
            
        best_move = current_pos
        best_value = -np.inf
        current_tile = game_state['maze'].tiles[current_pos[0]][current_pos[1]]
        
        for neighbor in current_tile.neighbors:
            if neighbor.obstacle:
                continue
            value = self._minimax(game_state, neighbor.grid_pos, self.depth-1, False)
            if value > best_value:
                best_value = value
                best_move = neighbor.grid_pos
        return best_move
    
    def _minimax(self, state, pos, depth, maximizing):
        if depth == 0:
            return self._evaluate(state, pos)
            
        current_tile = state['maze'].tiles[pos[0]][pos[1]]
        
        if maximizing:
            max_eval = -np.inf
            for neighbor in current_tile.neighbors:
                if neighbor.obstacle:
                    continue
                eval = self._minimax(state, neighbor.grid_pos, depth-1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = np.inf
            for neighbor in current_tile.neighbors:
                if neighbor.obstacle:
                    continue
                eval = self._minimax(state, neighbor.grid_pos, depth-1, True)
                min_eval = min(min_eval, eval)
            return min_eval
    
    def _evaluate(self, state, pos):
        if not state['players'][0].tokens:
            return 0
            
        player_pos = state['players'][0].tokens[0].grid_pos
        distance = abs(pos[0]-player_pos[0]) + abs(pos[1]-player_pos[1])
        return -distance  # Negative because we want to minimize distance

class QLearningAI:
    def __init__(self):
        self.model = tf.keras.Sequential([
            tf.keras.Input(shape=(6,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(4)
        ])
        self.model.compile(optimizer='adam', loss='mse')
        
    def decide_move(self, game_state, current_pos):
        if not game_state['players'][0].tokens:
            return current_pos
            
        state_vector = self._process_state(game_state, current_pos)
        q_values = self.model.predict(state_vector[np.newaxis], verbose=0)
        action = np.argmax(q_values[0])
    
        # Map index to direction
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        dx, dy = directions[action]
    
        new_pos = (current_pos[0] + dx, current_pos[1] + dy)
    
        # Ensure new position is within bounds and not obstacle
        if (0 <= new_pos[0] < game_state['maze'].size and
            0 <= new_pos[1] < game_state['maze'].size and
            not game_state['maze'].tiles[new_pos[0]][new_pos[1]].obstacle):
            return new_pos
        return current_pos
    
    def _process_state(self, state, current_pos):
        player_pos = state['players'][0].tokens[0].grid_pos if state['players'][0].tokens else (0,0)
        pellets_remaining = state['maze'].count_pellets()
        return np.array([
            current_pos[0], current_pos[1],
            player_pos[0], player_pos[1],
            state['turn_count'] % 10,
            pellets_remaining
        ])

# =====================
# Game Implementation
# =====================
class GameController:
    def __init__(self):
        pygame.init()  # Ensure pygame is initialized
        self.screen = pygame.display.set_mode((1000, 800))  # Larger window
        pygame.display.set_caption("Hex Maze Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 40, bold=True)
        
        # Create simple ghost images with different colors
        self.ghost_images = []
        for color in GHOST_COLORS:
            surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (20, 20), 15)
            pygame.draw.rect(surf, color, (5, 20, 30, 15))
            for i in range(5):
                pygame.draw.circle(surf, color, (5 + i*7, 35), 4)
            pygame.draw.circle(surf, WHITE, (14, 15), 5)
            pygame.draw.circle(surf, WHITE, (26, 15), 5)
            pygame.draw.circle(surf, BLACK, (14, 15), 2)
            pygame.draw.circle(surf, BLACK, (26, 15), 2)
            self.ghost_images.append(surf)
        
        self.maze = DynamicMaze()
        self.players = [Player(RED), Player(BLUE)]
        self.ghosts = [
            Ghost('minimax', 0),  # Blinky (red)
            Ghost('a_star', 1),   # Inky (cyan)
            Ghost('rl', 2)        # Pinky (pink)
        ]
        self._init_positions()
        self.state = "home"  # home or game
        self.last_shift_time = 0
        self.game_time = 0
        self.game_over = False
        self.victory = False
        self.last_move_time = 0
        self.move_delay = 100  # milliseconds between moves
        self.popups = []  # For displaying animated text
        self.destination = None  # Destination tile
        self.set_new_destination()  # Initialize destination

    def set_new_destination(self):
        """Set a new random destination for the player to reach"""
        if self.maze:
            # Get a position that's not the player's current position
            while True:
                new_dest = self.maze.get_random_position()
                if self.players[0].tokens and new_dest != self.players[0].tokens[0].grid_pos:
                    self.destination = new_dest
                    break

    def _init_positions(self):
        # Player 1 starts at top-left, Player 2 at bottom-right
        for idx, player in enumerate(self.players):
            start_x = 1 if idx == 0 else self.maze.size - 2
            start_y = 1 if idx == 0 else self.maze.size - 2
            player.home_position = (start_x, start_y)
            player.tokens = [self.maze.tiles[start_x][start_y]]
            player.invincible = 60  # 2 seconds of invincibility at start

        # Ghosts start near center but not too close to player
        center = self.maze.size // 2
        ghost_positions = [
            (center+1, center+1),
            (center-1, center+1),
            (center+1, center-1)
        ]
        for i, ghost in enumerate(self.ghosts):
            ghost.position = ghost_positions[i]

    def hex_to_pixel(self, pos, center=False):
        """Convert hex grid coordinates to pixel coordinates"""
        tile_size = 40
        offset_x, offset_y = 100, 80
        px = pos[0] * tile_size + offset_x
        py = pos[1] * tile_size + offset_y
        if center:
            px += tile_size // 2
            py += tile_size // 2
        return (px, py)

    def draw_maze(self, highlight_path=False):
        """Draw the maze with optional path highlighting"""
        tile_size = 40
        offset_x, offset_y = 100, 80
        
        for x in range(self.maze.size):
            for y in range(self.maze.size):
                tile = self.maze.tiles[x][y]
                px, py = self.hex_to_pixel((x, y))
                tile.pixel_pos = (px, py)
                
                # Draw tile with gradient background
                base_color = (30, 30, 50)  # Dark blue-gray
                if tile.obstacle:
                    color = (20, 20, 30)  # Darker for obstacles
                else:
                    # Slight gradient based on position
                    color = (
                        min(80, base_color[0] + x * 2),
                        min(80, base_color[1] + y * 2),
                        base_color[2]
                    )
                
                pygame.draw.rect(self.screen, color, (px, py, tile_size-2, tile_size-2))
                
                # Draw pellet if exists (more visible)
                if tile.pellets > 0:
                    pellet_color = (255, 255, 100)  # Brighter yellow
                    pygame.draw.circle(self.screen, pellet_color, 
                                     (px + tile_size//2, py + tile_size//2), 5)
                
                # Draw destination if this is the destination tile
                if self.destination and (x, y) == self.destination:
                    dest_size = tile_size // 2
                    pygame.draw.rect(self.screen, PURPLE, 
                                   (px + (tile_size - dest_size)//2, 
                                    py + (tile_size - dest_size)//2,
                                    dest_size, dest_size))

    def show_tutorial(self):
        running = True
        step = 0
        steps = [
            "Welcome to Hex Chase!",
            "Use WASD keys to move your player (RED CIRCLE)",
            "Collect the yellow pellets to earn points and lives",
            "Avoid the ghosts! They will chase you",
            "Reach the PURPLE destination to win the level",
            "The maze rotates every 15 seconds - watch out!",
            "Good luck!"
        ]

        player_pos = [1, 1]  # Make this mutable for movement
        ghost_pos = (6, 6)
        test_maze = DynamicMaze()  # Create a fresh maze for tutorial
        test_destination = (test_maze.size-2, test_maze.size-2)

        while running:
            self.screen.fill(BLACK)
            
            # Draw the tutorial maze
            tile_size = 40
            offset_x, offset_y = 100, 80
            
            for x in range(test_maze.size):
                for y in range(test_maze.size):
                    tile = test_maze.tiles[x][y]
                    px = x * tile_size + offset_x
                    py = y * tile_size + offset_y
                    
                    # Draw tile
                    color = (40, 40, 60) if not tile.obstacle else (20, 20, 30)
                    pygame.draw.rect(self.screen, color, (px, py, tile_size-2, tile_size-2))
                    
                    # Draw pellet if exists
                    if tile.pellets > 0:
                        pygame.draw.circle(self.screen, YELLOW, (px + tile_size//2, py + tile_size//2), 5)
                    
                    # Draw destination
                    if (x, y) == test_destination:
                        dest_size = tile_size // 2
                        pygame.draw.rect(self.screen, PURPLE, 
                                       (px + (tile_size - dest_size)//2, 
                                        py + (tile_size - dest_size)//2,
                                        dest_size, dest_size))

            # Draw tutorial player (red)
            pygame.draw.circle(self.screen, RED, 
                             (player_pos[0] * tile_size + offset_x + tile_size//2, 
                              player_pos[1] * tile_size + offset_y + tile_size//2), 
                             15)

            # Draw one ghost
            ghost_img = self.ghost_images[0]
            ghost_rect = ghost_img.get_rect(
                center=(ghost_pos[0] * tile_size + offset_x + tile_size//2, 
                       ghost_pos[1] * tile_size + offset_y + tile_size//2))
            self.screen.blit(ghost_img, ghost_rect)

            # Display step instructions
            pygame.draw.rect(self.screen, (50, 50, 80), (100, 550, 800, 150))
            text = self.font.render(steps[step], True, WHITE)
            self.screen.blit(text, (120, 570))

            # Continue prompt
            if step < len(steps) - 1:
                prompt = self.font.render("Press SPACE to continue...", True, WHITE)
            else:
                prompt = self.font.render("Press ENTER to start!", True, WHITE)
            self.screen.blit(prompt, (120, 610))

            pygame.display.flip()
            self.clock.tick(60)

            # Handle movement during the "try moving" step
            if step == 2:
                keys = pygame.key.get_pressed()
                if keys[K_w] and player_pos[1] > 0 and not test_maze.tiles[player_pos[0]][player_pos[1]-1].obstacle:
                    player_pos[1] -= 1
                if keys[K_s] and player_pos[1] < test_maze.size-1 and not test_maze.tiles[player_pos[0]][player_pos[1]+1].obstacle:
                    player_pos[1] += 1
                if keys[K_a] and player_pos[0] > 0 and not test_maze.tiles[player_pos[0]-1][player_pos[1]].obstacle:
                    player_pos[0] -= 1
                if keys[K_d] and player_pos[0] < test_maze.size-1 and not test_maze.tiles[player_pos[0]+1][player_pos[1]].obstacle:
                    player_pos[0] += 1

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE and step < len(steps) - 1:
                        step += 1
                    elif event.key == K_RETURN and step == len(steps) - 1:
                        running = False

    def _draw_homepage(self):
        title_text = self.title_font.render("Hex Maze Chase", True, YELLOW)
        instruction_lines = [
            "How to Play:",
            "- Use W A S D to move your player (RED)",
            "- Collect pellets on the tiles (YELLOW)",
            "- Reach the PURPLE destination to win",
            "- Avoid the ghosts:",
            "  - RED: Minimax (predicts your moves)",
            "  - CYAN: A* (efficient pathfinding)",
            "  - PINK: RL (learning AI)",
            "- Tiles rotate every 15 seconds",
            "- You have 5 lives",
            "",
            "Collect pellets to gain extra lives!"
        ]
        self.screen.blit(title_text, (500 - title_text.get_width() // 2, 50))

        for idx, line in enumerate(instruction_lines):
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (150, 150 + idx * 30))

        # Draw Start button
        self._start_button_rect = pygame.Rect(400, 600, 200, 50)
        pygame.draw.rect(self.screen, BLUE, self._start_button_rect, border_radius=12)
        button_text = self.font.render("Start Game", True, WHITE)
        self.screen.blit(button_text, (
            self._start_button_rect.centerx - button_text.get_width() // 2,
            self._start_button_rect.centery - button_text.get_height() // 2
        ))

    def _handle_input(self, event):
        player = self.players[0]
        if not player.tokens or self.game_over:
            return

        current_tile = player.tokens[0]
        x, y = current_tile.grid_pos

        # Corrected key mappings for WASD
        key_map = {
            K_w: (-1, 0),  # Up (W)
            K_s: (1, 0),   # Down (S)
            K_a: (0, -1),  # Left (A)
            K_d: (0, 1),   # Right (D)
        }

        if event.key in key_map:
            dx, dy = key_map[event.key]
            new_x, new_y = x + dx, y + dy

            if 0 <= new_x < self.maze.size and 0 <= new_y < self.maze.size:
                new_tile = self.maze.tiles[new_x][new_y]
                if not new_tile.obstacle:
                    player.tokens[0] = new_tile
                    self._check_pellet_collision(new_tile)
                    self._check_destination_reached(new_tile)

    def _check_pellet_collision(self, tile):
        if tile.pellets > 0:
            tile.pellets = 0
            player = self.players[0]
            player.score += 10
            player.pellets_collected += 1
            
            # Show +10 score popup
            pos = self.hex_to_pixel(tile.grid_pos, center=True)
            self.popups.append(PopUpText("+10", (pos[0]-10, pos[1]-20), GREEN))
            
            # Check for 5 pellet bonus
            if player.pellets_collected % 5 == 0:
                pos = self.hex_to_pixel(tile.grid_pos, center=True)
                player.score += 5
                
            # Check for 20 pellet life bonus
            if player.pellets_collected % 50 == 0:
                pos = self.hex_to_pixel(tile.grid_pos, center=True)
                self.popups.append(PopUpText("Life Up!", (pos[0]-30, pos[1]-60), RED, 90, 32))
                player.lives += 1

    def _check_destination_reached(self, tile):
        """Check if player reached the destination"""
        if self.destination and tile.grid_pos == self.destination:
            # Player reached destination - level complete!
            self.victory = True
            self.game_over = True
            
            # Add victory score bonus
            self.players[0].score += 100
            pos = self.hex_to_pixel(tile.grid_pos, center=True)
            self.popups.append(PopUpText("Level Complete!", (pos[0]-80, pos[1]-80), PURPLE, 120, 36))

    def _check_ghost_collisions(self):
        player = self.players[0]
        if not player.tokens or player.invincible > 0:
            return

        player_pos = player.tokens[0].grid_pos
        for ghost in self.ghosts:
            if ghost.position == player_pos:
                player.lives -= 1
                if player.lives <= 0:
                    self.game_over = True
                    self.victory = False
                else:
                    # Respawn player with invincibility
                    player.tokens[0] = self.maze.tiles[player.home_position[0]][player.home_position[1]]
                    player.invincible = 90  # 3 seconds of invincibility
                break

    def _update_game(self, dt, current_time):
        self.game_time = current_time
        
        # Shift maze every 15 seconds (slower)
        if current_time - self.last_shift_time > 15000:
            self.maze.shift_tiles()
            self.last_shift_time = current_time
            # After shifting, we might want to set a new destination
            # But for now, keep the same destination (it moves with the maze)
            
            # Show shift warning
            warning = PopUpText("Maze Shifted!", (400, 300), YELLOW, 60, 32)
            self.popups.append(warning)

        game_state = {
            'maze': self.maze,
            'players': self.players,
            'ghosts': self.ghosts,
            'turn_count': current_time,
            'destination': self.destination
        }

        # Update ghosts
        for ghost in self.ghosts:
            new_pos = ghost.make_move(game_state)
            # Only move if target tile is valid
            if 0 <= new_pos[0] < self.maze.size and 0 <= new_pos[1] < self.maze.size:
                if not self.maze.tiles[new_pos[0]][new_pos[1]].obstacle:
                    ghost.position = new_pos

        self._check_ghost_collisions()
        
        # Decrease invincibility timer
        if self.players[0].invincible > 0:
            self.players[0].invincible -= 1
        
        # Update popups
        self.popups = [popup for popup in self.popups if popup.update()]

    def _draw_interface(self, current_time):
        self.draw_maze()

        # Draw player
        player = self.players[0]
        if player.tokens:
            x, y = player.tokens[0].grid_pos
            px, py = self.maze.tiles[x][y].pixel_pos
            # Flash if invincible
            if player.invincible <= 0 or (player.invincible // 10) % 2 == 0:
                pygame.draw.circle(self.screen, player.color, (px + 20, py + 20), 15)

        # Draw ghosts
        for i, ghost in enumerate(self.ghosts):
            x, y = ghost.position
            tile = self.maze.tiles[x][y]
            ghost_rect = self.ghost_images[i].get_rect(center=(tile.pixel_pos[0] + 20, 20 + tile.pixel_pos[1]))
            self.screen.blit(self.ghost_images[i], ghost_rect)

        # Draw popups
        for popup in self.popups:
            popup.draw(self.screen)

        # Draw HUD
        score_text = self.font.render(f"Score: {self.players[0].score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.players[0].lives}", True, WHITE)
        pellets_text = self.font.render(f"Pellets: {self.maze.count_pellets()}", True, WHITE)
        time_text = self.font.render(f"Time: {(current_time - self.game_time)//1000}s", True, WHITE)
        
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(lives_text, (20, 50))
        self.screen.blit(pellets_text, (20, 80))
        self.screen.blit(time_text, (20, 110))

        # Draw invincibility indicator
        if self.players[0].invincible > 0:
            invinc_text = self.font.render(f"Invincible: {self.players[0].invincible//30}s", True, GREEN)
            self.screen.blit(invinc_text, (20, 140))

        # Draw destination indicator
        if self.destination:
            dest_text = self.font.render("Destination: PURPLE square", True, PURPLE)
            self.screen.blit(dest_text, (20, 170))

        # Draw game over/victory message
        if self.game_over:
            message = "You Win!" if self.victory else "Game Over!"
            color = GREEN if self.victory else RED
            game_over_text = self.title_font.render(message, True, color)
            restart_text = self.font.render("Press R to restart", True, WHITE)
            
            # Semi-transparent overlay
            s = pygame.Surface((1000, 800), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            self.screen.blit(s, (0, 0))
            
            self.screen.blit(game_over_text, 
                           (500 - game_over_text.get_width()//2, 
                            300 - game_over_text.get_height()//2))
            self.screen.blit(restart_text,
                           (500 - restart_text.get_width()//2,
                            350 - restart_text.get_height()//2))
            
            final_score = self.font.render(f"Final Score: {self.players[0].score}", True, WHITE)
            self.screen.blit(final_score,
                           (500 - final_score.get_width()//2,
                            400 - final_score.get_height()//2))

    def show_homepage(self):
        running = True
        while running:
            self.screen.fill(BLACK)
            self._draw_homepage()
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                if event.type == MOUSEBUTTONDOWN:
                    if hasattr(self, '_start_button_rect') and self._start_button_rect.collidepoint(event.pos):
                        running = False
            
            self.clock.tick(30)

    def run_game(self):
        # Show homepage first
        self.show_homepage()
        
        # Then show tutorial
        self.show_tutorial()
        
        # Then start main game
        self.state = "game"
        self.game_time = pygame.time.get_ticks()
        self.last_shift_time = self.game_time
        self.last_move_time = self.game_time
        
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            dt = self.clock.tick(60)
            
            # Handle continuous key presses for movement
            keys = pygame.key.get_pressed()
            if self.state == "game" and not self.game_over:
                player = self.players[0]
                if player.tokens:
                    current_tile = player.tokens[0]
                    x, y = current_tile.grid_pos
                    
                    # Check for key presses and move one tile at a time
                    if keys[K_w] and y > 0 and not self.maze.tiles[x][y-1].obstacle:
                        player.tokens[0] = self.maze.tiles[x][y-1]
                        self._check_pellet_collision(self.maze.tiles[x][y-1])
                        self._check_destination_reached(self.maze.tiles[x][y-1])
                    elif keys[K_s] and y < self.maze.size-1 and not self.maze.tiles[x][y+1].obstacle:
                        player.tokens[0] = self.maze.tiles[x][y+1]
                        self._check_pellet_collision(self.maze.tiles[x][y+1])
                        self._check_destination_reached(self.maze.tiles[x][y+1])
                    elif keys[K_a] and x > 0 and not self.maze.tiles[x-1][y].obstacle:
                        player.tokens[0] = self.maze.tiles[x-1][y]
                        self._check_pellet_collision(self.maze.tiles[x-1][y])
                        self._check_destination_reached(self.maze.tiles[x-1][y])
                    elif keys[K_d] and x < self.maze.size-1 and not self.maze.tiles[x+1][y].obstacle:
                        player.tokens[0] = self.maze.tiles[x+1][y]
                        self._check_pellet_collision(self.maze.tiles[x+1][y])
                        self._check_destination_reached(self.maze.tiles[x+1][y])

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif self.state == "game":
                    if event.type == KEYDOWN:
                        if self.game_over and event.key == K_r:
                            self.__init__()  # Reset game
                            self.state = "game"
                            self.game_time = current_time
                            self.last_shift_time = current_time
                            self.last_move_time = current_time

            self.screen.fill(BLACK)
            if self.state == "game":
                if not self.game_over:
                    self._update_game(dt, current_time)
                self._draw_interface(current_time)

            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = GameController()
    game.run_game()