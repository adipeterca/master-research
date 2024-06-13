from amazed.modules.maze import Maze
from amazed.modules.build import DepthFirstSearch
from amazed.modules.build import Sculptor
from amazed.modules.solver import AStar
from strategies import SimpleAgent
from strategies import Player



import random
import pygame
import pygame.freetype
import logging

from threading import Thread

class Button():
    def __init__(self, body: pygame.Rect, text: str, color: tuple = (180, 180, 180), text_color: tuple = (25, 25, 25)):
        self.body = body
        self.colorEnabled = color
        self.colorDisabled = ((color[0] - 40) % 255, (color[1] - 40) % 255, (color[2] - 40) % 255)
        self.text = text
        self.text_color = text_color
        self.enabled = True

    def inside(self, pos):
        (x, y) = pos
        return self.body.left < x and x < self.body.right and self.body.top < y and y < self.body.bottom


class GameMaster():

    PLAYER_A = (29, 245, 74)
    VIEW_A = (0, 146, 21)
    FINISH_A = (40, 255, 71)

    PLAYER_B = (198, 29, 235)
    VIEW_B = (140, 30, 93)
    FINISH_B = (255, 91, 185)

    UNKNOWN = (50, 50, 50)
    VIEW_ALL = (180, 180, 180)
    VIEW_HIDDEN = (15, 15, 15)

    # GameStates
    NONE = 0
    RUNNING = 1
    QUIT = 2
    PAUSED = 3
    WAITING_FOR_USER_INPUT = 4
    WIN_A = 5
    WIN_B = 6
    DRAW = 7
    UPDATE_POSITION = 8
    USER_QUIT = 9

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    class GameCell(Maze.Cell):
        def __init__(self):
            super().__init__()

            self.visibleA = False
            self.visibleB = False


    def __init__(self, maze_algorithm_class: Sculptor = DepthFirstSearch, seed = 0, playerA : Player=None, playerB : Player=None):
        self._maze_algorithm_class = maze_algorithm_class
        self._seed = seed

        self.maze = Maze(10, 10, self.GameCell)
        self.total_possible_negotiations = 0
        self.total_negotiations_attempts = 0
        self.successful_negotiations = 0

        # Logging settings
        self.logger = logging.getLogger("GameMaster")
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler("gamemaster.log", mode="w")
        file_handler.setFormatter(logging.Formatter("[ %(levelname)s ][ %(who)s ] %(message)s"))
        self.logger.addHandler(file_handler)

        # General settings
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("B O T H")

        self.FONT = pygame.freetype.SysFont("bahnschrift", 20)
        self.wall_gap = 5

        # Board settings
        self.board_bk = pygame.Rect((150, 50, 500+self.wall_gap, 500+self.wall_gap))
        self.cell_width = (self.board_bk.width - (self.maze.rows + 1) * self.wall_gap) // self.maze.rows
        self.cell_height = (self.board_bk.height - (self.maze.columns + 1) * self.wall_gap) // self.maze.columns
        self.board_cell = pygame.Rect((0, 0, self.cell_width, self.cell_height))
        self.board_wall_vertical = pygame.Rect((0, 0, self.wall_gap, self.cell_height))
        self.board_wall_horizontal = pygame.Rect((0, 0, self.cell_width, self.wall_gap))

        self.board_lower = pygame.Rect((0, self.SCREEN_HEIGHT-30, self.SCREEN_WIDTH, 30))

        # Buttons
        self.buttonLoop = Button(pygame.Rect((self.board_bk.left-120, self.board_bk.top+50, 100, 50)), "LOOP START")
        self.buttonNextMove = Button(pygame.Rect((self.board_bk.left-120, self.board_bk.top+150, 100, 50)), "NEXT MOVE")

        # Players settings
        if playerA is None:
            self.playerA = SimpleAgent("PlayerA", maze=self.maze)
        else:
            self.playerA = playerA
        
        if playerB is None:
            self.playerB = SimpleAgent("PlayerB", maze=self.maze)
        else:
            self.playerB = playerB

        # We need two separate models because we will modify each one respectively
        # and the update function is called only once.
        self.playerAModel = pygame.Rect((0, 0, self.cell_width//2, self.cell_height//2))
        self.playerBModel = pygame.Rect((0, 0, self.cell_width//2, self.cell_height//2))
        
        self.finishA = pygame.Rect((0, 0, self.cell_width // 4, self.cell_height // 4))
        self.finishB = pygame.Rect((0, 0, self.cell_width // 4, self.cell_height // 4))

        self.set_state(self.NONE)

    def set_state(self, new_state):
        '''
        Use this to avoid overriding states from multiple threads.
        '''
        if new_state == self.NONE:
            self.state = self.NONE
            self.logger.info(f"State reset!", extra={"who":"GameMaster"})
            return

        # Do not update the state in this situation
        if self.state in (self.WIN_A, self.WIN_B, self.DRAW, self.QUIT, self.USER_QUIT):
            self.logger.info(f"Could not update the state from {self.state} to {new_state} because of stuff.", extra={"who":"GameMaster"})
            return

        self.logger.debug(f"Changed state {self.state} to {new_state}", extra={"who":"GameMaster"})
        self.state = new_state

    def _create_maze(self):
        '''
        Destroys the current maze and recreates it.
        '''
        self.maze.reset()
        self._maze_algorithm_class(self.maze, seed=self._seed, gif=False)
        # DepthFirstSearch(self.maze, gif=False)

        # playerA_count = 0
        # playerB_count = 0

        # Randomly distribute each player a set of cells
        for i in range(self.maze.rows):
            for j in range(self.maze.columns):
                self.maze.data[i][j].visibleA = False
                self.maze.data[i][j].visibleB = False
                # if random.random() > 0.5:
                #     if playerA_count < self.maze.rows * self.maze.columns / 2:
                #         self.maze.data[i][j].visibleA = True
                #         self.maze.data[i][j].visibleB = False
                #         playerA_count += 1
                #     else:
                #         self.maze.data[i][j].visibleA = False
                #         self.maze.data[i][j].visibleB = True
                #         playerB_count += 1
                # else:
                #     if playerB_count < self.maze.rows * self.maze.columns / 2:
                #         self.maze.data[i][j].visibleA = False
                #         self.maze.data[i][j].visibleB = True
                #         playerB_count += 1
                #     else:
                #         self.maze.data[i][j].visibleA = True
                #         self.maze.data[i][j].visibleB = False
                #         playerA_count += 1
                # if self.maze.data[i][j].visibleA and self.maze.data[i][j].visibleB:
                #     # print(f"Marked cell {i}, {j} as visible to both.")
                #     self.logger.debug(f"Marked cell {i}, {j} as visible to both.", extra={"who": "GameMaster"})

        self.playerA.maze = self.maze
        self.playerB.maze = self.maze


    def _create_start_finish(self):
        
        # # #
        # ALMOST ZERO SUM GAME
        start_A = (random.randint(0, self.maze.rows-1), random.randint(0, self.maze.columns-1))
        finish_A = (random.randint(0, self.maze.rows-1), random.randint(0, self.maze.columns-1))
        while start_A == finish_A:
            finish_A = (random.randint(0, self.maze.rows-1), random.randint(0, self.maze.columns-1))
        start_B = finish_A
        finish_B = start_A
        # # #

        # print(f"[ Debug ][ GameMaster ] Set new start/finish positions for both players.\n\t\tPlayerA.start = {start_A}, PlayerA.finish = {finish_A}\n\t\tPlayerB.start = {start_B}, PlayerB.finish = {finish_B}")
        self.logger.info(f"Set new start/finish positions for both players.\n\t\tPlayerA.start = {start_A}, PlayerA.finish = {finish_A}\n\t\tPlayerB.start = {start_B}, PlayerB.finish = {finish_B}", extra={"who": "GameMaster"})
        self.playerA.start = start_A
        self.playerA.finish = finish_A
        self.playerA.reset_position()
        
        self.playerB.start = start_B
        self.playerB.finish = finish_B
        self.playerB.reset_position()

    def _draw_screen(self):
        self.screen.fill((255, 255, 255))
        self.screen.fill((0, 0, 0), self.board_bk)

        for i in range(self.maze.rows):
            self.board_cell.top = self.board_bk.top + i*self.board_cell.height + (i+1)*self.wall_gap
            for j in range(self.maze.columns):
                self.board_cell.left = self.board_bk.left + j*self.board_cell.width + (j+1)*self.wall_gap

                wall_color = None
                if self.maze.data[i][j].visibleA and self.maze.data[i][j].visibleB:
                    pygame.draw.rect(self.screen, self.VIEW_ALL, self.board_cell)
                    wall_color = self.VIEW_ALL
                elif self.maze.data[i][j].visibleA:
                    pygame.draw.rect(self.screen, self.VIEW_A, self.board_cell)
                    wall_color = self.VIEW_A
                elif self.maze.data[i][j].visibleB:
                    pygame.draw.rect(self.screen, self.VIEW_B, self.board_cell)
                    wall_color = self.VIEW_B
                else:
                    pygame.draw.rect(self.screen, self.VIEW_HIDDEN, self.board_cell)
                    wall_color = self.VIEW_HIDDEN

                # Clear the wall if not present
                if not self.maze.data[i][j].walls[Maze.EAST]:
                    self.board_wall_vertical.top = self.board_cell.top
                    self.board_wall_vertical.left = self.board_cell.right
                    pygame.draw.rect(self.screen, wall_color, self.board_wall_vertical)
                if not self.maze.data[i][j].walls[Maze.SOUTH]:
                    self.board_wall_horizontal.top = self.board_cell.bottom
                    self.board_wall_horizontal.left = self.board_cell.left
                    pygame.draw.rect(self.screen, wall_color, self.board_wall_horizontal)
        
        self.finishA.top = self.board_bk.top + self.playerA.finish[0]*self.board_cell.height + (self.playerA.finish[0]+1)*self.wall_gap + self.cell_height * 0.4
        self.finishA.left = self.board_bk.left + self.playerA.finish[1]*self.board_cell.width + (self.playerA.finish[1]+1)*self.wall_gap + self.cell_height * 0.4
        pygame.draw.rect(self.screen, self.FINISH_A, self.finishA)

        self.finishB.top = self.board_bk.top + self.playerB.finish[0]*self.board_cell.height + (self.playerB.finish[0]+1)*self.wall_gap + self.cell_height * 0.4
        self.finishB.left = self.board_bk.left + self.playerB.finish[1]*self.board_cell.width + (self.playerB.finish[1]+1)*self.wall_gap + self.cell_height * 0.4
        pygame.draw.rect(self.screen, self.FINISH_B, self.finishB)

        self.playerAModel.top = self.board_bk.top + self.playerA.pos.x*self.board_cell.height + (self.playerA.pos.x+1)*self.wall_gap + self.cell_height * 0.25
        self.playerAModel.left = self.board_bk.left + self.playerA.pos.y*self.board_cell.width + (self.playerA.pos.y+1)*self.wall_gap + self.cell_width * 0.25
        pygame.draw.rect(self.screen, self.PLAYER_A, self.playerAModel)

        self.playerBModel.top = self.board_bk.top + self.playerB.pos.x*self.board_cell.height + (self.playerB.pos.x+1)*self.wall_gap + self.cell_height * 0.25
        self.playerBModel.left = self.board_bk.left + self.playerB.pos.y*self.board_cell.width + (self.playerB.pos.y+1)*self.wall_gap + self.cell_width * 0.25
        pygame.draw.rect(self.screen, self.PLAYER_B, self.playerBModel)

        if self.buttonLoop.enabled:
            pygame.draw.rect(self.screen, self.buttonLoop.colorEnabled, self.buttonLoop.body)
            self.FONT.render_to(self.screen, (self.buttonLoop.body.x+20, self.buttonLoop.body.y+30), "STOP", self.buttonLoop.text_color)
        else:
            pygame.draw.rect(self.screen, self.buttonLoop.colorDisabled, self.buttonLoop.body)
            self.FONT.render_to(self.screen, (self.buttonLoop.body.x+20, self.buttonLoop.body.y+30), "START", self.buttonLoop.text_color)
        self.FONT.render_to(self.screen, (self.buttonLoop.body.x+25, self.buttonLoop.body.y+7), "LOOP", self.buttonLoop.text_color)

        if self.buttonNextMove.enabled:
            pygame.draw.rect(self.screen, self.buttonNextMove.colorEnabled, self.buttonNextMove.body)
        else:
            pygame.draw.rect(self.screen, self.buttonNextMove.colorDisabled, self.buttonNextMove.body)
        self.FONT.render_to(self.screen, (self.buttonNextMove.body.x+23, self.buttonNextMove.body.y+7), "NEXT", self.buttonNextMove.text_color)
        self.FONT.render_to(self.screen, (self.buttonNextMove.body.x+20, self.buttonNextMove.body.y+30), "MOVE", self.buttonNextMove.text_color)

        self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2-200, 20), f"SCORE: {self.playerA.rounds_won}", self.PLAYER_A)
        self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2-50, 20), f"ITERATION: {self.iteration}", (0, 0, 0))
        self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2+130, 20), f"SCORE: {self.playerB.rounds_won}", self.PLAYER_B)

        self.FONT.render_to(self.screen, (self.SCREEN_WIDTH-120, self.SCREEN_HEIGHT//2-50), f"DISTANCE", (0, 0, 0))
        self.FONT.render_to(self.screen, (self.SCREEN_WIDTH-120, self.SCREEN_HEIGHT//2-25), f"TO FINISH", (0, 0, 0))
        self.FONT.render_to(self.screen, (self.SCREEN_WIDTH-100, self.SCREEN_HEIGHT//2), f"A: {len(self.playerA.dfs_stack)}", self.PLAYER_A)
        self.FONT.render_to(self.screen, (self.SCREEN_WIDTH-100, self.SCREEN_HEIGHT//2+25), f"B: {len(self.playerB.dfs_stack)}", self.PLAYER_B)

        pygame.display.update()

    def _update_game(self):

        # Change this to 1. Having the negotiation step set to 3 is too much.
        for i in range(3):
            self.total_possible_negotiations += 1
            if self.playerA.wants_negotiation() and self.playerB.wants_negotiation():
                self.total_negotiations_attempts += 1
                # print(f"[ Negotiation ] Attempt number {i}:")
                self.logger.info(f"Attempt number {i}:", extra={"who": "Negotiation"})

                
                self.playerA.create_offer()
                self.playerA.create_request()

                self.playerB.create_offer()
                self.playerB.create_request()

                # print(f"[ Negotiation ] A proposal is: \n\tOFFER {self.playerA.offer}\n\tREQUEST {self.playerA.request}")
                self.logger.debug(f"A proposal is: \n\tOFFER {self.playerA.offer}\n\tREQUEST {self.playerA.request}", extra={"who": "Negotiation"})
                # print(f"[ Negotiation ] B proposal is: \n\tOFFER {self.playerB.offer}\n\tREQUEST {self.playerB.request}")
                self.logger.debug(f"B proposal is: \n\tOFFER {self.playerB.offer}\n\tREQUEST {self.playerB.request}", extra={"who": "Negotiation"})


                resultA = self.playerA.proposal(self.playerB.offer, self.playerB.request, i)
                resultB = self.playerB.proposal(self.playerA.offer, self.playerA.request, i)
                if resultA and resultB:
                    # print(f"[ Negotiation ] Succes!")
                    self.logger.info("Succes!", extra={"who": "Negotiation"})

                    self.successful_negotiations += 1

                    self.maze.data[self.playerB.offer[0]][self.playerB.offer[1]].visibleA = True
                    self.maze.data[self.playerA.offer[0]][self.playerA.offer[1]].visibleB = True

                    break
                else:
                    # print(f"[ Negotiation ] Attempt {i} failed!")
                    self.logger.info(f"Attempt {i} failed!", extra={"who": "Negotiation"})

                    if resultA and not resultB:
                        self.logger.debug("PlayerA was OK with the trader, but PlayerB refused.", extra={"who":"Negotiation"})
                    elif resultB and not resultA:
                        self.logger.debug("PlayerB was OK with the trader, but PlayerA refused.", extra={"who":"Negotiation"})
                    else:
                        self.logger.debug("Both players refused.", extra={"who":"Negotiation"})


            else:
                break
        # print("[ Negotiation ] The negotiation period ended.")

        self.playerA.best_move()
        self.playerB.best_move()

        self.maze.data[self.playerA.pos.x][self.playerA.pos.y].visibleA = True
        self.maze.data[self.playerB.pos.x][self.playerB.pos.y].visibleB = True

        if self.playerA.win() and self.playerB.win():
            
            self.set_state(self.DRAW)
            self.playerA.rounds_won += 1
            self.playerB.rounds_won += 1

            # # GA related settings
            # self.playerA.individual_score += 1
            # self.playerB.individual_score += 1
            self.playerA.individual_score += 0.5
            self.playerB.individual_score += 0.5
            # # #

            self.logger.info("The game finished in a draw.", extra={"who": "GameMaster"})

        elif self.playerA.win():
            # self.state = self.WIN_A
            self.set_state(self.WIN_A)
            self.playerA.rounds_won += 1

            # # GA related settings
            # self.playerA.individual_score += 2
            self.playerA.individual_score += 1
            astar = AStar(self.maze, start=self.playerB.pos.to_tuple(), end=self.playerB.finish)
            astar.solve()
            # self.playerB.individual_score -= 1
            self.playerB.individual_score += 1 / len(astar.steps)
            # # #

            self.logger.info("A won the game.", extra={"who": "GameMaster"})

        elif self.playerB.win():
            # self.state = self.WIN_B
            self.set_state(self.WIN_B)
            self.playerB.rounds_won += 1

            # # GA related settings
            # self.playerB.individual_score += 2
            # self.playerA.individual_score -= 1
            self.playerB.individual_score += 1
            astar = AStar(self.maze, start=self.playerA.pos.to_tuple(), end=self.playerA.finish)
            astar.solve()
            # self.playerB.individual_score -= 1
            self.playerA.individual_score += 1 / len(astar.steps)
            # # #
            self.logger.info("B won the game.", extra={"who": "GameMaster"})

        elif self.state == self.QUIT: 
            return
        
        else:
            # self.state = self.RUNNING
            self.set_state(self.RUNNING)
        
        if self.iteration >= 300:
            # print("[ Info ][ GameMaster ] Iteration count over 500. Marking the game as a draw.")
            self.logger.info("Iteration count over 300. Marking the game as a draw.", extra={"who": "GameMaster"})
            # self.state = self.DRAW
            self.set_state(self.DRAW)
            # self.playerA.individual_score -= 2
            # self.playerB.individual_score -= 2
            astar = AStar(self.maze, start=self.playerA.pos.to_tuple(), end=self.playerA.finish)
            astar.solve()
            # self.playerB.individual_score -= 1
            self.playerA.individual_score += 1 / len(astar.steps)

            astar = AStar(self.maze, start=self.playerB.pos.to_tuple(), end=self.playerB.finish)
            astar.solve()
            # self.playerB.individual_score -= 1
            self.playerB.individual_score += 1 / len(astar.steps)
            
        else:
            self.iteration += 1


    def _draw_results(self):

        font = pygame.freetype.SysFont("bahnschrift", 40)

        if self.state == self.WIN_A:
            font.render_to(self.screen, (self.SCREEN_WIDTH//2-120, self.SCREEN_HEIGHT//2), "And the winner is...", (255, 255, 255))
            font.render_to(self.screen, (self.SCREEN_WIDTH//2-120, self.SCREEN_HEIGHT//2+60), "Player A!", (255, 255, 255))
        elif self.state == self.WIN_B:
            font.render_to(self.screen, (self.SCREEN_WIDTH//2-120, self.SCREEN_HEIGHT//2), "And the winner is...", (255, 255, 255))
            font.render_to(self.screen, (self.SCREEN_WIDTH//2-120, self.SCREEN_HEIGHT//2+60), "Player B!", (255, 255, 255))
        else:
            font.render_to(self.screen, (self.SCREEN_WIDTH//2-120, self.SCREEN_HEIGHT//2), "And it's a draw!", (255, 255, 255))

        pygame.display.update()
        

    def _game_thread(self, rounds: int=1):
        '''
        Any loops that you create inside the "while" main loop must have a check for self.state!
        '''

        # Holds who exactly won in each round
        self.results = []
        for round in range(1, rounds+1):
            
            # self.state = self.RUNNING

            # First reset, the set.
            self.set_state(self.NONE)
            self.set_state(self.RUNNING)
            self.iteration = 0

            self.logger.info(f"Starting round {round}...", extra={"who": "GameMaster"})

            
            # Reset players & maze for a new game iteration.
            self._create_maze()
            self._create_start_finish()

            (x, y) = self.playerA.pos.to_tuple()
            self.maze.data[x][y].visibleA = True
            if self.maze.is_valid_position(x-1, y): self.maze.data[x-1][y].visibleA = True
            if self.maze.is_valid_position(x, y+1): self.maze.data[x][y+1].visibleA = True
            if self.maze.is_valid_position(x+1, y): self.maze.data[x+1][y].visibleA = True
            if self.maze.is_valid_position(x, y-1): self.maze.data[x][y-1].visibleA = True
            
            (x, y) = self.playerB.pos.to_tuple()
            self.maze.data[x][y].visibleB = True
            if self.maze.is_valid_position(x-1, y): self.maze.data[x-1][y].visibleB = True
            if self.maze.is_valid_position(x, y+1): self.maze.data[x][y+1].visibleB = True
            if self.maze.is_valid_position(x+1, y): self.maze.data[x+1][y].visibleB = True
            if self.maze.is_valid_position(x, y-1): self.maze.data[x][y-1].visibleB = True

            # print(f"[ Debug ][ PlayerA ] (after recalculation) Start from {self.playerA.start} and finish at {self.playerA.finish}.")
            self.logger.debug(f"(after recalculation) Start from {self.playerA.start} and finish at {self.playerA.finish}.", extra={"who": "PlayerA"})

            # print(f"[ Debug ][ PlayerB ] (after recalculation) Start from {self.playerB.start} and finish at {self.playerB.finish}.")
            self.logger.debug(f"(after recalculation) Start from {self.playerB.start} and finish at {self.playerB.finish}.", extra={"who": "PlayerB"})

            # Both players know where they start from
            self.maze.data[self.playerA.pos.x][self.playerA.pos.y].visibleA = True
            self.maze.data[self.playerB.pos.x][self.playerB.pos.y].visibleB = True

            # Both players know where they the finish goal is
            self.maze.data[self.playerA.finish[0]][self.playerA.finish[1]].visibleA = True
            self.maze.data[self.playerB.finish[0]][self.playerB.finish[1]].visibleB = True

            while self.state != self.QUIT:
                self._draw_screen()

                if self.state in (self.WIN_A, self.WIN_B, self.DRAW):
                    self._draw_results()
                    self.results.append((self.state, self.iteration))

                    # If it is not the last round
                    if round != rounds and not self.training:
                        countdown_seconds = 5
                        for second in range(countdown_seconds, 0, -1):
                            self.screen.fill((255, 255, 255), self.board_lower)
                            self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2-170, self.SCREEN_HEIGHT-30), f"Next game will start in {second} second{'s' if second > 1 else ''}...", (0, 0, 0))

                            pygame.display.update()
                            if self.state == self.QUIT:
                                break

                            pygame.time.delay(1000)
                        
                    break

                if self.state == self.UPDATE_POSITION:
                    self._update_game()
                
            # Gracefully kill this thread if the main application is closed.
            if self.state == self.QUIT:
                break

        self.screen.fill((255, 255, 255), self.board_lower)
        if self.playerA.rounds_won > self.playerB.rounds_won:
            self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2-150, self.SCREEN_HEIGHT-30),"Winner of the tournament is Player A!" , (0,0,0))
        elif self.playerA.rounds_won < self.playerB.rounds_won:
            self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2-150, self.SCREEN_HEIGHT-30),"Winner of the tournament is Player B!" , (0,0,0))
        else:
            self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2-100, self.SCREEN_HEIGHT-30),"The tournament is a draw!" , (0,0,0))
        pygame.display.update()

    def run(self, rounds: int=1, delay: int=50, training: bool=False):
        '''
        @training   : set to True only when performing GA strategies. \n
        '''

        if not training:
            self.buttonLoop.enabled = False
            self.buttonNextMove.enabled = True
            self.training = False
        else:
            self.buttonLoop.enabled = True
            self.buttonNextMove.enabled = False
            self.training = True


        game_thread = Thread(target=self._game_thread, args=(rounds, ))
        game_thread.start()

        # Only handle inputs
        while self.state != self.QUIT and self.state != self.USER_QUIT:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # self.state = self.QUIT
                    self.set_state(self.QUIT)
                    break

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.buttonLoop.enabled and self.buttonLoop.inside(pos):
                        self.buttonLoop.enabled = False
                        self.buttonNextMove.enabled = True
                    
                    elif not self.buttonLoop.enabled and self.buttonLoop.inside(pos):
                        self.buttonLoop.enabled = True
                        self.buttonNextMove.enabled = False
                    
                    elif self.buttonNextMove.enabled and self.buttonNextMove.inside(pos):
                        # self.state = self.UPDATE_POSITION
                        self.set_state(self.UPDATE_POSITION)
                
            if self.buttonLoop.enabled and self.state != self.QUIT:
                pygame.time.delay(delay)
                # self.state = self.UPDATE_POSITION
                self.set_state(self.UPDATE_POSITION)
            
            # All rounds were played
            if len(self.results) == rounds:
                game_thread.join()
                pygame.quit()
                # print("[ GameMaster ] Training finished, the application closed normally.")
                self.logger.info("Training finished, the application closed normally.", extra={"who": "GameMaster"})
                return
        
        game_thread.join()
        pygame.quit()
        # print("[ GameMaster ] The application was closed by the user.")
        self.logger.info("The application was closed by the user.", extra={"who": "GameMaster"})

if __name__ == "__main__":
    gm = GameMaster(seed=None)

    strategyA = "".join([str(random.randint(0, 1)) for _ in range(SimpleAgent.CHROMOSOME_LENGTH)])
    strategyB = "".join([str(random.randint(0, 1)) for _ in range(SimpleAgent.CHROMOSOME_LENGTH)])

    gm.playerA.set_strategy(strategyA)
    gm.playerB.set_strategy(strategyB)
    gm.run()