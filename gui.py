from constants import *
from maze import Maze

import pygame
import random

from solver import Solver
from interrupt_solver import InterruptSolver

if __name__ == '__main__':
    dimension = 5

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Maze Generator")

    maze = Maze()
    maze.make_random_maze(dimension, dimension, 40)
    maze.print()

    running = True
    explored = False
    time_since_move = 0
    total_moves = 0
    solver = InterruptSolver(maze)

    while running:
        time_delta = clock.tick(60)
        time_since_move += time_delta

        if not explored and time_since_move > 2000:
            solver.maze.update_walls_virt(MONA1)
            solver.solve(MONA1)
            solver.maze.update_walls_virt(MONA2)
            solver.solve(MONA2)
            
            total_moves += 1
            print(f"STEP {total_moves}")
            time_since_move = 0

            if maze.is_explored():
                explored = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        maze.draw(screen)
        pygame.display.flip()

    pygame.quit()