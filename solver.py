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
        self.height = maze.height
        self.width = maze.width
        self.distance_matrix = [[(0 if n1 == n2 else float('inf')) for n2 in range(self.height*self.width)] for n1 in range(self.height*self.width)]
        self.visited_ids = []
        self.mona1_target = None
        self.mona2_target = None
        self.mona1_path = []
        self.mona2_path = []
        self.mona1_last_action = None
        self.mona2_last_action = None

    def get_matrix_index(self, row, col):
        return row * self.width + col
    
    def get_coords(self, index):
        return divmod(index, self.width)

    def index_to_expanded_coords(self, index):
        row, col = self.get_coords(index)

        return 2*row + 1, 2*col + 1
    
    def expanded_to_grid_coords(self, expanded_coords):
        row, col = expanded_coords

        return row // 2, col // 2

    def expanded_to_index(self, expanded_coords):
        row, col = self.expanded_to_grid_coords(expanded_coords)

        return self.get_matrix_index(row, col)
    
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

    #@param min_time -minimum window time
    #@param max_dist -the minimum distance to the destination, which we should not exceed because we would already be on a suboptimal path
    def get_shortest_path(self, source_id, destination_id, visited, time, min_time, mona):
        # if time>min_dist:
        #     return 10000,[]
        
        current_path = []
        other_mona = MONA2 if mona == MONA1 else MONA1
        other_mona_path = self.mona2_path if mona == MONA1 else self.mona1_path
        available_tiles = [self.expanded_to_index(tile) for tile in self.maze.available_tiles_from_tile(self.index_to_expanded_coords(source_id))]
        if destination_id in available_tiles:
            return self.distance_matrix[source_id][destination_id], [self.get_coords(destination_id)]
        else:
            minimum = 10000
            for neighbour in available_tiles:
                if neighbour not in visited:
                    visited.append(neighbour)
                    neighbour_coords = self.get_coords(neighbour)

                    if neighbour_coords not in other_mona_path or abs(len(other_mona_path) - other_mona_path.index(neighbour_coords) - time - 1) >= min_time:
                        x, path_ending = self.get_shortest_path(neighbour, destination_id, visited, time+1, min_time, mona)
                        if x < minimum:
                            minimum = x
                            current_path = [neighbour_coords]
                            current_path.extend(path_ending)

            return minimum, current_path
        
    def update_distance_matrix(self, mona):
        # print(f"updating MONA{mona}")
        # self.maze.print()
        row, col =  self.expanded_to_grid_coords(self.maze.get_coords(mona))
        mona_index = self.get_matrix_index(row, col)
        self.visited_ids.append(mona_index)
        available_tiles = [self.expanded_to_grid_coords(tile) for tile in self.maze.available_tiles(mona, allow_mona_clash=True)]
        # print(available_tiles)

        for available_tile in available_tiles:
            self.distance_matrix[mona_index][self.get_matrix_index(available_tile[0], available_tile[1])] = 1
            self.distance_matrix[self.get_matrix_index(available_tile[0], available_tile[1])][mona_index] = 1

        for available_tile in available_tiles:
            available_tile_index = self.get_matrix_index(available_tile[0], available_tile[1])

            for j in range(self.height*self.width):
                if self.distance_matrix[available_tile_index][j] > self.distance_matrix[mona_index][j] + 1:
                    self.distance_matrix[available_tile_index][j] = self.distance_matrix[mona_index][j] + 1
                    self.distance_matrix[j][available_tile_index] = self.distance_matrix[mona_index][j] + 1
                
    def move_next(self, mona, next):
        r, c = next
        monar, monac = self.maze.get_coords(mona)

        if monar > r and self.maze.can_move(mona, DIR_UP):
            self.maze.move_mona(mona, DIR_UP)
            return True
        elif monar < r and self.maze.can_move(mona, DIR_DOWN):
            self.maze.move_mona(mona, DIR_DOWN)
            return True
        elif monac > c and self.maze.can_move(mona, DIR_LEFT):
            self.maze.move_mona(mona, DIR_LEFT)
            return True
        elif monac < c and self.maze.can_move(mona, DIR_RIGHT):
            self.maze.move_mona(mona, DIR_RIGHT)
            return True

        # TODO what if they come head on towards each other
        return False

    def pretty_print_distances(self, distances):
        for i in range(self.height):
            for j in range(self.width):
                print('i' if distances[self.get_matrix_index(i,j)] == float('inf') else distances[self.get_matrix_index(i,j)], end=" ")
            print()

    def pretty_print_matrix(self):
        for i in range(self.height*self.width):
            for j in range(self.height*self.width):
                print('i' if self.distance_matrix[i][j] == float('inf') else self.distance_matrix[i][j], end=" ")
            print()

    def get_next_explore_target(self, mona): 
        min_dist_to_travel=float("inf")
        best_node = self.maze.get_coords(mona)# Best thing to do is to stay in place
        mona_index = self.get_mona_index(mona)
        other_mona_target = self.mona2_target if mona == MONA1 else self.mona1_target

        # print(f'MONA{mona}:')
        best_node = None
        for node_id in range(self.height*self.width):
            if node_id != mona_index and node_id not in self.visited_ids and node_id != other_mona_target:

                print(f'{self.get_coords(node_id)}: {self.distance_matrix[mona_index][node_id]}. best: {min_dist_to_travel}')
                dist = self.distance_matrix[mona_index][node_id]
                if dist < min_dist_to_travel:
                    min_dist_to_travel = dist
                    best_node = node_id

        self.pretty_print_distances(self.distance_matrix[self.get_mona_index(mona)])

        if best_node == None:
            return None
            
        _, path = self.get_shortest_path(mona_index, best_node, [], 0, MIN_TIME, mona)
        # print(f"best_node: {self.get_coords(best_node)}. path: {path}")

        # allows poping to get next item
        path.reverse()

        if mona == MONA1:
            self.mona1_target = best_node
            self.mona1_path = path
        if mona == MONA2:
            self.mona2_target = best_node
            self.mona2_path = path

        return best_node
    
    def has_path(self, mona):
        return len(self.mona1_path) > 0 if mona == MONA1 else len(self.mona2_path) > 0

    def solve(self):
        #Explore Current cell & shortest distances & paths to every unexplored cell
        # self.pretty_print_matrix()

        if self.get_mona_index(MONA1) not in self.visited_ids:
            self.update_distance_matrix(MONA1)
        if self.get_mona_index(MONA2) not in self.visited_ids:
            self.update_distance_matrix(MONA2)

        if self.has_path(MONA1):
            self.move_next(MONA1, self.mona1_path.pop())
        else:
            target = self.get_next_explore_target(MONA1)
            if target is not None and self.has_path(MONA1):
                self.move_next(MONA1, self.mona1_path.pop())
            else:
                print(f"No target for MONA1")
                
        if self.has_path(MONA2):
            self.move_next(MONA2, self.mona2_path.pop())
        else:
            target = self.get_next_explore_target(MONA2)
            if target is not None and self.has_path(MONA2):
                self.move_next(MONA2, self.mona2_path.pop())
            else:
                print(f"No target for MONA2")


        
        
        