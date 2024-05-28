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

        
class SimpleAgent(Player):
    '''
    Class implementing a GA strategy.
    
    The chromosome is structured as follows:
    * 4 bytes represent DNEXT
    * 4 bytes represent DXNEXT
    * 3 bytes represent MOFF (multiplier for offer distance)
    * 3 bytes represent MREQ (multiplier for request distance)
    * 4 bytes represent SCORE_THRESHOLD

    (req - xoff) = 0 e ce vreau eu
    altfel deviaza de la ce am cerut (nu iau in calcul posibilitatea ca imi ofera ceva "mai bun")

    (off - xreq) = 0 cere ce ii ofer eu
    altfel deviaza de la ce i-am cerut

    daca scorul este 0 - foarte bine, 100%
    cu cat devine scorul mai mare, cu atat sa fie mai unlikely sa il accept.
    multiplierele sunt acolo pentru ca putem pune accent mai mult pe
    "vreau sa obtin oferta mea, nu mi pasa ce dau la schimb" sau alte strategii asemanatoare.

    SCORE_THRESHOLD va fi folosit pentru a determina daca schimbul este bun/rau.
    avand doar 16 valori posibile, vor face un clamp la valoarea scorului intre [0, 15], dupa
    care o voi compara cu SCORE_THRESHOLD. Scorul maxim il pot calcula la inceput.
    Ar veni cam asa:

    curr_score / max_score * 15

    Total length of the chromozome is 8 bytes.
    Each field is described in detail in the full documentation.
    '''

    CHROMOSOME_LENGTH = 18

    def __init__(self, name, body: Rect, maze: Maze, start=None, finish=None):
        super().__init__(name, body, maze, start, finish)

        self.strategy = None
        self.opponent_past_offers = []
        self.opponent_past_requests = []

    def set_strategy(self, strategy: list):
        if strategy is None:
            self.strategy = []
            for i in range(self.CHROMOSOME_LENGTH):
                if random.random() > 0.5:
                    self.strategy.append("0")
                else:
                    self.strategy.append("1")
        else:
            self.strategy = strategy
        try:
            self.dnext = int("".join(self.strategy[0:4]), base=2) + 1
            self.dxnext = int("".join(self.strategy[4:8]), base=2) + 1

            self.moff = int("".join(self.strategy[8:11]), base=2)
            self.mreq = int("".join(self.strategy[11:14]), base=2)

            self.score_threshold = int("".join(self.strategy[14:]), base=2)
        except TypeError as e:
            print(e)
            raise RuntimeError(f"Could not convert strategy <{strategy}> to int in base 2.")

        max_possible_distance = self._distance_metric((0, 0), (self.maze.rows-1, self.maze.columns-1))
        self.max_score = max_possible_distance * self.moff + max_possible_distance * self.mreq

    def create_request(self):
        '''
        Request the next DNEXT unknown cell (or last unknown cell if DNEXT > number of unknown cells).
        '''

        if self.strategy is None:
            raise RuntimeError(f"[ SimpleAgent ][ {self.name} ] You forgot to set the strategy for me!")

        self.request = None

        countdown = self.dnext
        last_unknown_cell = None
        for cell in self.dfs_stack:
            if not self.is_visible(cell):
                countdown -= 1
                last_unknown_cell = cell
                if countdown == 0:
                    self.request = cell
                    break

        if self.request is None:
            self.request = last_unknown_cell

        if self.request is None:
            print("[ Debug ][ SimpleAgent ][ {self.name} ] I could not find a cell to offer...")
            raise RuntimeError("how can it be??")

        # Just a gimmick and for a better usability
        return self.request
    
    def create_offer(self):
        '''
        Try to offer an unknown cell from the DFS stack. If the opponents already knows
        all cells from the DFS stack, try to offer one of the requested cells.
        If this also fails, offer the DXNEXT random cell.
        '''

        if self.strategy is None:
            raise RuntimeError(f"[ SimpleAgent ][ {self.name} ] You forgot to set the strategy for me!")

        self.offer = None

        last_known_cell = None
        countdown = self.dxnext
        for cell in reversed(self.dfs_stack):
            if self.is_visible(cell) and not self.is_visible_to_opponent(cell):
                countdown -= 1
                last_known_cell = cell
                if countdown == 0:
                    self.offer = cell
                    break

        if self.offer is None:
            self.offer = last_known_cell

        # No unknown cells were found in the DFS stack
        if self.offer is None:
            for cell in reversed(self.opponent_past_requests):
                if self.is_visible(cell) and not self.is_visible_to_opponent(cell):
                    self.offer = cell
                    break
        
        if self.offer is None:
            countdown = self.dxnext
            last_known_cell = None
            for i in range(self.maze.rows):
                for j in range(self.maze.columns):
                    cell = (i, j)
                    if self.is_visible(cell) and not self.is_visible_to_opponent(cell):
                        countdown -= 1
                        last_known_cell = cell
                        if countdown == 0:
                            self.offer = cell
                            break
            if self.offer is None:
                self.offer = last_known_cell

        if self.offer is None:
            raise RuntimeError("how??")
            
        # Just a gimmick for better usability
        return self.offer
    
    def proposal(self, offer, request, attempt=0) -> bool:
        
        if self.strategy is None:
            raise RuntimeError(f"[ SimpleAgent ][ {self.name} ] You forgot to set the strategy for me!")

        self.opponent_past_offers.append(offer)
        self.opponent_past_requests.append(request)

        curr_score = self._distance_metric(self.request, offer) * self.mreq + \
                     self._distance_metric(self.offer, request) * self.moff
        
        # Scale it between 0 and 15
        curr_score_adj = (curr_score / self.max_score) * 15

        print(f"[ SimpleAgent ][ {self.name} ] Proposal scores:")
        print(f"\t\t\t self.offer : {self.offer}")
        print(f"\t\t\t opponent.request : {request}")
        print(f"\t\t\t self.request : {self.request}")
        print(f"\t\t\t opponent.offer : {offer}")
        print(f"\t\t\t current score : {curr_score}")
        print(f"\t\t\t current score adjusted [0, 15] : {curr_score_adj}")
        print(f"\t\t\t score threshold : {self.score_threshold}")
        return curr_score_adj <= self.score_threshold