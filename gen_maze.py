from constants import *
from maze import Maze

if __name__ == '__main__':
    height = 5
    width = 5
    density = 20

    maze = Maze()
    maze.make_random_maze(height, width, density)
    maze.save('maz1.pkl')