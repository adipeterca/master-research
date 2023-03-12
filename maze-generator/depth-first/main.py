import numpy as np
import random

class Maze:
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

    class Cell:
        def __init__(self):
            self.walls = {
                Maze.NORTH : True,
                Maze.EAST : True,
                Maze.SOUTH : True,
                Maze.WEST : True
            }
        def __str__(self):
            return 'Cell '

    def __init__(self, size = 4):
        self.data = []
        for i in range(size):
            _ = []
            for j in range(size):
                _.append(Maze.Cell())
            self.data.append(_)
        
        self.size = size
    
    def path(self, x, y, direction):
        '''
        Destroyes the wall in direction @direction corresponding to cell at positions @x, @y
        '''
        if direction not in [Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST]:
            raise ValueError(f'Incorrect value provided for direction: {direction}\n')
        if x < 0 or y < 0 or x >= self.size or y >= self.size:
            raise ValueError(f'Incorrect values for x or/and y: ({x}, {y}). They must be between [0, {self.size})\n')

        try:
            self.data[x][y].walls[direction] = False
            if direction == Maze.NORTH:
                self.data[x-1][y].walls[Maze.SOUTH] = False
            elif direction == Maze.EAST:
                self.data[x][y+1].walls[Maze.WEST] = False
            if direction == Maze.SOUTH:
                self.data[x+1][y].walls[Maze.NORTH] = False
            if direction == Maze.WEST:
                self.data[x][y-1].walls[Maze.EAST] = False
        except:
            pass
    
    def is_valid_position(self, x, y):
        return x >= 0 and y >= 0 and x < self.size and y < self.size
    
    def __str__(self):
        output = np.full((self.size * 2 + 1, self.size * 2 + 1), '=')
        x = 0
        for i in range(1, 2 * self.size, 2):
            y = 0
            for j in range(1, 2 * self.size, 2):
                output[i][j] = '+'
                if not self.data[x][y].walls[Maze.NORTH]:
                    output[i-1][j] = ' '
                if not self.data[x][y].walls[Maze.EAST]:
                    output[i][j+1] = ' '
                if not self.data[x][y].walls[Maze.SOUTH]:
                    output[i+1][j] = ' '
                if not self.data[x][y].walls[Maze.WEST]:
                    output[i][j-1] = ' '
                y += 1
                if y >= self.size:
                    break
            x += 1
            if x >= self.size:
                break
        return output.__str__()

def depth_first_search(maze : Maze, current_x, current_y, visited : list):
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
        return

    random.shuffle(possible_directions)

    # print(f'Current at position [{current_x}, {current_y}]')
    for dir in possible_directions:
        try:
            if dir == Maze.NORTH and (current_x-1, current_y) not in visited:
                # print(f'\tGoing to position [{current_x-1}, {current_y}]')
                maze.path(current_x, current_y, dir)
                visited.append((current_x, current_y))
                depth_first_search(maze, current_x-1, current_y, visited)

            if dir == Maze.EAST and (current_x, current_y+1) not in visited:
                # print(f'\tGoing to position [{current_x}, {current_y+1}]')
                maze.path(current_x, current_y, dir)
                visited.append((current_x, current_y))
                depth_first_search(maze, current_x, current_y+1, visited)

            if dir == Maze.SOUTH and (current_x+1, current_y) not in visited:
                # print(f'\tGoing to position [{current_x+1}, {current_y}]')
                maze.path(current_x, current_y, dir)
                visited.append((current_x, current_y))
                depth_first_search(maze, current_x+1, current_y, visited)

            if dir == Maze.WEST and (current_x, current_y-1) not in visited:
                # print(f'\tGoing to position [{current_x}, {current_y-1}]')
                maze.path(current_x, current_y, dir)
                visited.append((current_x, current_y))
                depth_first_search(maze, current_x, current_y-1, visited)
        except:
            pass

maze = Maze(28)
depth_first_search(maze, 0, 0, [])
print(maze)