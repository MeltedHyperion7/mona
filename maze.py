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

    def get_shortest_distance(source:Node,destination:Node,visited:[]):
        if destination in source.neighbours:
            return source.dist[source.neighbours.index(destination)]
        else:
            minimum=10000
            for neighbour in source.neighbours:
                if neighbour not in visited:
                    visited.append(neighbour)
                    x=get_shortest_distance(neighbour,destination,visited)
                    if x<minimum:
                        minimum=x
            return minimum

    def is_maze_correct(self):
        accessible = {}
        stack = [(1, 1)]

        while len(stack) > 0:
            tile = stack.pop()
            accessible[tile] = True

            for direction in self.available_directions_from_tile(tile, allow_mona_clash=True):
                if direction == DIR_UP and (tile[0]-2, tile[1]) not in accessible:
                    stack.append((tile[0]-2, tile[1]))
                elif direction == DIR_DOWN and (tile[0]+2, tile[1]) not in accessible:
                    stack.append((tile[0]+2, tile[1]))
                elif direction == DIR_LEFT and (tile[0], tile[1]-2) not in accessible:
                    stack.append((tile[0], tile[1]-2))
                elif direction == DIR_RIGHT and (tile[0], tile[1]+2) not in accessible:
                    stack.append((tile[0], tile[1]+2))

        return len(accessible) == self.height * self.width

    def make_maze(self, height, width):
        for i in range(2*height+1):
            if i == 0 or i == 2*height:
                self.maze.append([WALL_UNEXPLORED] * (2*width + 1))
            elif i % 2 == 0:
                self.maze.append([WALL_UNEXPLORED if j == 0 or j == 2*width else UNKNOWN for j in range(2*width + 1)])
            else:
                self.maze.append([(WALL_UNEXPLORED if j == 0 or j == 2*width else UNKNOWN if j % 2 == 0 else PATH_UNEXPLORED) for j in range(2*width + 1)])

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

                        # make sure maze is correct
                        if not self.is_maze_correct():
                            self.maze[i][j] = UNKNOWN
            else:
                # vertical walls and paths
                for j in range(2, 2*width+1, 2):
                    if random.randint(0, 100) <= wall_density:
                        self.maze[i][j] = WALL_UNEXPLORED

                        # make sure maze is correct
                        if not self.is_maze_correct():
                            self.maze[i][j] = UNKNOWN

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

    def init_graph(self):
        step_weight=self.height
        for node_line,i in enumerate(self.nodes):
            for node, j in enumerate(node_line):

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
                    if self.maze[row][col] == PATH_EXPLORED:
                        pygame.draw.rect(screen, PATH_EXPLORED_COLOR, Rect(x, y, CELL_SIZE, CELL_SIZE))
                    if self.maze[row][col] == PATH_UNEXPLORED:
                        pygame.draw.rect(screen, PATH_UNEXPLORED_COLOR, Rect(x, y, CELL_SIZE, CELL_SIZE))
                    if self.maze[row][col] == WALL_UNEXPLORED:
                        pygame.draw.rect(screen, WALL_COLOR, Rect(x, y, WALL_SIZE, CELL_SIZE))
        
    def can_move(self, mona, direction, allow_mona_clash=False):
        mona_coords = self.mona1 if mona == MONA1 else self.mona2
        return self.can_move_from_tile(mona_coords, direction, mona, allow_mona_clash=allow_mona_clash)

    def can_move_from_tile(self, coords, direction, mona=None, allow_mona_clash=False): 
        if direction == DIR_UP:
            if coords[0] - 2 > 0:
                # if self.maze[coords[0] - 1] == UNKNOWN:
                #     return False, f"Moving UP through UNKNOWN. Mona: {mona}. Coordinates: {coords}"
                if self.isWall(coords[0] - 1,coords[1]):
                    return False, f"Moving UP through WALL. Mona: {mona}. Coordinates: {coords}"
                elif not allow_mona_clash and self.maze[coords[0] - 2][coords[1]] in [MONA1, MONA2]:
                    return False, f"Moving UP crashed into other mona. Mona: {mona}. Coordinates: {coords}"
                
                return True, None
                
            else:
                return False, f"Moving UP out of bounds. Mona: {mona}. Coordinates: {coords}"
                
        if direction == DIR_DOWN:
            if coords[0] + 2 < 2 * self.height + 1:
                # if self.maze[coords[0] + 1] == UNKNOWN:
                #     return False, f"Moving DOWN through UNKNOWN. Mona: {mona}. Coordinates: {coords}"
                if self.isWall(coords[0]+1,coords[1]):
                    return False, f"Moving DOWN through WALL. Mona: {mona}. Coordinates: {coords}"
                elif not allow_mona_clash and self.maze[coords[0] + 2][coords[1]] in [MONA1, MONA2]:
                    return False, f"Moving DOWN crashed into other mona. Mona: {mona}. Coordinates: {coords}"
                
                return True, None
                
            else:
                return False, f"Moving DOWN out of bounds. Mona: {mona}. Coordinates: {coords}"
        if direction == DIR_LEFT:
            if coords[1] - 2 > 0:
                # if self.maze[coords[1] - 1] == UNKNOWN:
                #     return False, f"Moving LEFT through UNKNOWN. Mona: {mona}. Coordinates: {coords}"
                if self.isWall(coords[0],coords[1]-1):
                    return False, f"Moving LEFT through WALL. Mona: {mona}. Coordinates: {coords}"
                elif not allow_mona_clash and self.maze[coords[0]][coords[1] - 2] in [MONA1, MONA2]:
                    return False, f"Moving LEFT crashed into other mona. Mona: {mona}. Coordinates: {coords}"
                
                return True, None
                
            else:
                return False, f"Moving LEFT out of bounds. Mona: {mona}. Coordinates: {coords}"
        if direction == DIR_RIGHT:
            if coords[1] + 2 < 2*self.width + 1:
                # if self.maze[coords[1] + 1] == UNKNOWN:
                #     return False, f"Moving RIGHT through UNKNOWN. Mona: {mona}. Coordinates: {coords}"
                if self.isWall(coords[0],coords[1]+1):
                    return False, f"Moving RIGHT through WALL. Mona: {mona}. Coordinates: {coords}"
                elif not allow_mona_clash and self.maze[coords[0]][coords[1] + 2] in [MONA1, MONA2]:
                    return False, f"Moving RIGHT crashed into other mona. Mona: {mona}. Coordinates: {coords}"
                
                return True, None
                
            else:
                return False, (f"Moving RIGHT out of bounds. Mona: {mona}. Coordinates: {coords}")
                
    def move_mona(self, mona, direction):
        mona_coords = self.mona1 if mona == MONA1 else self.mona2
        other_mona = (mona + 1) % 2

        move_possible, reason = self.can_move(mona, direction)

        if not move_possible:
            raise Exception(reason)
        
        if direction == DIR_UP:
            self.maze[mona_coords[0]][mona_coords[1]] = PATH_EXPLORED
            mona_coords[0] -= 2
            self.maze[mona_coords[0]][mona_coords[1]] = mona
        elif direction == DIR_DOWN:
            self.maze[mona_coords[0]][mona_coords[1]] = PATH_EXPLORED
            mona_coords[0] += 2
            self.maze[mona_coords[0]][mona_coords[1]] = mona
        elif direction == DIR_LEFT:
            self.maze[mona_coords[0]][mona_coords[1]] = PATH_EXPLORED
            mona_coords[1] -= 2
            self.maze[mona_coords[0]][mona_coords[1]] = mona
        elif direction == DIR_RIGHT:
            self.maze[mona_coords[0]][mona_coords[1]] = PATH_EXPLORED
            mona_coords[1] += 2
            self.maze[mona_coords[0]][mona_coords[1]] = mona
                
    def available_directions(self, mona, allow_mona_clash=False):
        d = [direction for direction in [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT] if self.can_move(mona, direction, allow_mona_clash=allow_mona_clash)[0]]
        return d

    def available_directions_from_tile(self, coords, allow_mona_clash=False):
        d = [direction for direction in [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT] if self.can_move_from_tile(coords, direction, allow_mona_clash=allow_mona_clash)[0]]
        return d

    def is_explored(self):
        for row in range(1, 2*self.height+1, 2):
            for col in range(1, 2*self.width+1, 2):
                if self.maze[row][col] == PATH_UNEXPLORED:
                    return False
                
        return True
