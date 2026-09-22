import pygame
from src.vector import Vector2
from src.constants import *
import numpy as np

class Pellet(object):
	def __init__(self, row, column):
		self.name = PELLET
		self.position = Vector2(
			column * TILEWIDTH + MAZE_OFFSET_X + TILEWIDTH // 2,
			row * TILEHEIGHT + MAZE_OFFSET_Y + TILEHEIGHT // 2
		)
		self.color = WHITE

		self.radius = int(2 * TILEWIDTH / 16)
		self.collideRadius = int(2 * TILEWIDTH / 16)
		self.points = 10
		self.visible = True

	def render(self, screen):
		if self.visible:
			p = self.position
			pygame.draw.circle(screen, self.color, p.asInt(), self.radius)


class PowerPellet(Pellet):
	def __init__(self, row, column):
		Pellet.__init__(self, row, column)
		self.name = POWERPELLET
		self.radius = int(5 * TILEWIDTH / 16)
		self.points = 50
		self.flashTime = 0.2
		self.timer= 0

	def update(self, dt):
		self.timer += dt
		if self.timer >= self.flashTime:
			self.visible = not self.visible
			self.timer = 0



class PelletGroup(object):
	def __init__(self, pelletfile):
		self.pelletList = []
		self.powerpellets = []
		self.createPelletList(pelletfile)
		self.numEaten = 0

	def update(self, dt):
		for powerpellet in self.powerpellets:
			powerpellet.update(dt)

	def createPelletList(self, maze_grid):
		last = len(maze_grid[0]) - 2
		powergums = [(1, 1), (1, last), (last, 1), (last, last)]

		for y, row in enumerate(maze_grid):
			for x, cell in enumerate(row):
				if cell == 15:
					continue
				if (y, x) not in powergums:
					self.pelletList.append(Pellet(y, x))
				else:
					pp = PowerPellet(y, x)
					self.pelletList.append(pp)
					self.powerpellets.append(pp)

	def readPelletfile(self, textfile):
		return np.loadtxt(textfile, dtype='<U1')

	def isEmpty(self):
		if len(self.pelletList) == 0:
			return True
		return False

	def render(self, screen):
		for pellet in self.pelletList:
			pellet.render(screen)
