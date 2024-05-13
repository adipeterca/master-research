from pygame import Rect
from amazed.modules.maze import Maze
from player import *

class CopyPlayer(Player):
    
    def __init__(self, name, body: Rect, maze: Maze, start=None, finish=None):
        super().__init__(name, body, maze, start, finish)

        # (opponent_offer, opponent_request, result)
        self.past_negotiations = []

    def create_offer(self):

        if len(self.past_negotiations) == 0 or self.past_negotiations[-1][2]:
            # Offer a random cell
            all_known_cells = []
            for i in range(self.maze.rows):
                for j in range(self.maze.columns):
                    if self.name == "PlayerA" and self.maze.data[i][j].visibleA or \
                        self.name == "PlayerB" and self.maze.data[i][j].visibleB:
                        all_known_cells.append((i, j))
            
            self.offer = random.choice(all_known_cells)
        else:
            self.offer = self.past_negotiations[-1][1]
    
    def create_request(self):

        if len(self.past_negotiations) == 0 or self.past_negotiations[-1][2]:
            # request a random cell
            all_unknown_cells = []
            for i in range(self.maze.rows):
                for j in range(self.maze.columns):
                    if self.name == "PlayerA" and not self.maze.data[i][j].visibleA or \
                        self.name == "PlayerB" and not self.maze.data[i][j].visibleB:
                        all_unknown_cells.append((i, j))
            
            self.request = random.choice(all_unknown_cells)
        else:
            self.request = self.past_negotiations[-1][0]
    
    def proposal(self, offer, request, attempt=0) -> bool:

        if self.offer == request or self.request == offer:
            result = True
        else:
            # Here the "attempt" factor will give a greater chance of acceptance
            result = random.random() + attempt / 30 > 0.5

        self.past_negotiations.append((offer, request, result))
        
        return result

        
class Agent(Player):

    def __init__(self, name, body: Rect, maze: Maze, start=None, finish=None):
        super().__init__(name, body, maze, start, finish)

        self.dfs_stack = []
        self.turn_counter = 0
        self.turn_recalculate = 5       # Recalculate the DFS path every 5 turns
    

    def _move_strategy(self):
        # Initial DFS
        if len(self.dfs_stack) == 0:
            self._internal_dfs()
        
        if self.turn_counter == self.turn_recalculate:
            self._internal_dfs()
            self.turn_counter = 0
        else:
            self.turn_counter += 1
        
        
        dest = Vector2D(self.dfs_stack.pop(0))
        position = dest - self.pos

        # NICE LOGIC
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
            self._move(position)
            print(f"{self.pos}.")
        # END NICE LOGIC
        
    def _internal_dfs(self):
        # Perform a new DFS each time a cell adjacent to a previous visited cell or a future cell is discovered.
        print(f"[ Debug ][ {self.name} ] Recalculating DFS.")
        def h(start, end):
            (x, y) = start
            (endx, endy) = end

            # Taxi cab
            return abs(x-endx) + abs(y-endy)

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
                    if self.visible(x-1, y):
                        if not self.maze.is_wall(x, y, x-1, y):
                            distance = h((x-1, y), self.finish)
                            pqueue.append((x-1, y, distance))
                    else:
                        distance = h((x-1, y), self.finish) * 1.2
                        pqueue.append((x-1, y, distance))
            
            # East
            if self.maze.is_valid_position(x, y+1):
                if not (x, y+1) in visited:
                    if self.visible(x, y+1):
                        if not self.maze.is_wall(x, y, x, y+1):
                            distance = h((x, y+1), self.finish)
                            pqueue.append((x, y+1, distance))
                    else:
                        distance = h((x, y+1), self.finish) * 1.2
                        pqueue.append((x, y+1, distance))
            
            # South
            if self.maze.is_valid_position(x+1, y):
                if not (x+1, y) in visited:
                    if self.visible(x+1, y):
                        if not self.maze.is_wall(x, y, x+1, y):
                            distance = h((x+1, y), self.finish)
                            pqueue.append((x+1, y, distance))
                    else:
                        distance = h((x+1, y), self.finish) * 1.2
                        pqueue.append((x+1, y, distance))
            
            # West
            if self.maze.is_valid_position(x, y-1):
                if not (x, y-1) in visited:
                    if self.visible(x, y-1):
                        if not self.maze.is_wall(x, y, x, y-1):
                            distance = h((x, y-1), self.finish)
                            pqueue.append((x, y-1, distance))
                    else:
                        distance = h((x, y-1), self.finish) * 1.2
                        pqueue.append((x, y-1, distance))

            if len(pqueue) != 0:
                # Sort the queue based on distance
                pqueue.sort(key=lambda tup:tup[2])
                self.dfs_stack.append((pqueue[0][0], pqueue[0][1]))
            else:
                self.dfs_stack.pop()

        self.dfs_stack.pop(0)