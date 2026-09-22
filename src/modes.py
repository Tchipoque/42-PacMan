from src.constants import *

class MainMode(object):
	def __init__(self):
		self.timer = 0
		self.chase()

	def update(self, dt):
		self.timer += dt
		if self.timer >= self.time:
			if self.mode is SCATTER:
				self.chase()
			elif self.mode is CHASE:
				self.scatter()

	def scatter(self):
		self.mode = SCATTER
		self.time = 7
		self.timer = 0

	def chase(self):
		self.mode = CHASE
		self.time = 20
		self.timer = 0


class ModeController(object):
	def __init__(self, entity):
		self.timer = 0
		self.time = None
		self.mainmode = MainMode()
		self.current = self.mainmode.mode
		self.entity = entity

	def update(self, dt):
		self.mainmode.update(dt)

		if self.current is FREIGHT:
			self.timer += dt
			if self.timer >= self.time:
				self.time = None
				self.timer = 0
				self.entity.normalMode()
				self.current = self.mainmode.mode

		elif self.current is SPAWN:
			# keep counting the leftover freight time while heading home
			if self.time is not None:
				self.timer += dt
			atHome = self.entity.node == self.entity.spawnNode
			expired = self.time is None or self.timer >= self.time
			if atHome and expired:
				self.time = None
				self.timer = 0
				self.entity.normalMode()
				self.current = self.mainmode.mode

		else:   # SCATTER / CHASE
			self.current = self.mainmode.mode

	def setSpawnMode(self):
		if self.current is FREIGHT:
			# keep self.timer and self.time so the remaining freight
			# time keeps running while the eyes travel home
			self.current = SPAWN

	def setFreightMode(self):
		if self.current in [SCATTER, CHASE]:
			self.timer = 0
			self.time = 7
			self.current = FREIGHT
		elif self.current is FREIGHT:
			self.timer = 0      # eating a second power pellet refreshes the window
