from constants import *
from maze import Maze

if __name__ == '__main__':
    num_each = 100

    for dimension in [5, 7]:
        height = dimension
        width = dimension

        for density in [20, 60, 80]:
            for i in range(num_each):
                maze = Maze()
                maze.make_random_maze(height, width, density)
                maze.save(f'mazes/{dimension}x{dimension}/{density}/maz{i}.pkl')