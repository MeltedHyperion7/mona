from interrupt_solver import InterruptSolver
import matplotlib.pyplot as plt

if __name__ == '__main__':
    num_each = 100

    for dimension in [5, 7]:
        height = dimension
        width = dimension

        for density in [20, 60, 80]:
            for i in range(num_each):
                solver = InterruptSolver()
                solver.maze.load(f'mazes/{dimension}x{dimension}/{density}/maz{i}.pkl')