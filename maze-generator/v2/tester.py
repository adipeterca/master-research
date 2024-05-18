from amazed.modules.maze import Maze

# from amazed.modules.build import HuntAndKill
# from amazed.modules.build import DepthFirstSearch
from amazed.modules.build import RandomKruskal
# from amazed.modules.build import AldousBroder
# from amazed.modules.build import RandomCarving
# from amazed.modules.build import Spiral

# from amazed.modules.solver import DFSHeuristic
# from amazed.modules.solver import AStar
from amazed.modules.solver import DFS

m = Maze(10, 10)
cell_colors = {
    f"{m.rows//2}, 0" : Maze.START_COLOR,
    f"{m.rows-1}, 0" : Maze.END_COLOR
}
for i in range(m.rows):
    for j in range(m.columns):
        m.path(j, i, Maze.SOUTH)

    m.path(m.rows // 2, i, Maze.EAST)
m.export(output="tmp/maze.png", cell_colors=cell_colors, show=False)
a = DFS(m, start=(m.rows//2, 0), end=(m.rows-1, 0))
a.solve()
a.image("tmp/maze-dfs.png")
# a.gif("tmp/maze-dfs.gif")
