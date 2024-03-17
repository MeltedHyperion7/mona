from simple_solver import SimpleSolver
from constants import *
from maze import Maze

class InterruptSolver(SimpleSolver):
    def get_next_explore_target(self, mona): 
        min_dist_to_travel=float("inf")
        mona_index = self.get_mona_index(mona)
        other_mona = (mona+1) % 2
        other_mona_target = self.mona2_target if mona == MONA1 else self.mona1_target
        other_mona_index = self.get_mona_index(other_mona)

        # print(f'MONA{mona}:')
        best_node = None
        path = []
        for node_id in range(self.height*self.width):
            if node_id != mona_index and node_id not in self.visited_ids:
                dist = self.distance_matrix[mona_index][node_id]
                if dist < min_dist_to_travel and (node_id != other_mona_target or dist < self.distance_matrix[other_mona_index][node_id]):
                    _, pos_path = self.get_shortest_path(mona_index, node_id)
                    if pos_path is not None:
                        min_dist_to_travel = dist
                        best_node = node_id
                        path = pos_path

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

        if best_node == other_mona_target:
            # interrupt other mona
            print(f'MONA{mona} interrupted MONA{other_mona}. Target: {best_node_coords}')
            self.get_next_explore_target(other_mona)


        return best_node_coords