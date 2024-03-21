from amazed.modules.maze import Maze

# from amazed.modules.build import HuntAndKill
# from amazed.modules.build import DepthFirstSearch
from amazed.modules.build import RandomKruskal
# from amazed.modules.build import AldousBroder
# from amazed.modules.build import RandomCarving
# from amazed.modules.build import Spiral

# from amazed.modules.solver import DFSHeuristic
# from amazed.modules.solver import AStar
# from amazed.modules.solver import DFS


import timeit

# m = Maze(20, 20)

# import numpy as np
# start = timeit.default_timer()

# DepthFirstSearch(m, seed=0, biased_dirs=[Maze.NORTH, Maze.SOUTH], biased_level=10).export(path)

# end = timeit.default_timer()
# print(f"done {end-start}")

# m.export(output="tmp/maze.png", show=False)


pp = timeit.default_timer()
m = Maze(200, 200)
print(timeit.default_timer() - pp)
