import pygame
import numpy as np

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class HexTile:
    def __init__(self, x, y, has_pellet=False, is_obstacle=False):
        self.grid_pos = (x, y)
        self.pixel_pos = (0, 0)
        self.pellets = 1 if has_pellet else 0
        self.obstacle = is_obstacle
        self.neighbors = []

class DynamicMaze:
    def __init__(self, size=8):
        self.size = size
        self.tiles = [[HexTile(x, y, has_pellet=(np.random.random() > 0.2),
                               is_obstacle=(np.random.random() < 0.1)) 
                      for y in range(size)] for x in range(size)]
        self.tiles[1][1].obstacle = False
        self.tiles[size-2][size-2].obstacle = False
        self._init_connections()

    def _init_connections(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
        for x in range(self.size):
            for y in range(self.size):
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        self.tiles[x][y].neighbors.append(self.tiles[nx][ny])

    def shift_tiles(self):
        self.tiles = np.rot90(self.tiles).tolist()
        self._init_connections()

    def count_pellets(self):
        return sum(tile.pellets for row in self.tiles for tile in row)


class Player:
    def _init_(self, color):
        self.tokens = []
        self.score = 0
        self.color = color
        self.home_position = (0, 0)
        self.lives = 5
        self.invincible = 0

# Simple test for player + maze init
if _name_ == "_main_":
    maze = DynamicMaze()
    player1 = Player((255, 0, 0))
    print(f"Player 1 initialized with color {player1.color}")
    print(f"Pellets in maze: {maze.count_pellets()}")
