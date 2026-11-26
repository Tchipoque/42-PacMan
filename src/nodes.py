import pygame
from src.vector import Vector2
from src.constants import *
import numpy as np


class Node(object):
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.neighbors = {UP: None, DOWN: None,
                          LEFT: None, RIGHT: None, PORTAL: None}
        self.access = {UP: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       DOWN: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       LEFT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       RIGHT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT]}

    def denyAccess(self, direction, entity):
        if entity.name in self.access[direction]:
            self.access[direction].remove(entity.name)

    def allowAccess(self, direction, entity):
        if entity.name not in self.access[direction]:
            self.access[direction].append(entity.name)

    def render(self, screen):
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None:
                line_start = self.position.asTuple()
                line_end = self.neighbors[n].position.asTuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                pygame.draw.circle(screen, RED, self.position.asInt(), 12)


class NodeGroup(object):
    def __init__(self, maze_grid):
        # self.level = level
        self.maze_grid = maze_grid
        self.nodesLUT = {}
        # self.nodeSymbols = ['+', 'P', 'n']
        # self.pathSymbols = ['.', '-', '|', 'p']
        # # data = self.readMazeFile(level)
        # self.createNodeTable(data)
        # self.connectHorizontally(data)
        # self.connectVertically(data)
        # self.homekey = None
        self.createNodesFromGrid()
        self.connectNodesFromGrid()

# NEW
    def createNodesFromGrid(self):
        for y, row in enumerate(self.maze_grid):
            for x, cell in enumerate(row):
                if cell == 15:
                    continue
                key = self.constructKey(x, y)
                self.nodesLUT[key] = Node(*key)

    def connectNodesFromGrid(self):
        NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
        for y, row in enumerate(self.maze_grid):
            for x, cell in enumerate(row):
                if cell == 15:
                    continue
                key = self.constructKey(x, y)
                if not (cell & EAST) and x + 1 < len(row):
                    otherkey = self.constructKey(x + 1, y)
                    if otherkey in self.nodesLUT:
                        self.nodesLUT[key].neighbors[RIGHT] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[LEFT] = self.nodesLUT[key]

                if not (cell & SOUTH) and y + 1 < len(self.maze_grid):
                    otherkey = self.constructKey(x, y + 1)
                    if otherkey in self.nodesLUT:
                        self.nodesLUT[key].neighbors[DOWN] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[UP] = self.nodesLUT[key]

    def pac_start(self):
        start_row = len(self.maze_grid) // 2
        start_col = len(self.maze_grid[0]) // 2
        right = start_col
        left = start_col

        x, y = self.constructKey(start_col, start_row)
        x_t, y_t = x, y
        while (x, y) not in self.nodesLUT.keys() and right < NCOLS:
            right += 1
            x, y = self.constructKey(right, start_row)

        while (x_t, y_t) not in self.nodesLUT.keys() and left > 0:
            left -= 1
            x_t, y_t = self.constructKey(left, start_row)   # corrigido

        if start_col == right:
            return self.nodesLUT[(x, y)]
        else:
            dif_r = right - start_col
            dif_l = start_col - left

            if dif_l > dif_r:
                # também estava trocado — devolvia o nó errado
                return self.nodesLUT[(x_t, y_t)]
            else:
                return self.nodesLUT[(x, y)]


# OLD


    def readMazeFile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')

    def createNodeTable(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    x, y = self.constructKey(col+xoffset, row+yoffset)
                    self.nodesLUT[(x, y)] = Node(x, y)

    # def constructKey(self, x, y):
    # 	return MAZE_OFFSET_X +  x * TILEWIDTH, MAZE_OFFSET_Y + y * TILEHEIGHT

    def constructKey(self, x, y):
        return (MAZE_OFFSET_X + x * TILEWIDTH + TILEWIDTH // 2,
                MAZE_OFFSET_Y + y * TILEHEIGHT + TILEHEIGHT // 2)

    def connectHorizontally(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            key = None
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.constructKey(col+xoffset, row+yoffset)
                        self.nodesLUT[key].neighbors[RIGHT] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[LEFT] = self.nodesLUT[key]
                        key = otherkey
                elif data[row][col] not in self.pathSymbols:
                    key = None

    def connectVertically(self, data, xoffset=0, yoffset=0):
        dataT = data.transpose()
        for col in list(range(dataT.shape[0])):
            key = None
            for row in list(range(dataT.shape[1])):
                if dataT[col][row] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.constructKey(col+xoffset, row+yoffset)
                        self.nodesLUT[key].neighbors[DOWN] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[UP] = self.nodesLUT[key]
                        key = otherkey
                elif dataT[col][row] not in self.pathSymbols:
                    key = None

    def getNodeFromPixels(self, xpixel, ypixel):
        if (xpixel, ypixel) in self.nodesLUT.keys():
            return self.nodesLUT[(xpixel, ypixel)]
        return None

    def getNodeFromTiles(self, col, row):
        x, y = self.constructKey(col, row)
        if (x, y) in self.nodesLUT.keys():
            return self.nodesLUT[(x, y)]
        return None

    def getStartTempNode(self):
        nodes = list(self.nodesLUT.values())
        return nodes[0]

    def setPortalPair(self, pair1, pair2):
        key1 = self.constructKey(*pair1)
        key2 = self.constructKey(*pair2)
        if key1 in self.nodesLUT.keys() and key2 in self.nodesLUT.keys():
            self.nodesLUT[key1].neighbors[PORTAL] = self.nodesLUT[key2]
            self.nodesLUT[key2].neighbors[PORTAL] = self.nodesLUT[key1]

    def createHomeNodes(self, xoffset, yoffset):
        homedata = np.array([['X', 'X', '+', 'X', 'X'],
                             ['X', 'X', '.', 'X', 'X'],
                             ['+', 'X', '.', 'X', '+'],
                             ['+', '.', '+', '.', '+'],
                             ['+', 'X', 'X', 'X', '+']])

        self.createNodeTable(homedata, xoffset, yoffset)
        self.connectHorizontally(homedata, xoffset, yoffset)
        self.connectVertically(homedata, xoffset, yoffset)
        self.homekey = self.constructKey(xoffset+2, yoffset)
        return self.homekey

    def connectHomeNodes(self, homekey, otherkey, direction):
        key = self.constructKey(*otherkey)
        self.nodesLUT[homekey].neighbors[direction] = self.nodesLUT[key]
        self.nodesLUT[key].neighbors[direction*-1] = self.nodesLUT[homekey]

    def denyAccess(self, col, row, direction, entity):
        node = self.getNodeFromTiles(col, row)
        if node is not None:
            node.denyAccess(direction, entity)

    def allowAccess(self, col, row, direction, entity):
        node = self.getNodeFromTiles(col, row)
        if node is not None:
            node.allowAccess(direction, entity)

    def denyAccessList(self, col, row, direction, entities):
        for entity in entities:
            self.denyAccess(col, row, direction, entity)

    def allowAccessList(self, col, row, direction, entities):
        for entity in entities:
            self.allowAccess(col, row, direction, entity)

    def denyHomeAccess(self, entity):
        self.nodesLUT[self.homekey].denyAccess(DOWN, entity)

    def allowHomeAccess(self, entity):
        self.nodesLUT[self.homekey].allowAccess(DOWN, entity)

    def denyHomeAccessList(self, entities):
        for entity in entities:
            self.denyHomeAccess(entity)

    def allowHomeAccessList(self, entities):
        for entity in entities:
            self.allowHomeAccess(entity)

    def render(self, screen):
        for node in self.nodesLUT.values():
            node.render(screen)
