import pygame
import numpy as np
import heapq

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GHOST_COLORS = [(255, 0, 0), (0, 255, 255), (255, 192, 203)]


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

class AStarPathfinder:
    def heuristic(self, a, b):
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
                next_pos = neighbor.grid_pos
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(end, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        return self._reconstruct_path(came_from, start, end) if end in came_from else []

    def _reconstruct_path(self, came_from, start, end):
        path = []
        current = end
        while current != start:
            path.append(current)
            current = came_from.get(current, start)
        path.reverse()
        return path


# Simple test for player + maze init
if _name_ == "_main_":
    maze = DynamicMaze()
    player1 = Player((255, 0, 0))
    pathfinder = AStarPathfinder()
    path = pathfinder.find_path((1,1), (6,6), maze)
    print("Sample path from (1,1) to (6,6):", path)
    print(f"Player 1 initialized with color {player1.color}")
    print(f"Pellets in maze: {maze.count_pellets()}")
