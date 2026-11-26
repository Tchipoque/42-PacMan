import random

import pygame
from pygame.locals import *

from typing import Any

from mazegenerator.mazegenerator import MazeGenerator
from src.constants import *
from src.fruit import Fruit
from src.ghosts import GhostGroup
from src.nodes import NodeGroup
from src.pauser import Pause
from src.pacman import Pacman
from src.pellets import PelletGroup
from src.sprites import LifeSprites
from src.text import TextGroup, Text
from src.highscores import load_highscores, add_highscore


class GameController:
    def __init__(self, config: dict[str, Any]) -> None:
        pygame.init()

        self.config = config
        self.max_levels = config.get("max_levels", 10)
        self.highscores = load_highscores()
        self.show_highscores = False
        self.show_instructions = False
        self.show_cheat_mode = False
        self.cheat_texts = []
        self.invincible = False
        self.ghost_frozen = False
        self.speed_boost = False

        try:
            self.maze_generator = MazeGenerator(
                size=tuple(config["maze_size"]),
                perfect=config["perfect"],
                entry_cell=tuple(config["entry_cell"]),
                exit_cell=tuple(config["exit_cell"]),
                seed=config["seed"],
            )
            self.maze_grid = self.maze_generator.maze

        except (ValueError, TypeError, IndexError) as error:
            raise RuntimeError(
                f"Could not generate maze: {error}"
            ) from error

        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.background_norm = None
        self.background_flash = None

        self.clock = pygame.time.Clock()
        self.fruit = None
        self.fruitCaptured = []

        self.pause = Pause(True)
        self.level = 0
        self.lives = 3
        self.score = 0
        self.used_seeds = set()
        self.level_time = config.get("level_time", 120)
        self.time_left = self.level_time
        self.player_name = ""
        self.entering_name = False
        self.game_won = False

        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)

        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0

        self.nodes = NodeGroup(self.maze_grid)

        self.title_screen = True
        self.titleText = None
        self. highscore_title = None
        self.highscore_texts = []
        self.menu_options = []
        self.menu_index = 0
        self.menu_texts = []
        self.instruction_texts = []

    def loadTitleScreen(self):
        self.title_screen = True
        self.setTitleScreenBackground()

        self.titleText = Text("PACMAN", YELLOW, 0, 10, 64)
        self.titleText.position.x = (
            self.screen.get_width() - self.titleText.label.get_width()
        ) / 2

        self.highscore_title = Text(
            "HIGHSCORES", WHITE, 0, 150, 24
        )
        self.highscore_title.position.x = (
            self.screen.get_width() - self.highscore_title.label.get_width()
        ) / 2

        self.highscore_texts = []

        for index, score in enumerate(self.highscores[:4]):
            text = Text(
                f"{index + 1}. {score['name']} - {score['score']}",
                WHITE,
                0,
                210 + index * 30,
                16
            )
            text.position.x = (
                self.screen.get_width() - text.label.get_width()
            ) / 2
            self.highscore_texts.append(text)

        self.menu_options = [
            "START GAME",
            "VIEW HIGHSCORES",
            "INSTRUCTIONS",
            "CHEAT MODE",
            "EXIT"
        ]
        self.menu_index = 0
        self.menu_texts = []

        for index, option in enumerate(self.menu_options):
            color = YELLOW if index == self.menu_index else WHITE

            text = Text(
                option,
                color,
                0,
                390 + index * 35,
                16
            )
            text.position.x = (
                self.screen.get_width() - text.label.get_width()
            ) / 2
            self.menu_texts.append(text)

    def restartGame(self):
        self.lives = 3
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.game_won = False

        self.fruitCaptured = []

        self.used_seeds.clear()
        self.startGame()

        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)

        self.loadTitleScreen()

    def savePlayerScore(self):
        """save the players score and return the main menu"""

        self.highscores = add_highscore(
            self.player_name,
            self.score
        )

        self.entering_name = False
        self.player_name = ""

        self.restartGame()

    def resetLevel(self):
        self.pause.paused = True
        self.time_left = self.level_time
        self.textgroup.updateTimer(self.time_left)
        self.pacman.reset()
        self.ghosts.reset()
        self.ghosts.setLevelSpeed(self.level)
        self.fruit = None
        self.textgroup.showText(READYTXT)

    def nextLevel(self):
        self.showEntities()
        self.level += 1

        if self.level >= self.max_levels:
            self.showVictoryScreen()
            return

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

        self.background_norm = self.render_walls(
            self.background_norm,
            self.maze_grid,
        )

        self.flashBG = False
        self.background = self.background_norm

    def startGame(self):
        self.title_screen = False
        self.pause.paused = False
        self.time_left = self.level_time

        if self.level == 0:
            seed = self.config["seed"]
            self.used_seeds.add(seed)
        else:
            seed = random.randint(50, 1000000)

            while seed in self.used_seeds:
                seed = random.randint(50, 1000000)

            self.used_seeds.add(seed)

        try:
            self.maze_generator = MazeGenerator(
                size=tuple(self.config["maze_size"]),
                perfect=self.config["perfect"],
                entry_cell=tuple(self.config["entry_cell"]),
                exit_cell=tuple(self.config["exit_cell"]),
                seed=seed,
            )
            self.maze_grid = self.maze_generator.maze

        except (ValueError, TypeError, IndexError) as error:
            raise RuntimeError(
                f"Could not generate maze: {error}"
            ) from error

        self.setBackground()

        self.nodes = NodeGroup(self.maze_grid)
        self.pacman = Pacman(self.nodes.pac_start())
        self.pellets = PelletGroup(self.maze_grid)

        rows = len(self.maze_grid)
        cols = len(self.maze_grid[0])

        self.ghosts = GhostGroup(
            self.nodes.getStartTempNode(),
            self.pacman,
        )

        self.ghosts.blinky.setStartNode(
            self.nodes.getNodeFromTiles(0, 0)
        )
        self.ghosts.pinky.setStartNode(
            self.nodes.getNodeFromTiles(cols - 1, 0)
        )
        self.ghosts.inky.setStartNode(
            self.nodes.getNodeFromTiles(0, rows - 1)
        )
        self.ghosts.clyde.setStartNode(
            self.nodes.getNodeFromTiles(cols - 1, rows - 1)
        )

        self.ghosts.setSpawnMode()
        self.ghosts.setLevelSpeed(self.level)

    def update(self):
        dt = self.clock.tick(60) / 1000.0

        if not self.title_screen:
            self.textgroup.update(dt)
            self.pellets.update(dt)

            if not self.pause.paused:
                self.time_left -= dt
                self.textgroup.updateTimer(self.time_left)

                if self.time_left <= 0:
                    self.time_left = 0
                    self.lives -= 1
                    self.lifesprites.removeImage()

                    if self.lives <= 0:
                        self.textgroup.showText(GAMEOVERTXT)
                        self.pause.setPause(
                            pauseTime=3,
                            func=self.startNameEntry,
                        )
                    else:
                        self.pause.setPause(
                            pauseTime=1,
                            func=self.resetLevel,
                        )

                if not self.ghost_frozen:
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
                pygame.quit()
                raise SystemExit

            elif event.type == KEYDOWN:
                if self.entering_name:
                    if event.key == K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == K_RETURN:
                        if self.player_name.strip():
                            self.savePlayerScore()
                    elif event.unicode.isalnum() or event.unicode == " ":
                        if len(self.player_name) < 10:
                            self.player_name += event.unicode
                    continue

                if not self.title_screen:
                    if self.pause.paused and event.key == K_ESCAPE:
                        self.pause.paused = True
                        self.pause.pauseTime = None
                        self.pause.func = None
                        self.textgroup.hideText()
                        self.showEntities()
                        self.loadTitleScreen()
                        continue

                    if event.key == K_i:
                        self.invincible = not self.invincible
                        print(
                            "Invincibility:",
                            "ON" if self.invincible else "OFF"
                        )
                    if event.key == K_k:
                        self.nextLevel()

                    if event.key == K_f:
                        self.ghost_frozen = not self.ghost_frozen
                        print(
                            "Ghosts Frozen:",
                            "ON" if self.ghost_frozen else "OFF"
                        )

                    if event.key == K_l:
                        self.lives += 1
                        self.lifesprites.addLife()
                        print("Extra Life! Lives:", self.lives)

                    if event.key == K_s:
                        self.speed_boost = not self.speed_boost

                        if self.speed_boost:
                            self.pacman.speed = self.pacman.normal_speed * 1.5
                        else:
                            self.pacman.speed = self.pacman.normal_speed

                        print(
                            "Speed Boost:",
                            "ON" if self.speed_boost else "OFF"
                        )

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
                    if event.key == K_UP:
                        self.menu_index = (
                            self.menu_index - 1
                        ) % len(self.menu_options)

                    elif event.key == K_DOWN:
                        self.menu_index = (
                            self.menu_index + 1
                        ) % len(self.menu_options)

                    for index, text in enumerate(self.menu_texts):
                        if index == self.menu_index:
                            text.color = YELLOW
                        else:
                            text.color = WHITE
                        text.createLabel()

                    if event.key == K_RETURN:
                        if self.menu_index == 0:
                            self.startGame()

                        elif self.menu_index == 1:
                            self.showHighscoresScreen()

                        elif self.menu_index == 2:
                            self.showIntructionsScreen()

                        elif self.menu_index == 3:
                            self.showCheatModeScreen()

                        elif self.menu_index == 4:
                            pygame.quit()
                            raise SystemExit

                    if self.show_highscores and event.key == K_ESCAPE:
                        self.show_highscores = False
                        self.loadTitleScreen()

                    if self.show_instructions and event.key == K_ESCAPE:
                        self.show_instructions = False

                    if self.show_cheat_mode and event.key == K_ESCAPE:
                        self.show_cheat_mode = False
                        self.loadTitleScreen()

    def checkGhostEvents(self):
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False

                    self.updateScore(ghost.points)

                    self.textgroup.addText(
                        str(ghost.points),
                        WHITE,
                        ghost.position.x,
                        ghost.position.y,
                        8,
                        time=1,
                    )

                    self.ghosts.updatePoints()
                    self.pause.setPause(
                        pauseTime=1,
                        func=self.showEntities,
                    )
                    ghost.startSpawn()

                elif ghost.mode.current is not SPAWN and not self.invincible:
                    if self.pacman.alive:
                        self.lives -= 1
                        self.lifesprites.removeImage()
                        self.pacman.die()
                        self.ghosts.hide()

                        if self.lives <= 0:
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(
                                pauseTime=3,
                                func=self.startNameEntry,
                            )
                        else:
                            self.pause.setPause(
                                pauseTime=3,
                                func=self.resetLevel,
                            )

    def checkFruitEvents(self):
        if self.pellets.numEaten in (10, 140):
            if self.fruit is None:
                self.fruit = Fruit(
                    self.pacman.position,
                    self.maze_grid,
                    self.nodes.nodesLUT,
                )

        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)

                self.textgroup.addText(
                    str(self.fruit.points),
                    WHITE,
                    self.fruit.position.x,
                    self.fruit.position.y,
                    8,
                    time=1,
                )

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
                self.pause.setPause(
                    pauseTime=3,
                    func=self.nextLevel,
                )

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

            self.pellets.render(self.screen)
            self.pacman.render(self.screen)
            self.ghosts.render(self.screen)
            self.textgroup.render(self.screen)

            for i in range(len(self.lifesprites.images)):
                x = self.lifesprites.images[i].get_width() * i
                y = SCREENHEIGHT - self.lifesprites.images[i].get_height()

                self.screen.blit(
                    self.lifesprites.images[i],
                    (x, y),
                )

        else:
            if self.entering_name:
                self.name_entry_title.render(self.screen)
                self.name_entry_text.setText(self.player_name)
                self.name_entry_text.render(self.screen)

            elif self.show_highscores:
                self.highscore_title.render(self.screen)

                for text in self.highscore_texts:
                    text.render(self.screen)

            elif self.show_instructions:
                for text in self.instruction_texts:
                    text.render(self.screen)

            elif self.show_cheat_mode:
                for text in self.cheat_texts:
                    text.render(self.screen)

            else:
                self.titleText.render(self.screen)
                self.highscore_title.render(self.screen)

                for text in self.highscore_texts:
                    text.render(self.screen)

                for text in self.menu_texts:
                    text.render(self.screen)

        pygame.display.update()
        self.clock.tick(60)

    def render_walls(self, screen, maze_grid, thickness=3):
        NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

        for y, row in enumerate(maze_grid):
            for x, cell in enumerate(row):
                px = MAZE_OFFSET_X + x * TILEWIDTH
                py = MAZE_OFFSET_Y + y * TILEHEIGHT

                if cell == 15:
                    pygame.draw.rect(
                        screen,
                        GREEN,
                        (px, py, TILEWIDTH, TILEHEIGHT),
                    )
                    continue

                if cell & NORTH:
                    pygame.draw.line(
                        screen,
                        BLUE,
                        (px, py),
                        (px + TILEWIDTH, py),
                        thickness,
                    )

                if cell & SOUTH:
                    pygame.draw.line(
                        screen,
                        BLUE,
                        (px, py + TILEHEIGHT),
                        (px + TILEWIDTH, py + TILEHEIGHT),
                        thickness,
                    )

                if cell & WEST:
                    pygame.draw.line(
                        screen,
                        BLUE,
                        (px, py),
                        (px, py + TILEHEIGHT),
                        thickness,
                    )

                if cell & EAST:
                    pygame.draw.line(
                        screen,
                        BLUE,
                        (px + TILEWIDTH, py),
                        (px + TILEWIDTH, py + TILEHEIGHT),
                        thickness,
                    )

        return screen

    def showHighscoresScreen(self):
        self.show_highscores = True
        self.highscores = load_highscores()

        self.highscore_title = Text(
            "HIGHSCORES", WHITE, 0, 100, 24
        )
        self.highscore_title.position.x = (
            self.screen.get_width() - self.highscore_title.label.get_width()
        ) / 2

        self.highscore_texts = []

        for index, score in enumerate(self.highscores[:10]):
            text = Text(
                f"{index + 1}. {score['name']} - {score['score']}",
                WHITE,
                0,
                160 + index * 30,
                16
            )
            text.position.x = (
                self.screen.get_width() - text.label.get_width()
            ) / 2
            self.highscore_texts.append(text)

    def showIntructionsScreen(self):
        self.show_instructions = True

        instructions = [
            "HOW TO PLAY",
            "ARROWS / WASD - MOVE",
            "EAT ALL THE PACGUMS",
            "AVOID THE GHOST",
            "SUPER PACGUMS MAKE GHOST VULNERABLE",
            "SPACE - PAUSE THE GAME",
            "ESQ - BACK TO MENU"
        ]

        self.instruction_texts = []

        for index, line in enumerate(instructions):
            color = YELLOW if index == 0 else WHITE

            text = Text(
                line,
                color,
                40,
                120 + index * 45,
                16
            )
            self.instruction_texts.append(text)

    def showCheatModeScreen(self):
        self.show_cheat_mode = True

        cheats = [
            "CHEAT MODE",
            "I - INVINCIBILITY",
            "K - SKIP LEVEL",
            "F - FREEZE GHOSTS",
            "L - EXTRA LIFE",
            "S - SPPED BOOST",
            "ESQ - BACK TO MENU"
        ]

        self.cheat_texts = []

        for index, line in enumerate(cheats):
            color = YELLOW if index == 0 else WHITE

            text = Text(
                line,
                color,
                40,
                120 + index * 45,
                16
            )
            self.cheat_texts.append(text)

    def startNameEntry(self):
        """start the player name entry screen"""

        self.entering_name = True
        self.player_name = ""
        self.title_screen = True
        self.game_won = False

        message = "GAME OVER - ENTER YOUR NAME"
        font = pygame.font.Font("PressStart2P-Regular.ttf", 16)
        text_width = font.size(message)[0]

        self.name_entry_title = Text(
            message,
            WHITE,
            (SCREENSIZE[0] - text_width) // 2,
            180,
            16
        )

        self.name_entry_text = Text(
            "",
            YELLOW,
            200,
            250,
            16
        )

    def showVictoryScreen(self):
        """Display the victory screen"""

        self.title_screen = True
        self.entering_name = True
        self.game_won = True
        self.player_name = ""

        victory_message = "CONGRATULATIONS! YOU WIN!"
        font = pygame.font.Font("PressStart2P-Regular.ttf", 16)
        text_width = font.size(victory_message)[0]

        self.name_entry_title = Text(
            victory_message,
            YELLOW,
            (SCREENSIZE[0] - text_width) // 2,
            180,
            16
        )

        self.name_entry_text = Text(
            "",
            WHITE,
            200,
            250,
            16
        )


if __name__ == "__main__":
    pygame.init()

    game = GameController()
    game.loadTitleScreen()

    while True:
        game.update()
