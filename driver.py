from simple_solver import SimpleSolver
from maze import Maze
from constants import *
from mona import *
from control import monas
import time
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
            return
        if direction==DIR_UP:
            if self.orientation==DIR_LEFT:
                self.mona.move_right()
                return
            if self.orientation==DIR_RIGHT:
                self.mona.move_left()
                return
            self.mona.move_backward()
            return
        if direction==DIR_DOWN:
            if self.orientation==DIR_RIGHT:
                self.mona.move_right()
                return
            if self.orientation==DIR_LEFT:
                self.mona.move_left()
                return
            self.mona.move_backward()
            return
        if direction==DIR_LEFT:
            if self.orientation==DIR_UP:
                self.mona.move_left()
                return
            if self.orientation==DIR_DOWN:
                self.mona.move_right()
                return
            self.mona.move_backward()
            return
        if direction==DIR_RIGHT:
            if self.orientation==DIR_DOWN:
                self.mona.move_right()
                return
            if self.orientation==DIR_UP:
                self.mona.move_left()
                return
            self.mona.move_backward()
            return
        
        

maze=Maze()
solver=SimpleSolver(maze)
mona1=MONA(1,DIR_RIGHT,monas[0])
mona2=MONA(1,DIR_LEFT,monas[1])

def execute_Mona(id,mona:MONA):
    while not mona.mona.busy:
        #If on unexplored cell
        row, col = solver.maze.get_coords(id)
        #explore cell && update walls
        if mona.mona.wall_left:
            solver.update_wall(mona.conver_direction(DIR_LEFT))
        if mona.mona.wall_right:
            solver.update_wall(mona.conver_direction(DIR_RIGHT))
        if mona.mona.wall_front:
            solver.update_wall(mona.conver_direction(DIR_UP))

        #Calculate new distances
        solver.update_distance_matrix()
        #Get next cell to move
        cmd=solver.solve(mona.id)
        #Turn to face the cell
        mona.face_towards(cmd)
        #Move in the cell       
        mona.mona.move_forward()
        #Rest
        time.sleep(0.1)

while not solver.maze.is_explored():
    time.sleep(0.1)

    execute_Mona(1,mona1)
    execute_Mona(2,mona2)

