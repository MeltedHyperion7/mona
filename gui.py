from constants import *
from maze import Maze

import pygame
import random

if __name__ == '__main__':
    height = 5
    width = 5

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Maze Generator")

    maze = Maze()
    maze.make_random_maze(height, width, 20)
    maze.make_maze_graph()
    maze.print()

    running = True
    explored = False
    time_since_move = 0
    total_moves=0

    while running:
        time_delta = clock.tick(60)
        time_since_move += time_delta

        if not explored and time_since_move > 2000:
            maze.move_mona(MONA1, random.choice(maze.available_directions(MONA1)))
            maze.move_mona(MONA2, random.choice(maze.available_directions(MONA2)))
            print(maze.nodes[3][3].neighbours)
            time_since_move = 0
            total_moves+=2

            if maze.is_explored():
                explored = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        maze.draw(screen)
        pygame.display.flip()

    pygame.quit()