from simple_solver import SimpleSolver
from interrupt_solver import InterruptSolver
from maze import Maze
from constants import *
from mona import *
import time
import pygame
class MONA:
    def __init__(self,id,orientation,mona:Mona) -> None:
        self.id=id
        self.orientation=orientation
        self.mona=mona
    

    def conver_direction(self,direction):
        if direction==DIR_LEFT:
            if self.orientation==DIR_LEFT:
                return DIR_DOWN
            if self.orientation==DIR_RIGHT:
                return DIR_UP
            if self.orientation==DIR_UP:
                return DIR_LEFT
            if self.orientation==DIR_DOWN:
                return DIR_RIGHT
            
        if direction==DIR_RIGHT:
            if self.orientation==DIR_LEFT:
                return DIR_UP
            if self.orientation==DIR_RIGHT:
                return DIR_DOWN
            if self.orientation==DIR_UP:
                return DIR_RIGHT
            if self.orientation==DIR_DOWN:
                return DIR_LEFT
            
        if direction==DIR_UP:
            if self.orientation==DIR_LEFT:
                return DIR_LEFT
            if self.orientation==DIR_RIGHT:
                return DIR_RIGHT
            if self.orientation==DIR_UP:
                return DIR_UP
            if self.orientation==DIR_DOWN:
                return DIR_DOWN
            
        if direction==DIR_DOWN:
            if self.orientation==DIR_LEFT:
                return DIR_RIGHT
            if self.orientation==DIR_RIGHT:
                return DIR_LEFT
            if self.orientation==DIR_UP:
                return DIR_DOWN
            if self.orientation==DIR_DOWN:
                return DIR_UP

    def face_towards(self,direction):
        if self.orientation==direction:
            self.mona.move_forward()
        elif direction==DIR_UP:
            if self.orientation==DIR_LEFT:
                self.mona.move_right()
            elif self.orientation==DIR_RIGHT:
                self.mona.move_left()
            else:
                self.mona.move_backward()
        elif direction==DIR_DOWN:
            if self.orientation==DIR_RIGHT:
                self.mona.move_right()
            elif self.orientation==DIR_LEFT:
                self.mona.move_left()
            else:
                self.mona.move_backward()
        elif direction==DIR_LEFT:
            if self.orientation==DIR_UP:
                self.mona.move_left()
            elif self.orientation==DIR_DOWN:
                self.mona.move_right()
            else:
                self.mona.move_backward()
        elif direction==DIR_RIGHT:
            if self.orientation==DIR_DOWN:
                self.mona.move_left()
            elif self.orientation==DIR_UP:
                self.mona.move_right()
            else:
                self.mona.move_backward()
        
        print("here")
        self.orientation = direction

    def rotate_find_walls(self):
        counts = [] * 4
        for i in range(4):
            while self.mona.busy:
                time.sleep(0.2)


            self.mona.turn_right_90()

        
def init():
   

    uno = MonaUno()
    monas = [
        Mona(uno, 0),
        Mona(uno, 1),
    ]
    monas[0].spawn_poll_thread()
    monas[1].spawn_poll_thread()
    monas[0].wait_for_online()
    monas[1].wait_for_online()

    return monas

monas=init()
maze=Maze()
maze.make_maze(5, 5)
solver=InterruptSolver(maze)
mona1=MONA(0,DIR_RIGHT,monas[0])
mona2=MONA(1,DIR_LEFT,monas[1])

DELAY = 0.2

def execute_Mona(id, mona:MONA):
    while not mona.mona.busy:
        time.sleep(0.2)

        # mona.face_towards(DIR_DOWN)

        # time.sleep(0.5)

        # mona.face_towards(DIR_RIGHT)
        # continue

        #If on unexplored cell
        #explore cell && update walls
        directions = []
        # mona.mona.take_ir_capture()
        mona_coords = solver.maze.get_coords(mona.id+1)
        print(mona.mona.state.ir)
        # while True:

        print(mona.mona.ir_capture)
        print(f'MONA{mona.id+1}. Coordinates: {solver.expanded_to_grid_coords(mona_coords)}. orientation: {mona.orientation}')
        if mona.mona.wall_left:
            directions.append(mona.conver_direction(DIR_LEFT))
            # solver.update_walls(mona.id+1,mona.conver_direction(DIR_LEFT))
        if mona.mona.wall_right:
            directions.append(mona.conver_direction(DIR_RIGHT))
            # solver.update_walls(mona.id+1,mona.conver_direction(DIR_RIGHT))
        if mona.mona.wall_front:
            directions.append(mona.conver_direction(DIR_UP))
            # solver.update_walls(mona.id+1,mona.conver_direction(DIR_UP))
        solver.update_walls(mona.id+1, directions)
        print(f'Mona{mona.id+1} sees {directions}')
        #Get next cell to move
        cmd = solver.solve(mona.id+1)
        print(f'Mona {mona.id+1} command: {cmd}')
        if cmd is not None:
            mona.face_towards(cmd)
        else:
            solver.solve(mona.id+1)
        #Turn to face the cell
        #Move in the cell       
        # mona.mona.move_forward()
        #Rest
        time.sleep(DELAY)

while not solver.maze.is_explored():
    time.sleep(DELAY)

    execute_Mona(1,mona1)
    execute_Mona(2,mona2)

