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

        self.full_discovered = False
        self.energy_available = 0
        self.energy_used = 0
    
    def move(self, dir):
        if dir not in (Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST):
            raise ValueError(f"Invalid direction provided {dir}")
        
        self.pos += dir
        self.score += 1
        self.moved = True

    def win(self):
        return self.pos.x == self.finish[0] and self.pos.y == self.finish[1]
    
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

        # If the answer is yes, proceed with offer & request.

        self.offer = self.start
        self.request = self.finish

        return True
    
    def proposal(self, offer, request, attempt=0) -> bool:
        '''
        Examine the offer and the request and determine if you are willing to accept the proposal.
        '''
        return random.random() > 0.5

        
    def best_move(self):
        '''
        Based on what the current situation is, determine what the best move is and return it.
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

        return random.choice(next_cells)