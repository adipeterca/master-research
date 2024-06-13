import numpy as np
from PIL import Image
from amazed.modules.maze import Maze
from amazed.modules.build import DepthFirstSearch

def maze_bitmap(bitmap_path:str, x:int, y:int) -> Maze:

    img = Image.open(bitmap_path)
    a = list(img.getdata())
    a = np.reshape(a, (img.height, img.width))

    maze = Maze(img.height, img.width)
    for i in range(maze.rows):
        for j in range(maze.columns):
            if a[i][j] == 0:
                maze.data[i][j].active = False
    DepthFirstSearch(maze, gif=False, x=x, y=y)
    return maze