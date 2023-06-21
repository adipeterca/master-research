import random
from sys import setrecursionlimit
from modules.maze import Maze
import os

# fig = 0
def depth_first_search_r(maze : Maze, current_x = 0, current_y = 0, visited = None):
    '''
    Steps:
    1) start with a random point. this becomes the current cell
    2) choose a random wall from the current cell to another cell
        2.1) break the wall if the new cell has not been visited yet
        2.2) mark the new cell as the current cell and return to 2)
    3) if there are no more unvisited adjacent cells, backtrack to the previous cell
    4) the algorithm finishes when:
        * there are no more visited cells
        * (more precisely) the starting point because the current cell (again)
    '''
    if visited is None:
        visited = set()
    
    visited.add((current_x, current_y))
    # global fig

    # Are there any unvisited cells?
    possible_directions = []
    if (current_x-1, current_y) not in visited and maze.is_valid_position(current_x-1, current_y):
        possible_directions.append(Maze.NORTH)
    if (current_x, current_y+1) not in visited and maze.is_valid_position(current_x, current_y+1):
        possible_directions.append(Maze.EAST)
    if (current_x+1, current_y) not in visited and maze.is_valid_position(current_x+1, current_y):
        possible_directions.append(Maze.SOUTH)
    if (current_x, current_y-1) not in visited and maze.is_valid_position(current_x, current_y-1):
        possible_directions.append(Maze.WEST)

    if len(possible_directions) == 0:
        # maze.export(4, output=f'temp_photos/{fig}.png', show=False, current_cell=(current_x, current_y), visited_cells=visited)
        # fig += 1
        return
    
    random.shuffle(possible_directions)

    for dir in possible_directions:
        # maze.export(4, output=f'temp_photos/{fig}.png', show=False, current_cell=(current_x, current_y), visited_cells=visited)
        # fig += 1
        if dir == Maze.NORTH and (current_x-1, current_y) not in visited:
            maze.path(current_x, current_y, dir)
            depth_first_search_r(maze, current_x-1, current_y, visited)

        if dir == Maze.EAST and (current_x, current_y+1) not in visited:
            maze.path(current_x, current_y, dir)
            depth_first_search_r(maze, current_x, current_y+1, visited)

        if dir == Maze.SOUTH and (current_x+1, current_y) not in visited:
            maze.path(current_x, current_y, dir)
            depth_first_search_r(maze, current_x+1, current_y, visited)

        if dir == Maze.WEST and (current_x, current_y-1) not in visited:
            maze.path(current_x, current_y, dir)
            depth_first_search_r(maze, current_x, current_y-1, visited)


def hunt_and_kill(maze : Maze, x = 0, y = 0):
    '''
    1. Set start location
    2. while there are unvisited cells:
        2.1. perform a random walk until there are no unvisited neighbors (you get stuck)
        2.2. search the grid starting from (0, 0) until you found a unvisited cell. Carve a random passage to a visited neighbor cell, then go to 2.1
    '''

    visited = set()
    # fig = 0
    while len(visited) < maze.rows * maze.columns:
        # maze.export(4, output=f'temp_photos/{fig}.png', show=False, current_cell=(x, y), visited_cells=visited)
        # fig += 1
        visited.add((x, y))

        possible_directions = []
        if (x-1, y) not in visited and maze.is_valid_position(x-1, y):
            possible_directions.append(Maze.NORTH)
        if (x, y+1) not in visited and maze.is_valid_position(x, y+1):
            possible_directions.append(Maze.EAST)
        if (x+1, y) not in visited and maze.is_valid_position(x+1, y):
            possible_directions.append(Maze.SOUTH)
        if (x, y-1) not in visited and maze.is_valid_position(x, y-1):
            possible_directions.append(Maze.WEST)
        
        # Perform grid search in order to update x, y
        if len(possible_directions) == 0:

            found_unvisited = False
            for i in range(maze.rows):
                for j in range(maze.columns):
                    # Make a wall in a random (valid) direction (of an already visited cell) from the first unvisited cell found
                    if (i, j) not in visited:
                        possible_directions = []
                        if (i-1, j) in visited and maze.is_valid_position(i-1, j):
                            possible_directions.append(Maze.NORTH)
                        if (i, j+1) in visited and maze.is_valid_position(i, j+1):
                            possible_directions.append(Maze.EAST)
                        if (i+1, j) in visited and maze.is_valid_position(i+1, j):
                            possible_directions.append(Maze.SOUTH)
                        if (i, j-1) in visited and maze.is_valid_position(i, j-1):
                            possible_directions.append(Maze.WEST)
                        
                        random.shuffle(possible_directions)

                        # Update the current position
                        x = i
                        y = j

                        maze.path(x, y, possible_directions[0])
                        # maze.export(4, output=f'temp_photos/{fig}.png', show=False, current_cell=(x, y), visited_cells=visited)
                        # fig += 1
                        found_unvisited = True
                        break
                if found_unvisited:
                    break
            
        else:
            random.shuffle(possible_directions)
            maze.path(x, y, possible_directions[0])

            # Update current position
            if possible_directions[0] == Maze.NORTH:
                x = x - 1
            elif possible_directions[0] == Maze.EAST:
                y = y + 1
            elif possible_directions[0] == Maze.SOUTH:
                x = x + 1
            else:
                y = y - 1


def binary_tree(maze : Maze):
    '''
    For every cell, randomly carve a passage either North or West.
    '''

    # fig = 0
    visited = set()
    for i in range(maze.rows):
        for j in range(maze.columns):
            # maze.export(4, output=f'temp_photos/{fig}.png', show=False, current_cell=(i, j), visited_cells=visited)
            # fig += 1
            visited.add((i, j))

            # Carve North
            if random.random() < 0.5:
                if maze.is_valid_position(i-1, j):
                    maze.path(i, j, Maze.NORTH)
                # If the cell does not have a path to North,
                # instead carve a path to West
                elif maze.is_valid_position(i, j-1):
                    maze.path(i, j, Maze.WEST)
            else:
                if maze.is_valid_position(i, j-1):
                    maze.path(i, j, Maze.WEST)
                # If the cell does not have a path to West,
                # instead carve a path to North
                elif maze.is_valid_position(i-1, j):
                    maze.path(i, j, Maze.NORTH)


def random_kruskal(maze : Maze):
    list_of_cells = []
    for i in range(maze.rows):
        for j in range(maze.columns):
            list_of_cells.append([[i, j]])
    
    list_of_edges = []
    for i in range(maze.rows):
        for j in range(maze.columns):
            if maze.is_valid_position(i-1, j):
                list_of_edges.append((i, j, i-1, j))
            if maze.is_valid_position(i+1, j):
                list_of_edges.append((i, j, i+1, j))
            if maze.is_valid_position(i, j-1):
                list_of_edges.append((i, j, i, j-1))
            if maze.is_valid_position(i, j+1):
                list_of_edges.append((i, j, i, j+1))
    
    random.shuffle(list_of_edges)
    # fig = 0
    for edge in list_of_edges:
        x1, y1, x2, y2 = edge

        # Find cell_set for (x1, y1)
        cell_set_1 = list_of_cells[0]
        for cell_set in list_of_cells:
            if [x1, y1] in cell_set:
                cell_set_1 = cell_set
                break
        # Find cell_set for (x2, y2)
        cell_set_2 = list_of_cells[0]
        for cell_set in list_of_cells:
            if [x2, y2] in cell_set:
                cell_set_2 = cell_set
                break
        
        
        if cell_set_1 != cell_set_2:
            new_cell_list = cell_set_1 + cell_set_2
            new_cell_list = new_cell_list.copy()
            list_of_cells.append(new_cell_list)
            list_of_cells.remove(cell_set_1)
            list_of_cells.remove(cell_set_2)

            maze.path_to_cell(x1, y1, x2, y2)
            # maze.export(4, output=f'temp_photos/{fig}.png', show=False, current_cell=(x1, y1))
            # fig += 1

def aldous_broder(maze : Maze):
    visited = set()

    # Random start position
    x = random.randint(0, maze.rows-1)
    y = random.randint(0, maze.columns-1)

    visited.add((x, y))

    fig = 0
    while len(visited) < maze.rows * maze.columns:
        # maze.export(4, output=f'temp_photos/{fig}.png', show=False, current_cell=(x, y), visited_cells=visited)
        # fig += 1
        # Gather all possible neighbors even visited ones
        possible_directions = []
        if maze.is_valid_position(x-1, y):
            possible_directions.append((x-1, y))
        if maze.is_valid_position(x, y+1):
            possible_directions.append((x, y+1))
        if maze.is_valid_position(x+1, y):
            possible_directions.append((x+1, y))
        if maze.is_valid_position(x, y-1):
            possible_directions.append((x, y-1))

        random.shuffle(possible_directions)
        if possible_directions[0] not in visited:
            maze.path_to_cell(x, y, possible_directions[0][0], possible_directions[0][1])
        
        x, y = possible_directions[0]
        visited.add((x, y))

import time
if __name__ == '__main__':

    setrecursionlimit(1_000_000)
    maze = Maze(64, 64)
    start_time = time.time()
    depth_first_search_r(maze)
    stop_time = time.time()
    print(stop_time-start_time)

    # maze = Maze(5, 5)
    # depth_first_search_r(maze)