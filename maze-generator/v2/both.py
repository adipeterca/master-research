from amazed.modules.maze import Maze
from amazed.modules.build import DepthFirstSearch
from player import Player

import random
import pygame
import pygame.freetype

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

    class GameCell(Maze.Cell):
        def __init__(self):
            super().__init__()

            self.visibleA = False
            self.visibleB = False


    def __init__(self):

        self.maze = Maze(10, 10, self.GameCell)
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

    def run(self, human_interaction: bool = True, delay=50):
        pygame.init()

        self.FONT = pygame.freetype.SysFont("bahnschrift", 20)

        SCREEN_WIDTH = 800
        SCREEN_HEIGHT = 600
        wall_gap = 5

        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("B O T H")

        # Board settings
        board_bk = pygame.Rect((150, 50, 500+wall_gap, 500+wall_gap))
        cell_width = (board_bk.width - (self.maze.rows + 1) * wall_gap) // self.maze.rows
        cell_height = (board_bk.height - (self.maze.columns + 1) * wall_gap) // self.maze.columns
        board_cell = pygame.Rect((0, 0, cell_width, cell_height))
        board_wall_vertical = pygame.Rect((0, 0, wall_gap, cell_height))
        board_wall_horizontal = pygame.Rect((0, 0, cell_width, wall_gap))

        # Buttons
        buttonLoop = Button(pygame.Rect((board_bk.left-120, board_bk.top+50, 100, 50)), "LOOP START")
        buttonLoop.enabled = False
        buttonNextMove = Button(pygame.Rect((board_bk.left-120, board_bk.top+150, 100, 50)), "NEXT MOVE")

        # Players settings
        playerA = Player("PlayerA", body=pygame.Rect((0, 0, cell_width//2, cell_height//2)), maze=self.maze, start=(0, 0), finish=(9, 9))
        playerA.body.top = board_bk.top + playerA.pos.x*board_cell.height + (playerA.pos.x+1)*wall_gap + cell_height * 0.25
        playerA.body.left = board_bk.left + playerA.pos.y*board_cell.width + (playerA.pos.y+1)*wall_gap + cell_width * 0.25

        playerB = Player("PlayerB", body=pygame.Rect((0, 0, cell_width//2, cell_height//2)), maze=self.maze, start=(9, 9), finish=(0, 0))
        playerB.body.top = board_bk.top + playerB.pos.x*board_cell.height + (playerB.pos.x+1)*wall_gap + cell_height * 0.25
        playerB.body.left = board_bk.left + playerB.pos.y*board_cell.width + (playerB.pos.y+1)*wall_gap + cell_width * 0.25

        finishA = pygame.Rect((0, 0, cell_width // 4, cell_height // 4))
        finishA.top = board_bk.top + playerA.finish[0]*board_cell.height + (playerA.finish[0]+1)*wall_gap + cell_height * 0.4
        finishA.left = board_bk.left + playerA.finish[1]*board_cell.width + (playerA.finish[1]+1)*wall_gap + cell_height * 0.4

        finishB = pygame.Rect((0, 0, cell_width // 4, cell_height // 4))
        finishB.top = board_bk.top + playerB.finish[0]*board_cell.height + (playerB.finish[0]+1)*wall_gap + cell_height * 0.4
        finishB.left = board_bk.left + playerB.finish[1]*board_cell.width + (playerB.finish[1]+1)*wall_gap + cell_height * 0.4

        state = self.RUNNING
        iteration = 0
        while state != self.QUIT:
            # ------------------------------------------------------------------------------------
            # Draw the board
            if True:
                screen.fill((255, 255, 255))
                screen.fill((0, 0, 0), board_bk)

                for i in range(self.maze.rows):
                    board_cell.top = board_bk.top + i*board_cell.height + (i+1)*wall_gap
                    for j in range(self.maze.columns):
                        board_cell.left = board_bk.left + j*board_cell.width + (j+1)*wall_gap

                        wall_color = None
                        if self.maze.data[i][j].visibleA and self.maze.data[i][j].visibleB:
                            pygame.draw.rect(screen, self.VIEW_ALL, board_cell)
                            wall_color = self.VIEW_ALL
                        elif self.maze.data[i][j].visibleA:
                            pygame.draw.rect(screen, self.VIEW_A, board_cell)
                            wall_color = self.VIEW_A
                        elif self.maze.data[i][j].visibleB:
                            pygame.draw.rect(screen, self.VIEW_B, board_cell)
                            wall_color = self.VIEW_B
                        else:
                            pygame.draw.rect(screen, self.VIEW_HIDDEN, board_cell)
                            wall_color = self.VIEW_HIDDEN


                        # Clear the wall if not present
                        if not self.maze.data[i][j].walls[Maze.EAST]:
                            board_wall_vertical.top = board_cell.top
                            board_wall_vertical.left = board_cell.right
                            pygame.draw.rect(screen, wall_color, board_wall_vertical)
                        if not self.maze.data[i][j].walls[Maze.SOUTH]:
                            board_wall_horizontal.top = board_cell.bottom
                            board_wall_horizontal.left = board_cell.left
                            pygame.draw.rect(screen, wall_color, board_wall_horizontal)


                pygame.draw.rect(screen, self.FINISH_A, finishA)
                pygame.draw.rect(screen, self.FINISH_B, finishB)

                if playerA.moved:
                    playerA.body.top = board_bk.top + playerA.pos.x*board_cell.height + (playerA.pos.x+1)*wall_gap + cell_height * 0.25
                    playerA.body.left = board_bk.left + playerA.pos.y*board_cell.width + (playerA.pos.y+1)*wall_gap + cell_width * 0.25
                    playerA.moved = False
                pygame.draw.rect(screen, self.PLAYER_A, playerA.body)

                if playerB.moved:
                    playerB.body.top = board_bk.top + playerB.pos.x*board_cell.height + (playerB.pos.x+1)*wall_gap + cell_height * 0.25
                    playerB.body.left = board_bk.left + playerB.pos.y*board_cell.width + (playerB.pos.y+1)*wall_gap + cell_width * 0.25
                    playerB.moved = False
                pygame.draw.rect(screen, self.PLAYER_B, playerB.body)

                if buttonLoop.enabled:
                    pygame.draw.rect(screen, buttonLoop.colorEnabled, buttonLoop.body)
                    self.FONT.render_to(screen, (buttonLoop.body.x+20, buttonLoop.body.y+30), "STOP", buttonLoop.text_color)
                else:
                    pygame.draw.rect(screen, buttonLoop.colorDisabled, buttonLoop.body)
                    self.FONT.render_to(screen, (buttonLoop.body.x+20, buttonLoop.body.y+30), "START", buttonLoop.text_color)
                self.FONT.render_to(screen, (buttonLoop.body.x+25, buttonLoop.body.y+7), "LOOP", buttonLoop.text_color)


                if buttonNextMove.enabled:
                    pygame.draw.rect(screen, buttonNextMove.colorEnabled, buttonNextMove.body)
                else:
                    pygame.draw.rect(screen, buttonNextMove.colorDisabled, buttonNextMove.body)
                self.FONT.render_to(screen, (buttonNextMove.body.x+23, buttonNextMove.body.y+7), "NEXT", buttonNextMove.text_color)
                self.FONT.render_to(screen, (buttonNextMove.body.x+20, buttonNextMove.body.y+30), "MOVE", buttonNextMove.text_color)

                self.FONT.render_to(screen, (SCREEN_WIDTH//2-200, 20), f"SCORE: {playerA.score}", self.PLAYER_A)
                self.FONT.render_to(screen, (SCREEN_WIDTH//2-50, 20), f"ITERATION: {iteration}", (0, 0, 0))
                self.FONT.render_to(screen, (SCREEN_WIDTH//2+130, 20), f"SCORE: {playerB.score}", self.PLAYER_B)

                pygame.display.update()
            
            # ------------------------------------------------------------------------------------
            # Handle game logic

            # Only update the position if it was actually modified
            if state == self.UPDATE_POSITION:
                if not human_interaction:

                    # Handle the negociation
                    if playerA.wants_negotiation() and playerB.wants_negotiation():
                        for i in range(3):
                            print(f"[ Negociation ] Attempt number {i}:")

                            print(f"[ Negociation ] A proposal is: \n\tOFFER {playerA.offer}\n\tREQUEST {playerA.request}")
                            print(f"[ Negociation ] B proposal is: \n\tOFFER {playerB.offer}\n\tREQUEST {playerB.request}")

                            if playerA.proposal(playerB.offer, playerB.request, i) and playerB.proposal(playerA.offer, playerA.request, i):
                                print(f"[ Negociation ] Succes!")

                                self.maze.data[playerA.offer[0]][playerA.offer[1]].visibleB = True
                                self.maze.data[playerB.offer[0]][playerB.offer[1]].visibleA = True

                                break
                            else:
                                print(f"[ Negociation ] Failure!")

                    print("[ Negociation ] The negociation period ended.")

                    # Handle the movement
                    playerA.best_move()
                    playerB.best_move()


                self.maze.data[playerA.pos.x][playerA.pos.y].visibleA = True
                self.maze.data[playerB.pos.x][playerB.pos.y].visibleB = True

                state = self.RUNNING
                iteration += 1

                if playerA.win() and playerB.win():
                    state = self.DRAW
                    print("[ Debug ] Draw.")
                elif playerA.win():
                    state = self.WIN_A
                    print("[ Debug ] A won.")
                elif playerB.win():
                    state = self.WIN_B
                    print("[ Debug ] B won.")

            # ------------------------------------------------------------------------------------
            # Handle events

            if state == self.RUNNING:
                if human_interaction:
                    print("[ Human Interaction ] Accepting user input.")
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_UP and self.maze.is_valid_move(playerA.pos.x, playerA.pos.y, Maze.NORTH):
                                playerA.move(Maze.NORTH)
                                state = self.UPDATE_POSITION
                            elif event.key == pygame.K_RIGHT and self.maze.is_valid_move(playerA.pos.x, playerA.pos.y, Maze.EAST):
                                playerA.move(Maze.EAST)
                                state = self.UPDATE_POSITION
                            elif event.key == pygame.K_DOWN and self.maze.is_valid_move(playerA.pos.x, playerA.pos.y, Maze.SOUTH):
                                playerA.move(Maze.SOUTH)
                                state = self.UPDATE_POSITION
                            elif event.key == pygame.K_LEFT and self.maze.is_valid_move(playerA.pos.x, playerA.pos.y, Maze.WEST):
                                playerA.move(Maze.WEST)
                                state = self.UPDATE_POSITION

                            if event.key == pygame.K_w and self.maze.is_valid_move(playerB.pos.x, playerB.pos.y, Maze.NORTH):
                                playerB.move(Maze.NORTH)
                                state = self.UPDATE_POSITION
                            elif event.key == pygame.K_d and self.maze.is_valid_move(playerB.pos.x, playerB.pos.y, Maze.EAST):
                                playerB.move(Maze.EAST)
                                state = self.UPDATE_POSITION
                            elif event.key == pygame.K_s and self.maze.is_valid_move(playerB.pos.x, playerB.pos.y, Maze.SOUTH):
                                playerB.move(Maze.SOUTH)
                                state = self.UPDATE_POSITION
                            elif event.key == pygame.K_a and self.maze.is_valid_move(playerB.pos.x, playerB.pos.y, Maze.WEST):
                                playerB.move(Maze.WEST)
                                state = self.UPDATE_POSITION

                        if event.type == pygame.QUIT:
                            state = self.QUIT

                else:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            state = self.QUIT
                            break

                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pos = pygame.mouse.get_pos()
                            if buttonLoop.inside(pos):
                                buttonLoop.enabled = not buttonLoop.enabled
                                buttonNextMove.enabled = not buttonLoop.enabled

                                print(f"[ Debug ] Switched loop to {buttonLoop.enabled}")
                            if buttonNextMove.inside(pos) and buttonNextMove.enabled:
                                state = self.UPDATE_POSITION
                        
                    if buttonLoop.enabled and state != self.QUIT:
                        pygame.time.delay(delay)
                        state = self.UPDATE_POSITION

            if state in (self.WIN_A, self.WIN_B, self.DRAW):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        state = self.QUIT
        pygame.quit()
        print("[ Debug ] The application was closed by the user.")

gm = GameMaster()
DepthFirstSearch(gm.maze, seed=0, gif=False)

gm.run(human_interaction=False)

# Ideas: