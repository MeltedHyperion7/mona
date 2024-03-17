from solver import Solver
from constants import *
from maze import Maze

class SimpleSolver(Solver):
    def get_shortest_path(self, source_id, destination_id):
        current_path = []
        current_tile = source_id
        current_distance = self.distance_matrix[current_tile][destination_id]

        while current_distance > 0:
            available_tiles = [self.expanded_to_index(tile) for tile in self.maze.available_tiles_from_tile(self.index_to_expanded_coords(current_tile), allow_mona_clash=True)]

            found = False
            for available_tile in available_tiles:
                if self.distance_matrix[available_tile][destination_id] < current_distance:
                    current_path.append(self.get_coords(available_tile))
                    current_tile = available_tile
                    current_distance = self.distance_matrix[available_tile][destination_id]
                    found = True
                    break

            if not found:
                return 0, None

        return len(current_path), current_path

    def get_next_explore_target(self, mona): 
        min_dist_to_travel=float("inf")
        mona_index = self.get_mona_index(mona)
        other_mona_target = self.mona2_target if mona == MONA1 else self.mona1_target

        # print(f'MONA{mona}:')
        best_node = None
        for node_id in range(self.height*self.width):
            if node_id != mona_index and node_id not in self.visited_ids:
                dist = self.distance_matrix[mona_index][node_id]
                if dist < min_dist_to_travel:
                    min_dist_to_travel = dist
                    best_node = node_id

        # self.pretty_print_distances(self.distance_matrix[self.get_mona_index(mona)])

        if best_node == None:
            return None
            
        _, path = self.get_shortest_path(mona_index, best_node)
        best_node_coords = self.get_coords(best_node)
        # print(f"best_node: {best_node_coords}. path: {path}")

        # allows poping to get next item
        path.reverse()

        if mona == MONA1:
            self.mona1_target = best_node
            self.mona1_path = path
        if mona == MONA2:
            self.mona2_target = best_node
            self.mona2_path = path

        return best_node_coords
    
    def move_next(self, mona):
        mona_path = self.mona1_path if mona == MONA1 else self.mona2_path
        r, c = mona_path.pop()
        monar, monac = self.expanded_to_grid_coords(self.maze.get_coords(mona))

        if monar > r and self.maze.can_move(mona, DIR_UP)[0]:
            self.maze.move_mona(mona, DIR_UP)
            return DIR_UP
        elif monar < r and self.maze.can_move(mona, DIR_DOWN)[0]:
            self.maze.move_mona(mona, DIR_DOWN)
            return DIR_DOWN
        elif monac > c and self.maze.can_move(mona, DIR_LEFT)[0]:
            self.maze.move_mona(mona, DIR_LEFT)
            return DIR_LEFT
        elif monac < c and self.maze.can_move(mona, DIR_RIGHT)[0]:
            self.maze.move_mona(mona, DIR_RIGHT)
            return DIR_RIGHT
        else:
            mona_path.append((r, c))
            return None

    def update_walls(self, mona, walls):
        self.maze.update_walls(mona, walls)

    def solve(self, mona):
        # if self.get_mona_index(MONA1) not in self.visited_ids:
        # if self.get_mona_index(MONA2) not in self.visited_ids:
        # self.update_distance_matrix(MONA1)
        # self.update_distance_matrix(MONA2)
        # self.maze.print()
        self.update_distance_matrix(mona)

        mona_action = None

        if mona == MONA1:
            if self.has_path(MONA1):
                self.mona1_last_action = mona_action = self.move_next(MONA1)
            else:
                target = self.get_next_explore_target(MONA1)
                if self.has_path(MONA1):
                    self.mona1_last_action = mona_action = self.move_next(MONA1)
                # else:
                #     print(f"No target for MONA1")
        else:
            if self.has_path(MONA2):
                self.mona2_last_action = mona_action = self.move_next(MONA2)
            else:
                target = self.get_next_explore_target(MONA2)
                if self.has_path(MONA2):
                    self.mona2_last_action = mona_action = self.move_next(MONA2)
                # else:
                #     print(f"No target for MONA2")

        # flipped order to counter deadlocks
        if self.mona1_last_action == None and self.mona2_last_action == None:
            self.mona1_target = None
            self.mona1_path = []
            self.mona2_target = None
            self.mona2_path = []
            self.get_next_explore_target(MONA2)
            self.get_next_explore_target(MONA1)

        return mona_action