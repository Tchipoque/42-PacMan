import pygame
from pygame.locals import *
from src.constants import *
from src.pacman import Pacman
from src.nodes import NodeGroup
from src.pellets import PelletGroup
from src.ghosts import GhostGroup
from src.fruit import Fruit
from src.pauser import Pause
from src.text import TextGroup, Text  ########
from src.sprites import LifeSprites
from src.sprites import MazeSprites
from mazegenerator.mazegenerator import MazeGenerator
import random

class GameController(object):
	def __init__(self):
		pygame.init()
		self.maze_generator = MazeGenerator(seed=42)
		self.maze_grid = self.maze_generator.maze
		NROWS, NCOLS = len(self.maze_grid), len(self.maze_grid[0])
		self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
		self.background = None
		self.background_norm = None
		self.background_flash = None
		self.clock = pygame.time.Clock()
		self.fruit = None
		self.pause = Pause(True)
		self.level = 0
		self.lives = 3
		self.score = 0
		self.textgroup = TextGroup()
		self.lifesprites = LifeSprites(self.lives)
		self.flashBG = False
		self.flashTime = 0.2
		self.flashTimer = 0
		# self.fruitCaptured = []
		self.nodes = NodeGroup(self.maze_grid)


	def loadTitleScreen(self):
		self.title_screen = True
		self.setTitleScreenBackground()
		self.titleText = Text("PACMAN", YELLOW, 32, 10, 64)


	def restartGame(self):
		self.lives = 3
		self.level = 0
		self.pause.paused = True
		self.fruit = None
		self.startGame()
		self.score = 0
		self.textgroup.updateScore(self.score)
		self.textgroup.updateLevel(self.level)
		self.textgroup.showText(READYTXT)
		self.lifesprites.resetLives(self.lives)
		self.fruitCaptured = []
		self.loadTitleScreen()

	def resetLevel(self):
		self.pause.paused = True
		self.pacman.reset()
		self.ghosts.reset()
		self.fruit = None
		self.textgroup.showText(READYTXT)

	def nextLevel(self):
		self.showEntities()
		self.level += 1
		self.pause.paused = True
		self.startGame()
		self.textgroup.updateLevel(self.level)


	def setTitleScreenBackground(self):
		self.background = pygame.surface.Surface(SCREENSIZE).convert()
		self.background.fill(BLACK)


	def setBackground(self):
		self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
		self.background_norm.fill(BLACK)
		self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
		self.background_flash.fill(BLACK)
		self.background_norm = self.render_walls(self.background_norm, self.maze_grid)
		self.flashBG = False
		self.background = self.background_norm

	def startGame(self):
		self.title_screen = False
		self.pause.paused = False
		self.setBackground()
		if self.level == 0:
			seed = 42
		else:
			seed = random.randint(50, 99)
		self.maze_generator = MazeGenerator(seed=seed)
		self.maze_grid = self.maze_generator.maze
		self.nodes = NodeGroup(self.maze_grid)
		self.pacman = Pacman(self.nodes.pac_start())
		self.pellets = PelletGroup(self.maze_grid)

		rows = len(self.maze_grid)
		cols = len(self.maze_grid[0])

		self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)

		self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(0, 0))
		self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(cols - 1, 0))
		self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(0, rows - 1))
		self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(cols - 1, rows - 1))

		self.ghosts.setSpawnMode()

	def update(self):
		dt = self.clock.tick(60) / 1000.0
		if not self.title_screen:
			self.textgroup.update(dt)
			self.pellets.update(dt)
			if not self.pause.paused:
				self.ghosts.update(dt)
				if self.fruit is not None:
					self.fruit.update(dt)
				self.checkPelletEvents()
				self.checkGhostEvents()
				self.checkFruitEvents()

			if self.pacman.alive:
				if not self.pause.paused:
					self.pacman.update(dt)
			else:
				self.pacman.update(dt)

			if self.flashBG:
				self.flashTimer += dt
				if self.flashTimer >= self.flashTime:
					self.flashTimer = 0
					if self.background == self.background_norm:
						self.background = self.background_flash
					else:
						self.background = self.background_norm

			afterPauseMethod = self.pause.update(dt)
			if afterPauseMethod is not None:
				afterPauseMethod()

		self.checkEvents()
		self.render()

	def updateScore(self, points):
		self.score += points
		self.textgroup.updateScore(self.score)

	def checkEvents(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				exit()
			elif event.type == KEYDOWN:
				if not self.title_screen:
					if event.key == K_SPACE:
						if self.pacman.alive:
							self.pause.setPause(playerPaused=True)
							if not self.pause.paused:
								self.textgroup.hideText()
								self.showEntities()
							else:
								self.textgroup.showText(PAUSETXT)
								self.hideEntities()

				else:
					if event.key == K_RETURN:
						self.startGame()


	def checkGhostEvents(self):
		for ghost in self.ghosts:
			if self.pacman.collideGhost(ghost):
				if ghost.mode.current is FREIGHT:
					self.pacman.visible = False
					ghost.visible = False
					self.updateScore(ghost.points)
					self.textgroup.addText(str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1)
					self.ghosts.updatePoints()
					self.pause.setPause(pauseTime=1, func=self.showEntities)
					ghost.startSpawn()
				elif ghost.mode.current is not SPAWN:
					if self.pacman.alive:
						self.lives -=  1
						self.lifesprites.removeImage()
						self.pacman.die()
						self.ghosts.hide()
						if self.lives <= 0:
							self.textgroup.showText(GAMEOVERTXT)
							self.pause.setPause(pauseTime=3, func=self.restartGame)

						else:
							self.pause.setPause(pauseTime=3, func=self.resetLevel)

	def checkFruitEvents(self):
		if self.pellets.numEaten == 10 or self.pellets.numEaten == 140:
			if self.fruit is None:
				self.fruit = Fruit(self.pacman.position, self.maze_grid, self.nodes.nodesLUT)
		if self.fruit is not None:
			if self.pacman.collideCheck(self.fruit):
				self.updateScore(self.fruit.points)
				self.textgroup.addText(str(self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8, time=1)
				fruitCaptured = False
				for fruit in self.fruitCaptured:
					if fruit.get_offset() == self.fruit.image.get_offset():
						fruitCaptured = True
						break
				if not fruitCaptured:
					self.fruitCaptured.append(self.fruit.image)
				self.fruit = None
			elif self.fruit.destroy:
				self.fruit = None

	def checkPelletEvents(self):
		pellet = self.pacman.eatPellets(self.pellets.pelletList)
		if pellet:
			self.pellets.numEaten += 1
			self.updateScore(pellet.points)
			self.pellets.pelletList.remove(pellet)
			if pellet.name == POWERPELLET:
				self.ghosts.startFreight()
			if self.pellets.isEmpty():
				self.flashBG = True
				self.hideEntities()
				self.pause.setPause(pauseTime=3, func=self.nextLevel)

	def showEntities(self):
		self.pacman.visible = True
		self.ghosts.show()

	def hideEntities(self):
		self.pacman.visible = False
		self.ghosts.hide()

	def render(self):
		self.screen.fill(BLACK)

		self.screen.blit(self.background, (0, 0))

		if not self.title_screen:
			if self.fruit is not None:
				self.fruit.render(self.screen)
			# self.nodes.render(self.screen)
			self.pellets.render(self.screen)
			self.pacman.render(self.screen)
			self.ghosts.render(self.screen)
			self.textgroup.render(self.screen)
			for i in range(len(self.lifesprites.images)):
				x = self.lifesprites.images[i].get_width() * i
				y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
				self.screen.blit(self.lifesprites.images[i], (x, y))

		# 	for i in range(len(self.fruitCaptured)):
		# 		x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i+1)
		# 		y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
		# 		self.screen.blit(self.fruitCaptured[i], (x, y))
		else:
			self.titleText.render(self.screen)

		pygame.display.update()
		self.clock.tick(60)

	def render_walls(self, screen, maze_grid, thickness=3):
		NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
		for y, row in enumerate(maze_grid):
				for x, cell in enumerate(row):
						px = MAZE_OFFSET_X + x * TILEWIDTH
						py = MAZE_OFFSET_Y + y * TILEHEIGHT
						if cell == 15:
								pygame.draw.rect(screen, GREEN, (px, py, TILEWIDTH, TILEHEIGHT))
								continue
						if cell & NORTH:
								pygame.draw.line(screen, BLUE, (px, py), (px+TILEWIDTH, py), thickness)
						if cell & SOUTH:
								pygame.draw.line(screen, BLUE, (px, py+TILEHEIGHT), (px+TILEWIDTH, py+TILEHEIGHT), thickness)
						if cell & WEST:
								pygame.draw.line(screen, BLUE, (px, py), (px, py+TILEHEIGHT), thickness)
						if cell & EAST:
								pygame.draw.line(screen, BLUE, (px+TILEWIDTH, py), (px+TILEWIDTH, py+TILEHEIGHT), thickness)
		return screen

if __name__ == "__main__":
	pygame.init()
	game = GameController()
	game.loadTitleScreen()
	while True:
		game.update()
