import pygame
import random
from amazed.modules.maze import Maze, Vector2D

class Player():
    '''
    Default class which can be inherited to develop strategies
    '''
    def __init__(self, name, body: pygame.Rect, maze: Maze, start, finish):
        if name not in ("PlayerA", "PlayerB"):
            raise ValueError(f"Player name incorrect <{name}>")
        
        self.name = name
        self.body = body
        self.maze = maze
        self.pos = Vector2D(start)
        # self.pos.x = start.x
        # self.pos.y = start.y

        self.start = start
        self.finish = finish

        self.score = 0
        self.moved = False
    
    def move(self, dir):
        if dir not in (Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST):
            raise ValueError(f"Invalid direction provided {dir}")
        
        self.pos += dir
        self.score += 1
        self.moved = True

    def win(self):
        return self.pos.x == self.finish[0] and self.pos.y == self.finish[1]
    
    def wants_negociation(self) -> bool:
        '''
        Based on what this player knows, does it want to negociate?
        '''

        # Make a strategy to decide

        # If the answer is yes, proceed with offer & request.

        self.offer = self.start
        self.request = self.finish

        return True
    
    def proposal(self, offer, request, attempt=0) -> bool:
        '''
        Examine the offer and the request and determine if you are willing to accept the proposal.
        '''
        return random.random() > 0.5
        
        # if attempt == 0:
        #     return self.offer == request
        # if attempt == 1:
        #     return offer == self.request
        # if attempt == 2:
        #     return True
        
    def best_move(self):
        '''
        Based on what the current situation is, determine what the best move is and perform it.
        Only to be used when human interaction is not intended.
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

        print(f"[ best move ] Player {self.name} moved from {self.pos} ", end="")
        self.move(random.choice(next_cells))
        print(f"to {self.pos}")