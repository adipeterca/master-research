from pygame import Rect
from amazed.modules.maze import Maze
from player import *

class CopyPlayer(Player):
    
    def __init__(self, name, maze: Maze, start=None, finish=None):
        super().__init__(name, maze, start, finish)

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
    * 8 bytes represent MOFF (multiplier for offer distance)
    * 8 bytes represent MREQ (multiplier for request distance)
    * 8 bytes represent SCORE_THRESHOLD
    * 8 bytes represent DFS_EXPLORATION_CHANCE
    * 8 bytes represent ATTEMPT_MULTIPLIER (increase the chance that a negotiation will take place)

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

    Total length of the chromozome is CHROMOSOME_LENGTH bytes.
    Each field is described in detail in the full documentation.
    '''

    CHROMOSOME_LENGTH = 48

    def __init__(self, name, maze: Maze, start=None, finish=None):
        super().__init__(name, maze, start, finish)

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

            self.moff = int("".join(self.strategy[8:16]), base=2) / (2**8 - 1)
            self.mreq = int("".join(self.strategy[16:24]), base=2) / (2**8 - 1)

            self.score_threshold = int("".join(self.strategy[24:32]), base=2) / (2**8 - 1)

            # Value between [0, 15], that's why we divide by 15 -> scale it between [0, 1]
            self.dfs_exploration_chance = int("".join(self.strategy[32:40]), base=2) / (2**8 - 1)

            self.attempt_modifier = int("".join(self.strategy[40:48]), base=2) / (2**8 - 1)

        except TypeError as e:
            print(e)
            self.logger.error(e, extra={"who" : self.name})
            self.logger.error(f"Could not convert strategy <{strategy}> to int in base 2.", extra={"who" : self.name})
            raise RuntimeError(f"[{self.name}] Could not convert strategy <{strategy}> to int in base 2.")

        max_possible_distance = self._distance_metric((0, 0), (self.maze.rows-1, self.maze.columns-1))
        self.max_score = max_possible_distance * self.moff + max_possible_distance * self.mreq

    @classmethod
    def print_strategy(strategy):
        dnext = int("".join(strategy[0:4]), base=2) + 1
        dxnext = int("".join(strategy[4:8]), base=2) + 1

        moff = int("".join(strategy[8:16]), base=2) / (2**8 - 1)
        mreq = int("".join(strategy[16:24]), base=2) / (2**8 - 1)

        score_threshold = int("".join(strategy[24:32]), base=2) / (2**8 - 1)

        # Value between [0, 15], that's why we divide by 15 -> scale it between [0, 1]
        dfs_exploration_chance = int("".join(strategy[32:40]), base=2) / (2**8 - 1)

        attempt_modifier = int("".join(strategy[40:48]), base=2) / (2**8 - 1)

        print(f"dnext = {dnext}")
        print(f"dxnext = {dxnext}")
        print(f"moff = {moff}")
        print(f"mreq = {mreq}")
        print(f"score_threshold = {score_threshold}")
        print(f"dfs_exploration_chance = {dfs_exploration_chance}")
        print(f"attempt_modifier = {attempt_modifier}")
        

    def create_request(self):
        '''
        Request the next DNEXT unknown cell (or last unknown cell if DNEXT > number of unknown cells).
        '''

        if self.strategy is None:
            self.logger.error(f"You forgot to set the strategy for me!", extra={"who" : self.name})
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

        # if self.request is None:
        #     self.logger.error(f"I could not find a cell to request...", extra={"who" : self.name})
        #     raise RuntimeError("how can it be??")

        # Just a gimmick and for a better usability
        return self.request
    
    def create_offer(self):
        '''
        Try to offer an unknown cell from the DFS stack. If the opponents already knows
        all cells from the DFS stack, try to offer one of the requested cells.
        If this also fails, offer the DXNEXT random cell.
        '''

        if self.strategy is None:
            self.logger.error(f"You forgot to set the strategy for me!", extra={"who" : self.name})
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

        # if self.offer is None:
        #     self.logger.error(f"how??", extra={"who" : self.name})
        #     raise RuntimeError("how??")
            
        # Just a gimmick for better usability
        return self.offer
    
    def proposal(self, offer, request, attempt=0) -> bool:
        
        if self.strategy is None:
            self.logger.error(f"You forgot to set the strategy for me!", extra={"who" : self.name})
            raise RuntimeError(f"[ SimpleAgent ][ {self.name} ] You forgot to set the strategy for me!")
        
        if offer is None or request is None:
            return False
        if self.is_visible(offer) or self.is_visible(request):
            return False

        self.opponent_past_offers.append(offer)
        self.opponent_past_requests.append(request)

        curr_score = self._distance_metric(self.request, offer) * self.mreq + \
                     self._distance_metric(self.offer, request) * self.moff - \
                     attempt * self.attempt_modifier
        
        # Scale it between 0 and 15
        if self.max_score == 0:
            curr_score_adj = 0
        else:
            curr_score_adj = (curr_score / self.max_score)

        self.logger.info(f"Score for current proposal : {curr_score}", extra={"who" : self.name})
        self.logger.info(f"Score for current proposal, adjusted between [0, 1] : {curr_score_adj} (must be <= than {self.score_threshold})", extra={"who" : self.name})
        # print(f"[ SimpleAgent ][ {self.name} ] Proposal scores:")
        # print(f"\t\t\t self.offer : {self.offer}")
        # print(f"\t\t\t opponent.request : {request}")
        # print(f"\t\t\t self.request : {self.request}")
        # print(f"\t\t\t opponent.offer : {offer}")
        # print(f"\t\t\t current score : {curr_score}")
        # print(f"\t\t\t current score adjusted [0, 15] : {curr_score_adj}")
        # print(f"\t\t\t score threshold : {self.score_threshold}")
        return curr_score_adj <= self.score_threshold
    
    def _internal_dfs(self):
        '''
        Perform a new DFS each time a cell adjacent to a previous visited cell or a future cell is discovered.\n
        Use the DFS_EXPLORATION_RATE to sometimes include worse options in the event that they will lead to better outcomes, similar to Simulated Annealing.
        '''

        # How much penalty should taking an unknown cell step add to the total distance
        unknown_penalty = 1.2

        # print(f"[ Debug ][ {self.name} ] Recalculating DFS. From current position {self.pos} to finish at {self.finish}")
        self.logger.debug(f"Recalculating DFS. From current position {self.pos} to finish at {self.finish}", extra={"who": self.name})

        self.dfs_stack.clear()
        self.dfs_stack.append((self.pos.x, self.pos.y))
        visited = []

        while self.dfs_stack[-1] != self.finish:
            if len(self.dfs_stack) == 0:
                self.logger.error(f"Could not find a connected path from {self.start} to {self.finish}!", extra={"who": self.name})
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

                index = 0
                while random.random() <= self.dfs_exploration_chance:
                    
                    # This is to avoid selecting a cell that does not exist in the priority queue
                    if index == len(pqueue) - 1:
                        break

                    index += 1
                    self.dfs_exploration_chance *= 0.95

                self.dfs_stack.append((pqueue[index][0], pqueue[index][1]))
            else:
                self.dfs_stack.pop()

        self.dfs_stack.pop(0)
        # print(f"[ Debug ][ {self.name} ] Recalculated DFS: {self.dfs_stack}")
        self.logger.info(f"Recalculated DFS, starting from {self.pos}: {self.dfs_stack}", extra={"who": self.name})

class Human(Player):

    def __init__(self, name, maze: Maze, start=None, finish=None):
        super().__init__(name, maze, start, finish)

    def create_offer(self):
        print(f"[ Human ] Create offer:")
        while True:
            row = input(f"row (between [0, {self.maze.rows-1}]) = ")
            try:
                row = int(row)
            except:
                print(f"[ Error ] Provide an integer in base 10. You provided {row} as {type(row)}")
                continue
            
            column = input(f"column (between [0, {self.maze.columns-1}]) = ")
            try:
                column = int(column)
            except:
                print(f"[ Error ] Provide an integer in base 10. You provided {column} as {type(column)}")
                continue
            
            proceed = input(f"Selected ({row}, {column}) as an offer. Proceed? (y/n) ")
            if proceed.lower()[0] == "y":
                break
        print(f"Set offer to ({row}, {column}).")
        self.offer = (row, column)

        return self.offer

    def create_request(self):
        print(f"[ Human ] Create request:")
        while True:
            row = input(f"row (between [0, {self.maze.rows-1}]) = ")
            try:
                row = int(row)
            except:
                print(f"[ Error ] Provide an integer in base 10. You provided {row} as {type(row)}")
                continue
            
            column = input(f"column (between [0, {self.maze.columns-1}]) = ")
            try:
                column = int(column)
            except:
                print(f"[ Error ] Provide an integer in base 10. You provided {column} as {type(column)}")
                continue
            
            proceed = input(f"Selected ({row}, {column}) as an request. Proceed? (y/n) ")
            if proceed.lower()[0] == "y":
                break
        print(f"Set request to ({row}, {column}).")
        self.request = (row, column)

        return self.request

    def proposal(self, offer, request, attempt=0) -> bool:
        print(f"[ Human ] Attempted proposal number {attempt} :")

        print(f"My request: {self.request}")
        print(f"Opponent's offer: {offer}\n")
        print(f"My offer: {self.offer}")
        print(f"Opponent's request: {request}\n\n")

        proceed = input("Proceed? (y/n) ")
        if proceed[0].lower() != "y":
            print(f"Proposal refused!")
            return False
        
        print(f"Proposal accepted!")
        return True
