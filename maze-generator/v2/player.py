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

        # All cells are tuples (x, y), not Vector2D!
        self.dfs_stack = []
        self._internal_dfs()
        
        # Recalculate the DFS path every X turns
        self.turn_counter = 0
        self.turn_recalculate = 10
        
        self.full_discovered = False
        # Used after the maze is fully discovered and the path to the finish can be instantly calculated.
        self.next_best_move = []

    def reset_position(self):
        '''
        Override the current @pos value with a Vector2D(self.start).\n
        Also recalculate DFS.
        '''
        self.pos = Vector2D(self.start)
        self._internal_dfs()
    
    def _move_old(self, dir):
        if not isinstance(dir, Vector2D):
            raise TypeError(f"[ {self.name} ] Invalid type for direction <{dir}> provided: {type(dir)}")

        if dir not in (Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST):
            raise ValueError(f"[ {self.name} ] Invalid direction provided {dir}.")

        self.pos += dir
        self.moved = True

    def _move(self, direction: tuple | Vector2D):
        if not isinstance(direction, tuple) and not isinstance(direction, Vector2D):
            raise TypeError(f"[ {self.name} ] Invalid type for direction <{direction}> provided: {type(direction)}")

        if isinstance(direction, tuple):
            direction = Vector2D(direction)
        
        if direction not in (Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST):
            print(f"[ {self.name} ] Invalid direction provided {direction}. Trying to convert it to an actual direction instead of a location...")
            new_direction = direction - self.pos

            if new_direction not in (Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST):
                raise ValueError(f"[ {self.name} ] Tried converting {direction} to {new_direction} but still failed...")

            direction = new_direction
        
        # NICE LOGIC
        # Discover a cell if you are trying to move towards it and you cannot.
        dest = self.pos + direction
        if self.maze.is_wall(self.pos.x, self.pos.y, dest.x, dest.y):
            print(f"[ Debug ][ {self.name} ] Hit a wall trying to go from {self.pos} to {dest}! Not moving this round...")
            if self.name == "PlayerA":
                self.maze.data[dest.x][dest.y].visibleA = True
            else:
                self.maze.data[dest.x][dest.y].visibleB = True
            self._internal_dfs()
            self.turn_counter = 0
        else:
            print(f"[ Debug ][ {self.name} ] Moving from {self.pos} to ", end="")
            print(f"{self.pos}.")
            self.pos += direction
            self.moved = True
        # END NICE LOGIC


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
        if self.full_discovered:
            print(f"[ {self.name} ] Does not want negociation because the full maze is known.")
            return False

        # Make a strategy to decide
        self.full_discovered = True
        for cell in self.dfs_stack:
            if not self.is_visible(cell):
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
            # dest = Vector2D(self.dfs_stack.pop(0))
            # position = dest - self.pos
            # self._move(position)
            # return
            self._move(self.dfs_stack.pop(0))
            return

        self._move_strategy()
    
    def _move_strategy(self):
        # Initial DFS
        if len(self.dfs_stack) == 0:
            self._internal_dfs()
        
        if self.turn_counter >= self.turn_recalculate:
            self._internal_dfs()
            self.turn_counter = 0
        else:
            self.turn_counter += 1
        
        self._move(self.dfs_stack.pop(0))
        # dest = Vector2D(self.dfs_stack.pop(0))
        # position = dest - self.pos

        # # NICE LOGIC
        # # Discover a cell if you are trying to move towards it and you cannot.
        # if self.maze.is_wall(self.pos.x, self.pos.y, dest.x, dest.y):
        #     print(f"[ Debug ][ {self.name} ] Hit a wall trying to go from {self.pos} to {dest}! Not moving this round...")
        #     if self.name == "PlayerA":
        #         self.maze.data[dest.x][dest.y].visibleA = True
        #     else:
        #         self.maze.data[dest.x][dest.y].visibleB = True
        #     self._internal_dfs()
        #     self.turn_counter = 0
        # else:
        #     print(f"[ Debug ][ {self.name} ] Moving from {self.pos} to ", end="")
        #     self._move(position)
        #     print(f"{self.pos}.")
        # # END NICE LOGIC

    def _distance_metric(self, start=None, end=None):

        if start is None:
            start = (self.pos.x, self.pos.y)
        if end is None:
            end = self.finish

        (x, y) = start
        (endx, endy) = end

        # Taxi cab
        return abs(x-endx) + abs(y-endy)

    def _internal_dfs(self):
        '''
        Perform a new DFS each time a cell adjacent to a previous visited cell or a future cell is discovered.\n
        '''

        # How much penalty should taking an unknown cell step add to the total distance
        unknown_penalty = 1.2

        print(f"[ Debug ][ {self.name} ] Recalculating DFS. From {self.start} to {self.finish}")

        self.dfs_stack.clear()
        self.dfs_stack.append((self.pos.x, self.pos.y))
        visited = []

        while self.dfs_stack[-1] != self.finish:
            if len(self.dfs_stack) == 0:
                raise ValueError(f"[{self.name}] Could not find a connected path from {self.start} to {self.finish}!")

            pqueue = []
            (x, y) = self.dfs_stack[-1]
            visited.append((x, y))

            # North
            if self.maze.is_valid_position(x-1, y):
                if not (x-1, y) in visited:
                    if self.is_visible(x-1, y):
                        if not self.maze.is_wall(x, y, x-1, y):
                            distance = self._distance_metric((x-1, y), self.finish)
                            pqueue.append((x-1, y, distance))
                    else:
                        distance = self._distance_metric((x-1, y), self.finish) * unknown_penalty
                        pqueue.append((x-1, y, distance))
            
            # East
            if self.maze.is_valid_position(x, y+1):
                if not (x, y+1) in visited:
                    if self.is_visible(x, y+1):
                        if not self.maze.is_wall(x, y, x, y+1):
                            distance = self._distance_metric((x, y+1), self.finish)
                            pqueue.append((x, y+1, distance))
                    else:
                        distance = self._distance_metric((x, y+1), self.finish) * unknown_penalty
                        pqueue.append((x, y+1, distance))
            
            # South
            if self.maze.is_valid_position(x+1, y):
                if not (x+1, y) in visited:
                    if self.is_visible(x+1, y):
                        if not self.maze.is_wall(x, y, x+1, y):
                            distance = self._distance_metric((x+1, y), self.finish)
                            pqueue.append((x+1, y, distance))
                    else:
                        distance = self._distance_metric((x+1, y), self.finish) * unknown_penalty
                        pqueue.append((x+1, y, distance))
            
            # West
            if self.maze.is_valid_position(x, y-1):
                if not (x, y-1) in visited:
                    if self.is_visible(x, y-1):
                        if not self.maze.is_wall(x, y, x, y-1):
                            distance = self._distance_metric((x, y-1), self.finish)
                            pqueue.append((x, y-1, distance))
                    else:
                        distance = self._distance_metric((x, y-1), self.finish) * unknown_penalty
                        pqueue.append((x, y-1, distance))

            if len(pqueue) != 0:
                # Sort the queue based on distance
                pqueue.sort(key=lambda tup:tup[2])
                self.dfs_stack.append((pqueue[0][0], pqueue[0][1]))
            else:
                self.dfs_stack.pop()

        self.dfs_stack.pop(0)
        print(f"[ Debug ][ {self.name} ] Recalculated DFS: {self.dfs_stack}")