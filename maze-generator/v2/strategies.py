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

        self.strategy = []

    def create_request(self):
        '''
        Request the first (counting from the current position) unknown cell in the current DFS stack.
        '''

        self.request = None
        for cell in self.dfs_stack:
            if not self.is_visible(cell):
                self.request = cell
                break
        
        # If there are no more unknown cells, it should refuse any other negociation, right