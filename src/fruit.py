import pygame
from src.entity import Entity
from src.constants import *
from src.sprites import FruitSprites
import random

class Fruit(Entity):
		def __init__(self, node, maze_grid, nodes_list, level=0):
				self.maze = maze_grid
				self.nodes = nodes_list
				Entity.__init__(self, self.get_fruit_position(node))
				self.name = FRUIT
				self.color = GREEN
				self.lifespan = 5
				self.timer = 0
				self.destroy = False
				self.points = 100 + level*20
				self.setBetweenNodes(RIGHT)
				self.sprites = FruitSprites(self, level)

		def update(self, dt):
				self.timer += dt
				if self.timer >= self.lifespan:
						self.destroy = True

		def get_fruit_position(self, node):
			x = int((node.x - MAZE_OFFSET_X - TILEWIDTH // 2) // TILEWIDTH)
			y = int((node.y - MAZE_OFFSET_Y - TILEHEIGHT // 2) // TILEHEIGHT)
			options = []

			for row in range(y - 5, y + 6):
				for col in range(x - 5, x + 6):
					if not (0 <= row < len(self.maze)):
						continue
					if not (0 <= col < len(self.maze[row])):
						continue

					distance = abs(col - x) + abs(row - y)

					if distance == 0 or distance > 5:
						continue
					pixel_key = (MAZE_OFFSET_X + col * TILEWIDTH + TILEWIDTH // 2,
								 MAZE_OFFSET_Y + row * TILEHEIGHT + TILEHEIGHT // 2)
					if pixel_key in self.nodes:
						options.append(self.nodes[pixel_key])

			if options:
				return random.choice(options)

			return self.nodes[node]





