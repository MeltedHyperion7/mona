import solver

class Away_Solver(solver.Solver):

    def get_next_explore_target(self, mona):
        min_dist_to_travel=float("inf")
        best_node = self.maze.get_coords(mona)# Best thing to do is to stay in place
        mona_index = self.get_mona_index(mona)
        other_mona_target = self.mona2_target if mona == MONA1 else self.mona1_target

        print(f'MONA{mona}:')
        best_node = None
        for node_id in range(self.height*self.width):
            if node_id != mona_index and node_id not in self.visited_ids and node_id != other_mona_target:

                print(f'{self.get_coords(node_id)}: {self.distance_matrix[mona_index][node_id]}. best: {min_dist_to_travel}')
                dist = self.distance_matrix[mona_index][node_id]
                if dist < min_dist_to_travel:
                    min_dist_to_travel = dist
                    best_node = node_id
                elif dist==min_dist_to_travel:
                    if self.distance_matrix[mona_index][best_node]<self.distance_matrix[mona_index][node_id]:
                        min_dist_to_travel = dist
                        best_node = node_id

        self.pretty_print_distances(self.distance_matrix[self.get_mona_index(mona)])

        if best_node == None:
            return None
            
        _, path = self.get_shortest_path(mona_index, best_node, [], 0, MIN_TIME, mona)
        print(f"best_node: {self.get_coords(best_node)}. path: {path}")

        # allows poping to get next item
        path.reverse()

        if mona == MONA1:
            self.mona1_target = best_node
            self.mona1_path = path
        if mona == MONA2:
            self.mona2_target = best_node
            self.mona2_path = path

        return best_node