from constants import *

import pickle
import pygame
from pygame import Rect
import random

class Node:
    def __init__(self,id) -> None:
        self.neighbours=[]
        self.dist=[]
        self.id=id

    def add_neighbour(self,node,dist):
        self.neighbours.append(node)
        self.dist.append(dist)
        node.neighbours.append(self)
        node.dist.append(dist)
class Maze:
    def isWall(self,row,col):
        tile= self.maze[row][col]
        if tile==WALL_UNEXPLORED or tile==WALL_EXPLORED_1 or tile==WALL_EXPLORED_2:
            return True
        return False
        
    

    def __init__(self) -> None:
        self.maze = []
        self.height = 0
        self.width = 0
        self.mona1 = [0, 0]
        self.mona2 = [0, 0]
        self.nodes=[]

    def make_maze(self, height, width):
        for i in range(2*height+1):
            if i == 0 or i == 2*height:
                self.maze.append([WALL_UNEXPLORED] * (2*width + 1))
            elif i % 2 == 0:
                self.maze.append([WALL_UNEXPLORED if j == 0 or j == 2*width else UNKNOWN for j in range(2*width + 1)])
            else:
                self.maze.append([(WALL_UNEXPLORED if j == 0 or j == 2*width else UNKNOWN if j % 2 == 0 else PATH) for j in range(2*width + 1)])

        self.maze[1][1] = MONA1
        self.maze[-2][-2] = MONA2

        self.height = height
        self.width = width

        self.mona1 = [1, 1]
        self.mona2 = [2*height-1, 2*width-1]

    def make_random_maze(self, height, width, wall_density):
        self.make_maze(height, width)

        for i in range(1, 2*height):
            if i % 2 == 0:
                # horizontal walls
                for j in range(1, 2*width+1, 2):
                    if random.randint(0, 100) <= wall_density:
                        self.maze[i][j] = WALL_UNEXPLORED
            else:
                # vertical walls and paths
                for j in range(2, 2*width+1, 2):
                    if random.randint(0, 100) <= wall_density:
                        self.maze[i][j] = WALL_UNEXPLORED

    def make_maze_graph(self):
        icounter=0
        for i in range(1,2*self.height,2):

            self.nodes.append([])
            jcounter=0
            for j in range(1,2*self.width,2):
                node=Node(icounter*self.height+jcounter)
                #Add left neighbour

                if jcounter!=0:
                    if self.maze[i][j-1]!=WALL_UNEXPLORED:
                        node.add_neighbour(self.nodes[icounter][jcounter-1],1)
                    else:
                        node.add_neighbour(self.nodes[icounter][jcounter-1],-1)
                #Add top neighbour
                if icounter!=0:
                    if self.maze[i-1][j]!=WALL_UNEXPLORED:
                        node.add_neighbour(self.nodes[icounter-1][jcounter],1)
                    else:
                        node.add_neighbour(self.nodes[icounter-1][jcounter],-1)
                self.nodes[icounter].append(node)
                jcounter+=1
            icounter+=1

    def print(self):
        for row in self.maze:
            for c in row:
                print(c, end='')
            print()

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.maze, f)

    def load(self, filename):
        with open(filename, 'rb') as f:
            self.maze = pickle.load(f)

    def draw(self, screen):
        screen.fill(WHITE)
        for row in range(2*self.height+1):
            y = (row // 2) * (CELL_SIZE + WALL_SIZE) + (WALL_SIZE if row % 2 == 1 else 0) 
            
            if row % 2 == 0:
                # all horizontal walls
                for col in range(1, 2*self.width+1, 2):
                    x = (col + 1) // 2 * WALL_SIZE + (col // 2) * CELL_SIZE 
                    if self.maze[row][col] == UNKNOWN:
                        pygame.draw.rect(screen, BLACK, Rect(x, y, CELL_SIZE, WALL_SIZE))
                    if self.maze[row][col] == WALL_UNEXPLORED:
                        pygame.draw.rect(screen, WALL_COLOR, Rect(x, y, CELL_SIZE, WALL_SIZE))
            else:
                # vertical walls and cells
                for col in range(0, 2*self.width+1):
                    x = (col // 2) * (CELL_SIZE + WALL_SIZE) + (WALL_SIZE if col % 2 == 1 else 0) 
                    if self.maze[row][col] == MONA1:
                        pygame.draw.rect(screen, MONA1_COLOR, Rect(x, y, CELL_SIZE, CELL_SIZE))
                    if self.maze[row][col] == MONA2:
                        pygame.draw.rect(screen, MONA2_COLOR, Rect(x, y, CELL_SIZE, CELL_SIZE))
                    if self.maze[row][col] == UNKNOWN:
                        pygame.draw.rect(screen, BLACK, Rect(x, y, WALL_SIZE, CELL_SIZE))
                    if self.maze[row][col] == PATH:
                        pygame.draw.rect(screen, PATH_COLOR, Rect(x, y, CELL_SIZE, CELL_SIZE))
                    if self.maze[row][col] == WALL_UNEXPLORED:
                        pygame.draw.rect(screen, WALL_COLOR, Rect(x, y, WALL_SIZE, CELL_SIZE))
        
    def can_move(self, mona, direction):
        mona_coords = self.mona1 if mona == MONA1 else self.mona2
        wall_explored = WALL_EXPLORED_1 if mona == MONA1 else WALL_EXPLORED_2
        
        other_mona = (mona + 1) % 2

        if direction == DIR_UP:
            if mona_coords[0] - 2 > 0:
                # if self.maze[mona_coords[0] - 1] == UNKNOWN:
                #     return False, f"Moving UP through UNKNOWN. Mona: {mona}. Coordinates: {mona_coords}"
                if self.isWall(mona_coords[0] - 1,mona_coords[1]):
                    return False, f"Moving UP through WALL. Mona: {mona}. Coordinates: {mona_coords}"
                elif self.maze[mona_coords[0] - 2][mona_coords[1]] == other_mona:
                    return False, f"Moving UP crashed into other mona. Mona: {mona}. Coordinates: {mona_coords}"
                
                return True, None
                
            else:
                return False, f"Moving UP out of bounds. Mona: {mona}. Coordinates: {mona_coords}"
                
        if direction == DIR_DOWN:
            if mona_coords[0] + 2 < 2 * self.height + 1:
                # if self.maze[mona_coords[0] + 1] == UNKNOWN:
                #     return False, f"Moving DOWN through UNKNOWN. Mona: {mona}. Coordinates: {mona_coords}"
                if self.isWall(mona_coords[0]+1,mona_coords[1]):
                    return False, f"Moving DOWN through WALL. Mona: {mona}. Coordinates: {mona_coords}"
                elif self.maze[mona_coords[0] + 2][mona_coords[1]] == other_mona:
                    return False, f"Moving DOWN crashed into other mona. Mona: {mona}. Coordinates: {mona_coords}"
                
                return True, None
                
            else:
                return False, f"Moving DOWN out of bounds. Mona: {mona}. Coordinates: {mona_coords}"
        if direction == DIR_LEFT:
            if mona_coords[1] - 2 > 0:
                # if self.maze[mona_coords[1] - 1] == UNKNOWN:
                #     return False, f"Moving LEFT through UNKNOWN. Mona: {mona}. Coordinates: {mona_coords}"
                if self.isWall(mona_coords[0],mona_coords[1]-1):
                    return False, f"Moving LEFT through WALL. Mona: {mona}. Coordinates: {mona_coords}"
                elif self.maze[mona_coords[0]][mona_coords[1] - 2] == other_mona:
                    return False, f"Moving LEFT crashed into other mona. Mona: {mona}. Coordinates: {mona_coords}"
                
                return True, None
                
            else:
                return False, f"Moving LEFT out of bounds. Mona: {mona}. Coordinates: {mona_coords}"
        if direction == DIR_RIGHT:
            if mona_coords[1] + 2 < 2*self.width + 1:
                # if self.maze[mona_coords[1] + 1] == UNKNOWN:
                #     return False, f"Moving RIGHT through UNKNOWN. Mona: {mona}. Coordinates: {mona_coords}"
                if self.isWall(mona_coords[0],mona_coords[1]+1):
                    return False, f"Moving RIGHT through WALL. Mona: {mona}. Coordinates: {mona_coords}"
                elif self.maze[mona_coords[0]][mona_coords[1] + 2] == other_mona:
                    return False, f"Moving RIGHT crashed into other mona. Mona: {mona}. Coordinates: {mona_coords}"
                
                return True, None
                
            else:
                return False, (f"Moving RIGHT out of bounds. Mona: {mona}. Coordinates: {mona_coords}")
                
    def move_mona(self, mona, direction):
        mona_coords = self.mona1 if mona == MONA1 else self.mona2
        other_mona = (mona + 1) % 2

        move_possible, reason = self.can_move(mona, direction)

        if not move_possible:
            raise Exception(reason)
        
        if direction == DIR_UP:
            self.maze[mona_coords[0]][mona_coords[1]] = PATH
            mona_coords[0] -= 2
            self.maze[mona_coords[0]][mona_coords[1]] = mona
        elif direction == DIR_DOWN:
            self.maze[mona_coords[0]][mona_coords[1]] = PATH
            mona_coords[0] += 2
            self.maze[mona_coords[0]][mona_coords[1]] = mona
        elif direction == DIR_LEFT:
            self.maze[mona_coords[0]][mona_coords[1]] = PATH
            mona_coords[1] -= 2
            self.maze[mona_coords[0]][mona_coords[1]] = mona
        elif direction == DIR_RIGHT:
            self.maze[mona_coords[0]][mona_coords[1]] = PATH
            mona_coords[1] += 2
            self.maze[mona_coords[0]][mona_coords[1]] = mona
                
    def available_directions(self, mona):
        d = [direction for direction in [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT] if self.can_move(mona, direction)[0]]
        print(f"Mona: {mona}. Direcitons: {d}")
        return d
