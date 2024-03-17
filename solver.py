from constants import *

import random
from maze import Maze

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

class Solver:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.nodes=[]
        self.visited_ids=[]
        self.height = maze.height
        self.width = maze.width
        self.distance_matrix = [[((0, None) if n1 == n2 else (float('inf'), None)) for n2 in range(self.height*self.width)] for n1 in range(self.height*self.width)]
        self.visited_ids=[]
        self.init_graph()
        self.mona1_target=None
        self.mona2_target=None

    def get_matrix_index(self, row, col):
        return row * self.width + col
    
    def get_coords(self, index):
        return divmod(index, self.width)
    
    def get_mona_index(self, mona):
        if mona == MONA1:
            return self.get_matrix_index(self.maze.mona1[0] // 2, self.maze.mona1[1] // 2)
        else:
            return self.get_matrix_index(self.maze.mona2[0] // 2, self.maze.mona2[1] // 2)

    def opposite_direction(self, direction):
        if direction == DIR_UP:
            return DIR_DOWN
        elif direction == DIR_DOWN:
            return DIR_UP
        elif direction == DIR_LEFT:
            return DIR_RIGHT
        else:
            return DIR_LEFT

    def get_shortest_distance(self, source:Node, destination:Node, visited: [Node]):
        if destination in source.neighbours:
            return source.dist[source.neighbours.index(destination)]
        else:
            minimum=10000
            for neighbour in source.neighbours:
                if neighbour not in visited:
                    visited.append(neighbour)
                    x = self.get_shortest_distance(neighbour,destination,visited)
                    if x<minimum:
                        minimum=x
            return minimum
        
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
                jcounter += 1
            icounter += 1

    def init_graph(self):
        # step_weight=self.height
        # for mona in monas:
        for node_line,i in enumerate(self.nodes):
            for node, j in enumerate(node_line):
                    for x in range(len(node.dist)):
                        node.dist[x]=float("inf")

    # def update_shortest_paths(self, mona, row, col):
    def update_shortest_paths(self, mona):
        available_directions = self.maze.available_directions(mona)
        print(f'MONA{mona}, available directions: {available_directions}')

        row, col = self.maze.get_coords(mona)
        mona_index = self.get_matrix_index(row, col)
        self.visited_ids.append(mona_index)
        available_cells = []
        for direction in available_directions:
            if direction == DIR_UP:
                available_cells.append((row-1, col))
            if direction == DIR_DOWN:
                available_cells.append((row+1, col))
            if direction == DIR_LEFT:
                available_cells.append((row, col-1))
            if direction == DIR_RIGHT:
                available_cells.append((row, col+1))

        for i, available_cell in enumerate(available_cells):
            self.distance_matrix[mona_index][self.get_matrix_index(available_cell[0], available_cell[1])] = (1, available_directions[i])
            self.distance_matrix[self.get_matrix_index(available_cell[0], available_cell[1])][mona_index] = (1, self.opposite_direction(available_directions[i]))

        for i, available_cell in enumerate(available_cells):
            available_cell_index = self.get_matrix_index(available_cell[0], available_cell[1])

            for j in range(self.height*self.width):
                if  self.distance_matrix[available_cell_index][j][0] > self.distance_matrix[mona_index][j][0] + 1:
                    self.distance_matrix[available_cell_index][j] = (self.distance_matrix[mona_index][j][0] + 1, self.opposite_direction(available_directions[i]))
                
        # for node_line in self.nodes:
        #     for node in node_line:
        #         if node.id not in self.visited_ids:
        #             self.distance_matrix[row][col] = self.get_shortest_distance(self.nodes[row][col])

    def move_to(self, mona, r, c):
        monar,monac=self.maze.get_coords(mona)
        if monar>r:
            self.maze.move_mona(mona, DIR_UP)
        elif monar<r:
            self.maze.move_mona(mona, DIR_DOWN)
        if monac>c:
            self.maze.move_mona(mona, DIR_LEFT)
        elif monac<c:
            self.maze.move_mona(mona, DIR_RIGHT)

    def pretty_print_distances(self, distances):
        for i in range(self.height):
            for j in range(self.width):
                print('i' if distances[self.get_matrix_index(i,j)][0] == float('inf') else distances[self.get_matrix_index(i,j)][0], end=" ")
            print()

    def get_next_explore_target(self, mona): 
        min_dist_to_travel=float("inf")
        best_node = self.maze.get_coords(mona)# Best thing to do is to stay in place
        mona_index = self.get_mona_index(mona)
        other_mona_target = self.mona2_target if mona == MONA1 else self.mona1_target

        print(f'We({mona}) should not target {other_mona_target}')
        for node_id in range(self.height**2):
            if node_id != mona_index and node_id not in self.visited_ids and node_id!=other_mona_target:
                dist = self.distance_matrix[self.get_mona_index(mona)][node_id][0]
                if dist < min_dist_to_travel:
                    best_node = node_id
        

        self.pretty_print_distances(self.distance_matrix[self.get_mona_index(mona)])
        if mona==MONA1:
            self.mona1_target=best_node
        if mona==MONA2:
            self.mona2_target=best_node
        return best_node
    
    def get_next_step_to(self, mona, target_index):
        mona_index = self.get_mona_index(mona)

        print(f'For mona {mona} we are targeting {self.get_coords(target_index)}')
        step = self.distance_matrix[mona_index][target_index][1]

        print(f'MONA{mona}, next direction: {step}')

        return step

    def solve(self):
        #Explore Current cell & shortest distances & paths to every unexplored cell
        if self.get_mona_index(MONA1) not in self.visited_ids:
            self.update_shortest_paths(MONA1)
        if self.get_mona_index(MONA2) not in self.visited_ids:
            self.update_shortest_paths(MONA2)

        #Move one more step towards the closes unexplored cell
        self.maze.move_mona(MONA1, self.get_next_step_to(MONA1, self.get_next_explore_target(MONA1)))
        self.maze.move_mona(MONA2, self.get_next_step_to(MONA2, self.get_next_explore_target(MONA2)))
        

        
        
        