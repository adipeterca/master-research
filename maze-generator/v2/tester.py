# from both import GameMaster
# from strategies import Human

# s = [
#     [_ for _ in "111111000111000000110000110111001111111101111010"],
#     [_ for _ in "100010000111011110110100011111010101100101011001"],
#     [_ for _ in "101111001110111010011010011111110100010111000100"],
#     [_ for _ in "100011111111101100110010010110101110011111011110"],
#     [_ for _ in "000101111101001101111110010100000100001000110000"],
#     [_ for _ in "110001010000000010111011010110000100010000011001"],
#     [_ for _ in "000001100111011101011111010110010100011000101011"],
#     [_ for _ in "010001010000001111110100001111000011100010111111"],
#     [_ for _ in "110001010111000011111000010100101111101100110000"],
#     [_ for _ in "110001110101000010101001111110101001011000101011"],
#     [_ for _ in "110101010111000001101001000100101111111111101010"],
#     [_ for _ in "110110011011011100101010100011011100110000010001"],
# ]
# for i in range(len(s)):
#     game = GameMaster(seed=None)
#     game.playerA.set_strategy([_ for _ in "000001000101001101111110011101101111110010011001"])
#     game.playerB.set_strategy(s[i])
#     # game.playerA.set_strategy(strategy=None)
#     # game.playerB.set_strategy(strategy=None)

#     game.run(rounds=100, training=True)
#     print(f"Final score for A: {game.playerA.score}")
#     print(f"Final score for B: {game.playerB.score}")

from amazed.modules.maze import Maze
from amazed.modules.build import RecursiveDivision
from amazed.modules.build import WallsCellularAutomata

maze = Maze(20, 20)
RecursiveDivision(maze, gif=False)
WallsCellularAutomata(maze, generations=100).export(speed=300)
# maze.export()