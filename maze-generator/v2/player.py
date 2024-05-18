import pygame
import random
from amazed.modules.maze import Maze, Vector2D
from amazed.modules.solver import AStar

class Player():
    '''
    Default class which can be inherited to develop strategies
    '''
    def __init__(self, name, body: pygame.Rect, maze: Maze, start=None, finish=None):
        if name not in ("PlayerA", "PlayerB"):
            raise ValueError(f"Player name incorrect <{name}>")
        
        self.name = name
        self.body = body
        self.maze = maze
        # self.pos.x = start.x
        # self.pos.y = start.y

        # Requested cell in tuple(x, y) form
        self.request = None

        # Offered cell in tuple(x, y) form
        self.offer = None

        self.start = start if start is not None else (random.randint(0, self.maze.rows-1), random.randint(0, self.maze.columns-1))
        self.finish = finish if finish is not None else (random.randint(0, self.maze.rows-1), random.randint(0, self.maze.columns-1))

        self.pos = Vector2D(self.start)

        self.score = 0
        self.moved = False
        
        self.full_discovered = False
        # Used after the maze is fully discovered and the path to the finish can be instantly calculated.
        self.next_best_move = []

    def reset_position(self):
        self.pos = Vector2D(self.start)
    
    def _move(self, dir):
        if not isinstance(dir, Vector2D):
            raise TypeError(f"Invalid type for direction <{dir}> provided: {type(dir)}")

        if dir not in (Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST):
            raise ValueError(f"Invalid direction provided {dir}.")

        self.pos += dir
        self.moved = True

    def win(self):
        return self.pos.x == self.finish[0] and self.pos.y == self.finish[1]
    
    def create_offer(self):
        '''
        Needs to be implented when inheriting this class
        '''

        # Look for a random known cell in the maze
        all_known_cells = []
        for i in range(self.maze.rows):
            for j in range(self.maze.columns):
                if self.name == "PlayerA" and self.maze.data[i][j].visibleA or \
                     self.name == "PlayerB" and self.maze.data[i][j].visibleB:
                    all_known_cells.append((i, j))
        
        self.offer = random.choice(all_known_cells)

    def create_request(self):
        '''
        Needs to be implented when inheriting this class
        '''

        # Look for a random unknown cell in the maze
        all_unknown_cells = []
        for i in range(self.maze.rows):
            for j in range(self.maze.columns):
                if self.name == "PlayerA" and not self.maze.data[i][j].visibleA or \
                     self.name == "PlayerB" and not self.maze.data[i][j].visibleB:
                    all_unknown_cells.append((i, j))
        
        self.request = random.choice(all_unknown_cells)

    def wants_negotiation(self) -> bool:
        '''
        Based on what this player knows, does it want to negociate?
        '''

        if self.full_discovered:
            print(f"[ {self.name} ] Does not want negociation because the full maze is known.")
            return False

        # Make a strategy to decide
        self.full_discovered = True
        for i in range(self.maze.rows):
            for j in range(self.maze.columns):
                if self.name == "PlayerA" and not self.maze.data[i][j].visibleA or \
                    self.name == "PlayerB" and not self.maze.data[i][j].visibleB:
                    self.full_discovered = False
                    break
        
        if self.full_discovered:
            print(f"[ {self.name} ] Does not want negociation because the full maze is known.")
            return False

        return True

    
    def proposal(self, offer, request, attempt=0) -> bool:
        '''
        Examine the offer and the request and determine if you are willing to accept the proposal.
        '''
        return random.random() > 0.5

    def is_visible(self, x_or_tuple, y=None):
        '''
        Is maze[x][y] visible to this player?
        '''

        if isinstance(x_or_tuple, tuple) and y is None:
            x = x_or_tuple[0]
            y = x_or_tuple[1]
        elif isinstance(x_or_tuple, int) and isinstance(y, int):
            x = x_or_tuple
            y = y
        else:
            raise TypeError(f"Got type <{type(x_or_tuple)}> for x and <{type(y)}> for y. Excepted either a tuple or two ints.")

        if self.name == "PlayerA":
            return self.maze.data[x][y].visibleA
        return self.maze.data[x][y].visibleB
        
        
    def best_move(self):
        # If the maze is fully discovered, the next best move is always known.
        if self.full_discovered:
            if len(self.next_best_move) == 0:
                # Compute all next moves
                solver = AStar(self.maze, start=(self.pos.x, self.pos.y), end=self.finish)
                solver.solve()
                
                for i in range(0, len(solver.steps) - 1):
                    a = Vector2D(solver.steps[i])
                    b = Vector2D(solver.steps[i+1])
                    self.next_best_move.append(b - a)

            self._move(self.next_best_move.pop(0))
            return

        self._move_strategy()
    
    def _move_strategy(self):
        '''
        Based on what the current situation is, determine what the best move is and perform it.
        To be overriden
        '''

        # Move in a random direction with more ephasys on exploration (unknown cells).
        next_cells = []
        for dir in self.maze.possible_actions(self.pos.x, self.pos.y):
            peek_cell = self.pos + dir
            if self.name == "PlayerA":
                if self.maze.data[peek_cell.x][peek_cell.y].visibleA:
                    next_cells.append(dir)
                else:
                    next_cells.append(dir)
                    next_cells.append(dir)
            else:
                if self.maze.data[peek_cell.x][peek_cell.y].visibleB:
                    next_cells.append(dir)
                else:
                    next_cells.append(dir)
                    next_cells.append(dir)

        self._move(random.choice(next_cells))