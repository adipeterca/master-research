from amazed.modules.maze import Maze
from amazed.modules.build import DepthFirstSearch
from amazed.modules.build import Sculptor
from player import Player
from strategies import CopyPlayer

import random
import pygame
import pygame.freetype

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
    VIEW_ALL = (200, 200, 200)
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

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    class GameCell(Maze.Cell):
        def __init__(self):
            super().__init__()

            self.visibleA = False
            self.visibleB = False


    def __init__(self, maze_algorithm_class: Sculptor = DepthFirstSearch, seed = 0):
        self._maze_algorithm_class = maze_algorithm_class
        self._seed = seed

        self._create_maze()

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
        # self.playerA = Player("PlayerA", body=pygame.Rect((0, 0, self.cell_width//2, self.cell_height//2)), maze=self.maze)
        self.playerA = CopyPlayer("PlayerA", body=pygame.Rect((0, 0, self.cell_width//2, self.cell_height//2)), maze=self.maze)
        while self.playerA.start == self.playerA.finish:
            self.playerA.finish = (random.randint(0, self.maze.rows-1), random.randint(0, self.maze.columns-1))
        
        # self.playerB = Player("PlayerB", body=pygame.Rect((0, 0, self.cell_width//2, self.cell_height//2)), maze=self.maze)
        self.playerB = CopyPlayer("PlayerB", body=pygame.Rect((0, 0, self.cell_width//2, self.cell_height//2)), maze=self.maze)
        while self.playerB.start == self.playerB.finish:
            self.playerB.finish = (random.randint(0, self.maze.rows-1), random.randint(0, self.maze.columns-1))
        
        self.finishA = pygame.Rect((0, 0, self.cell_width // 4, self.cell_height // 4))
        self.finishB = pygame.Rect((0, 0, self.cell_width // 4, self.cell_height // 4))

        self.state = self.NONE

    def _create_maze(self):
        self.maze = Maze(10, 10, self.GameCell)
        self._maze_algorithm_class(self.maze, seed=self._seed, gif=False)
        # DepthFirstSearch(self.maze, gif=False)

        playerA_count = 0
        playerB_count = 0

        # Randomly distribute each player a set of cells
        self.cell_colors_a = {}
        self.cell_colors_b = {}
        for i in range(self.maze.rows):
            for j in range(self.maze.columns):
                if random.random() > 0.5:
                    if playerA_count < self.maze.rows * self.maze.columns / 2:
                        self.maze.data[i][j].visibleA = True
                        self.maze.data[i][j].visibleB = False
                        playerA_count += 1
                        self.cell_colors_a[f"{i}, {j}"] = self.VIEW_A
                        self.cell_colors_b[f"{i}, {j}"] = self.UNKNOWN
                    else:
                        self.maze.data[i][j].visibleA = False
                        self.maze.data[i][j].visibleB = True
                        playerB_count += 1
                        self.cell_colors_b[f"{i}, {j}"] = self.VIEW_B
                        self.cell_colors_a[f"{i}, {j}"] = self.UNKNOWN
                else:
                    if playerB_count < self.maze.rows * self.maze.columns / 2:
                        self.maze.data[i][j].visibleA = False
                        self.maze.data[i][j].visibleB = True
                        playerB_count += 1
                        self.cell_colors_b[f"{i}, {j}"] = self.VIEW_B
                        self.cell_colors_a[f"{i}, {j}"] = self.UNKNOWN
                    else:
                        self.maze.data[i][j].visibleA = True
                        self.maze.data[i][j].visibleB = False
                        playerA_count += 1
                        self.cell_colors_a[f"{i}, {j}"] = self.VIEW_A
                        self.cell_colors_b[f"{i}, {j}"] = self.UNKNOWN
                if self.maze.data[i][j].visibleA and self.maze.data[i][j].visibleB:
                    print(f"Marked cell {i}, {j} as visible to both.")


    def view_a(self):
        self.maze.export(output="tmp/playerA.png", show=False, cell_colors=self.cell_colors_a)

    def view_b(self):
        self.maze.export(output="tmp/playerB.png", show=False, cell_colors=self.cell_colors_b)

    def view_all(self):
        all_cell_colors = self.cell_colors_a
        for key in self.cell_colors_b.keys():
            if all_cell_colors[key] == self.UNKNOWN:
                all_cell_colors[key] = self.VIEW_B

        all_cell_colors["0, 0"] = self.PLAYER_A
        all_cell_colors["9, 9"] = self.PLAYER_B

        self.maze.export(output="tmp/all.png", show=False, cell_colors=all_cell_colors)

    def _draw_screen(self):
        '''
        
        '''
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

        self.playerA.body.top = self.board_bk.top + self.playerA.pos.x*self.board_cell.height + (self.playerA.pos.x+1)*self.wall_gap + self.cell_height * 0.25
        self.playerA.body.left = self.board_bk.left + self.playerA.pos.y*self.board_cell.width + (self.playerA.pos.y+1)*self.wall_gap + self.cell_width * 0.25
        pygame.draw.rect(self.screen, self.PLAYER_A, self.playerA.body)

        self.playerB.body.top = self.board_bk.top + self.playerB.pos.x*self.board_cell.height + (self.playerB.pos.x+1)*self.wall_gap + self.cell_height * 0.25
        self.playerB.body.left = self.board_bk.left + self.playerB.pos.y*self.board_cell.width + (self.playerB.pos.y+1)*self.wall_gap + self.cell_width * 0.25
        pygame.draw.rect(self.screen, self.PLAYER_B, self.playerB.body)

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

        self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2-200, 20), f"SCORE: {self.playerA.score}", self.PLAYER_A)
        self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2-50, 20), f"ITERATION: {self.iteration}", (0, 0, 0))
        self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2+130, 20), f"SCORE: {self.playerB.score}", self.PLAYER_B)

        pygame.display.update()

    def _update_game(self):
        '''
        
        '''
        if self.playerA.wants_negotiation() and self.playerB.wants_negotiation():
            for i in range(3):
                print(f"[ Negotiation ] Attempt number {i}:")
                self.playerA.create_offer()
                self.playerA.create_request()

                self.playerB.create_offer()
                self.playerB.create_request()

                print(f"[ Negotiation ] A proposal is: \n\tOFFER {self.playerA.offer}\n\tREQUEST {self.playerA.request}")
                print(f"[ Negotiation ] B proposal is: \n\tOFFER {self.playerB.offer}\n\tREQUEST {self.playerB.request}")

                if self.playerA.proposal(self.playerB.offer, self.playerB.request, i) and self.playerB.proposal(self.playerA.offer, self.playerA.request, i):
                    print(f"[ Negotiation ] Succes!")

                    self.maze.data[self.playerA.offer[0]][self.playerA.offer[1]].visibleB = True
                    self.maze.data[self.playerB.offer[0]][self.playerB.offer[1]].visibleA = True

                    break
                else:
                    print(f"[ Negotiation ] Attempt {i} failed!")

        print("[ Negotiation ] The negotiation period ended.")

        self.playerA.best_move()
        self.playerB.best_move()

        self.maze.data[self.playerA.pos.x][self.playerA.pos.y].visibleA = True
        self.maze.data[self.playerB.pos.x][self.playerB.pos.y].visibleB = True

        if self.playerA.win() and self.playerB.win():
            self.state = self.DRAW
            self.playerA.score += 1
            self.playerB.score += 1
            print("[ Debug ] Draw.")

        elif self.playerA.win():
            self.state = self.WIN_A
            self.playerA.score += 1
            print("[ Debug ] A won.")

        elif self.playerB.win():
            self.state = self.WIN_B
            self.playerB.score += 1
            print("[ Debug ] B won.")
        
        elif self.state == self.QUIT: 
            return
        
        else:
            self.state = self.RUNNING
        
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
        

    def _game_thread(self, rounds: int = 1):
        '''
        Any loops that you create inside the "while" main loop must have a check for self.state!
        '''

        for round in range(1, rounds+1):
            
            self.state = self.RUNNING
            self.iteration = 0

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

                    # If it is not the last round
                    if round != rounds:
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
            
            # Reset players & maze for a new game iteration.
            self._create_maze()

            self.playerA.start = (random.randint(0, self.maze.rows-1), random.randint(0, self.maze.columns-1))
            self.playerA.reset_position()
            self.playerA.maze = self.maze
            
            self.playerB.start = (random.randint(0, self.maze.rows-1), random.randint(0, self.maze.columns-1))
            self.playerB.reset_position()
            self.playerB.maze = self.maze

            self.playerA.finish = (random.randint(0, self.maze.rows-1), random.randint(0, self.maze.columns-1))
            self.playerB.finish = (random.randint(0, self.maze.rows-1), random.randint(0, self.maze.columns-1))

        self.screen.fill((255, 255, 255), self.board_lower)
        if self.playerA.score > self.playerB.score:
            self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2-150, self.SCREEN_HEIGHT-30),"Winner of the tournament is Player A!" , (0,0,0))
        elif self.playerA.score < self.playerB.score:
            self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2-150, self.SCREEN_HEIGHT-30),"Winner of the tournament is Player B!" , (0,0,0))
        else:
            self.FONT.render_to(self.screen, (self.SCREEN_WIDTH//2-100, self.SCREEN_HEIGHT-30),"The tournament is a draw!" , (0,0,0))
        pygame.display.update()

    def _run(self, rounds: int=1, delay: int=50):

        self.buttonLoop.enabled = False
        self.buttonNextMove.enabled = True

        game_thread = Thread(target=self._game_thread, args=(rounds, ))
        game_thread.start()

        # Only handle inputs
        while self.state != self.QUIT:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = self.QUIT
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
                        self.state = self.UPDATE_POSITION
                
            if self.buttonLoop.enabled and self.state != self.QUIT:
                pygame.time.delay(delay)
                self.state = self.UPDATE_POSITION
        
        game_thread.join()
        pygame.quit()
        print("[ Debug ] The application was closed by the user.")

    def run(self, rounds:int=1):
        '''
        @rounds : how many game rounds to play
        '''
        
        self.buttonLoop.enabled = False

        for round in range(1, rounds+1):

            self.state = self.RUNNING
            self.iteration = 0
            while self.state != self.QUIT:

                self._draw_screen()

                # Only update the position if it was actually modified
                if self.state == self.UPDATE_POSITION:
                    
                    self._update_game()

                    if self.playerA.win() and self.playerB.win():
                        self.state = self.DRAW
                        self.playerA.score += 1
                        self.playerB.score += 1
                        print("[ Debug ] Draw.")

                    elif self.playerA.win():
                        self.state = self.WIN_A
                        self.playerA.score += 1
                        print("[ Debug ] A won.")

                    elif self.playerB.win():
                        self.state = self.WIN_B
                        self.playerB.score += 1
                        print("[ Debug ] B won.")

                    
                    self.state = self.RUNNING
                    self.iteration += 1

                if self.state == self.RUNNING:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.state = self.QUIT
                            break

                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pos = pygame.mouse.get_pos()
                            if self.buttonLoop.enabled and self.buttonLoop.inside(pos):
                                self.buttonLoop.enabled = not self.buttonLoop.enabled
                                self.buttonNextMove.enabled = not self.buttonLoop.enabled

                            if self.buttonNextMove.enabled and self.buttonNextMove.inside(pos):
                                self.state = self.UPDATE_POSITION
                        
                    if self.buttonLoop.enabled and self.state != self.QUIT:
                        pygame.time.delay(50)
                        self.state = self.UPDATE_POSITION

                # self.state=self.WIN_A
                if self.state in (self.WIN_A, self.WIN_B, self.DRAW):
                    self._draw_results(self.state)

                    # If it is not the last round
                    if round != rounds:
                        self._draw_countdown()
                    while self.state != self.QUIT:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                self.state = self.QUIT
            
            if self.state == self.QUIT:
                break
        pygame.quit()
        print("[ Debug ] The application was closed by the user.")

if __name__ == "__main__":

    gm = GameMaster(seed=None)

    gm._run(rounds=1)
    # gm.run(rounds=2)

'''
Ideas:
* implement a client-server approach for human interaction

Todo:
* [x] clean-up the mess with energy
* [x] implement score only when winning
* [x] implement a method of tournaments (with or without graphical interface - first with GUI, then without)
* finish implementing all strategies (offer and request made to follow the same idea, so no mixing requiered)
* read about Genetic Algorithms for Iterated Prisoner's Dilemma
* implement a Genetic Algorithm to create strategies for this game
'''