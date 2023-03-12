'''
Starting from a random generated maze (the spawn rate of walls can be adjusted), the algorithm applies the Lee technique
to generate a path to the closest edge. Two variations were tested, one in which the order of neighborhood testing is
set to NORTH-EAST-SOUTH-WEST and one in which the direction is randomly selected.
The path taken by the algorithm can be observed in the generated 'test.png' picture.
'''

from PIL import Image
import numpy as np
import random

WALL = 0
EMPTY = 255
WALKED = 127
PAST_WALK = 110

solved = False
def lee(grid, x, y):
    global solved
    # If the grid is already solved, just return
    if solved:
        return
    
    # The current position is on the margin
    if x == 0 or y == 0 or x == grid.shape[0]-1 or y == grid.shape[0]-1:
        solved = True
        return
    
    step = 2

    def search_north():
        # Search NORTH
        if grid[x-1][y] == EMPTY:
            grid[x-1][y] = grid[x][y] - step
            lee(grid, x-1, y)
            if solved:
                return
            else:
                grid[x-1][y] = PAST_WALK

    def search_east():
        # Search EAST
        if grid[x][y+1] == EMPTY:
            grid[x][y+1] = grid[x][y] - step
            lee(grid, x, y+1)
            if solved:
                return
            else:
                grid[x][y+1] = PAST_WALK

    def search_south():
        # Search SOUTH
        if grid[x+1][y] == EMPTY:
            grid[x+1][y] = grid[x][y] - step
            lee(grid, x+1, y)
            if solved:
                return
            else:
                grid[x+1][y] = PAST_WALK
    
    def search_west():
        # Search WEST
        if grid[x][y-1] == EMPTY:
            grid[x][y-1] = grid[x][y] - step
            lee(grid, x, y-1)
            if solved:
                return
            else:
                grid[x][y-1] = PAST_WALK
            
    possible_searches = [search_north, search_east, search_south, search_west]
    random.shuffle(possible_searches)
    for i in possible_searches:
        i()
        if solved:
            break


if __name__ == '__main__':
    size = 28
    grid = np.ones(size * size) * 255

    # Fill the matrix with random black spots
    wall_rate = 0.2
    for i in range(len(grid)):
        if np.random.random() < wall_rate:
            grid[i] = WALL
    grid = grid.reshape((size, size))

    start_x = size // 2
    start_y = size // 2
    while grid[start_x][start_y] == WALL:
        start_x = np.random.randint(1, size)
        start_y = np.random.randint(1, size)
    
    grid[start_x][start_y] = 200
    lee(grid, start_x, start_y)

    # Display the original maze
    img = Image.new('L', (size, size))
    img.putdata(grid.flatten())
    img.save('test.png')