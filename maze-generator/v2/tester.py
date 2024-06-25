from colab import GameMaster
from strategies import Human
from player import Player
from strategies import CopyPlayer
from strategies import SimpleAgent
from strategies import RememberMe

# print(SimpleAgent.str_strategy("10101101110000100111111101011000111101010011000001101000"))
# exit()


# s = [
#     [_ for _ in "111111000111000000110000110111001111111101111010"],
#     # [_ for _ in "100010000111011110110100011111010101100101011001"],
#     # [_ for _ in "101111001110111010011010011111110100010111000100"],
#     # [_ for _ in "100011111111101100110010010110101110011111011110"],
#     # [_ for _ in "000101111101001101111110010100000100001000110000"],
#     # [_ for _ in "110001010000000010111011010110000100010000011001"],
#     # [_ for _ in "000001100111011101011111010110010100011000101011"],
#     # [_ for _ in "010001010000001111110100001111000011100010111111"],
#     # [_ for _ in "110001010111000011111000010100101111101100110000"],
#     # [_ for _ in "110001110101000010101001111110101001011000101011"],
#     # [_ for _ in "110101010111000001101001000100101111111111101010"],
#     # [_ for _ in "110110011011011100101010100011011100110000010001"],
# ]
# for i in range(len(s)):
#     game = GameMaster(seed=None)
#     # game.playerA.set_strategy([_ for _ in "01100111101111010000000000001011001001111111111100000110"])
#     # game.playerB.set_strategy([_ for _ in "10010101000100001010010011000111010010010011101011100000"])
#     # game.playerB.set_strategy(s[i])
#     game.playerA.set_strategy(strategy=None)
#     game.playerB.set_strategy(strategy=None)
#     # game.playerA = RememberMe("PlayerA", game.maze, start=game.playerA.start, finish=game.playerA.finish)
#     # game.playerB = RememberMe("PlayerB", game.maze, start=game.playerB.start, finish=game.playerB.finish)

#     game.run(rounds=10, training=True)
#     print(f"\nNegotiation procent: {game.total_negotiations_attempts / game.total_possible_negotiations * 100:.2f} %")
#     print(f"Out of which only {game.successful_negotiations / game.total_negotiations_attempts * 100:.2f} % were successful.\n")
#     print(f"Final score for A: {game.playerA.rounds_won}")
#     print(f"Final score for B: {game.playerB.rounds_won}")
#     print(f"GA score for A: {game.playerA.individual_score}")
#     print(f"GA score for B: {game.playerB.individual_score}")

from amazed.modules.maze import Maze
from amazed.modules.build import DepthFirstSearch
from amazed.modules.build import RecursiveDivision
from amazed.modules.build import RandomPrim

maze = Maze(7, 10)
RandomPrim(maze)
maze.export(output="tmp/dfs.png", show=False)

# import random

# X = random.randint(0, 100000)
# average = [0] * 5
# stats = [0, 25, 50, 75, 100]
# MAZES = 100
# for k in range(5):
#     for i in range(MAZES):
#         gm = GameMaster(seed=i+X)
#         gm.max_allowed_iterations = 2000

#         if i == 0:
#             print(f"Start for A: {gm.playerA.start} -> {gm.playerA.finish}")

#         gm.playerA.set_strategy([_ for _ in "01100111101111010000000000001011001001111111111100000110"])
#         gm.playerB.set_strategy([_ for _ in "10010101000100001010010011000111010010010011101011100000"])

#         gm.playerA.TESTING_CHANCE = stats[k] / 100

#         gm.run(training=True)

#         print(gm.iteration, end=", ", flush=True)
#         average[k] += gm.iteration
#     average[k] /= MAZES
#     print(f"Final : {average[k]:.2f}")
