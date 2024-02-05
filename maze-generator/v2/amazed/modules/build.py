import random
from amazed.modules.maze import Maze
import numpy as np

# fig = 0
def depth_first_search_r(maze : Maze, current_x=0, current_y=0, visited=None):
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


def hunt_and_kill(maze : Maze, x=0, y=0):
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

    for i in range(maze.rows):
        for j in range(maze.columns):
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


def aldous_broder(maze : Maze):
    visited = set()

    # Random start position
    x = random.randint(0, maze.rows-1)
    y = random.randint(0, maze.columns-1)

    visited.add((x, y))

    while len(visited) < maze.rows * maze.columns:
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


def random_carving(maze : Maze, original_chance=0.05, multicell=True, adaptive=True, adaptive_function=None):
    '''
    Break walls at random in the given @maze.

    @original_chance:   depicts how likely it is for a wall to be broken.
    @multicell: if set to True, will evaluate each individual wall in the current position. \n
                Otherwise, will move on to the next wall after a successful break.
    @adaptive:  if set to True, the chance to break a wall will be influenced by the breaking of recent walls.\n
                Otherwise, each wall will have the same chance to be broken.
    @adaptive_function: what function to use to update the chance after each unbroken wall. \n
                        MUST have the following signature: func (curr_chance, streak_number) -> float.\n
                        By default, it will increase by 0.01 for each consecutive unbreaked wall.\n
                        Works only if @adaptive is set to True.\n
    '''

    def _func(choice : float, streak : int) -> float:
        return choice + streak * 0.01
    
    adaptive_function = _func if adaptive_function is None else adaptive_function

    chance = original_chance
    streak = 0
    for row in range(maze.rows):
        for col in range(maze.columns):
            valid_dir = []
            if maze.is_valid_position(row-1, col):
                valid_dir.append(maze.NORTH)
            if maze.is_valid_position(row, col+1):
                valid_dir.append(maze.EAST)
            if maze.is_valid_position(row+1, col):
                valid_dir.append(maze.SOUTH)
            if maze.is_valid_position(row, col-1):
                valid_dir.append(maze.WEST)

            assert len(valid_dir) >= 2
            
            if multicell:
                for dir in valid_dir:
                    if random.random() < chance:
                        maze.path(row, col, dir)
                        streak = 0
                        chance = original_chance
                    else:
                        streak += 1
                        if adaptive:
                            chance = adaptive_function(original_chance, streak)

            else:
                random.shuffle(valid_dir)
                if random.random() < chance:
                    maze.path(row, col, valid_dir[0])
                    streak = 0
                    chance = original_chance
                else:
                    streak += 1
                    if adaptive:
                        chance = adaptive_function(original_chance, streak)


def boulder(maze : Maze, x=0, y=0, max_len=10):
    '''
    Inspired by hunt and kill.
    Select the starting node as (x, y)\n.
    While the current node is NOT visited or NOT outside the maze, select a random direction and follow it until you end up
    with a visited cell or you run out of the maze. Next, starting from (0, 0), perform a grid search and select the next
    unvisited cell and repeat.\n

    @max_len    : represents how long a hallway can be
    '''

    visited = set()
    last_dir = None
    last_selected_position = 0
    while len(visited) != maze.rows * maze.columns:

        possible_directions = []
        if maze.is_valid_position(x-1, y) and (x-1, y) not in visited: possible_directions.append(Maze.NORTH)
        if maze.is_valid_position(x, y+1) and (x, y+1) not in visited: possible_directions.append(Maze.EAST)
        if maze.is_valid_position(x+1, y) and (x+1, y) not in visited: possible_directions.append(Maze.SOUTH)
        if maze.is_valid_position(x, y-1) and (x, y-1) not in visited: possible_directions.append(Maze.WEST)
        

        if len(possible_directions) == 0:
            visited.add((x, y))

            # Select the next unvisited cell
            i = last_selected_position // maze.columns
            j = last_selected_position % maze.columns
            while maze.columns * i + j < maze.rows * maze.columns:
                if (i, j) not in visited:
                    x = i
                    y = j
                    last_selected_position = i * maze.columns + j
                    break
                j += 1
                if j >= maze.columns:
                    j = 0
                    i += 1
            
            # print(f"[!] Selected next start cell as ({x}, {y})")
            continue
        

        # Increase chances to not follow the same direction
        if last_dir is not None:
            aux = possible_directions
            for _ in aux:
                if _ != last_dir:
                    possible_directions.append(_)
        _dir = random.choice(possible_directions)
        # print(f"({x}, {y}) choose direction {_dir}")
        length = 0
        while True:

            # Calculate the next move
            x_next = x
            y_next = y
            if _dir == Maze.NORTH: x_next = x - 1
            elif _dir == Maze.EAST: y_next = y + 1
            elif _dir == Maze.SOUTH: x_next = x + 1
            else: y_next = y - 1

            if length + 1 == max_len:
                break
            if not maze.is_valid_position(x_next, y_next):
                break
            if (x_next, y_next) in visited:
                break
            
            visited.add((x, y))
            maze.path(x, y, _dir)
            length += 1

            x = x_next
            y = y_next

        # If there is no other cell unvisted adjaced to the current position, then search for a new start position.
        if maze.is_valid_position(x-1, y) and (x-1, y) not in visited or \
             maze.is_valid_position(x, y+1) and (x, y+1) not in visited or \
             maze.is_valid_position(x+1, y) and (x+1, y) not in visited or \
             maze.is_valid_position(x, y-1) and (x, y-1) not in visited:
            continue
        
        # print(f"({x}, {y}) no more available neighboaring cells")

        # Select the next unvisited cell
        i = last_selected_position // maze.columns
        j = last_selected_position % maze.columns
        while maze.columns * i + j < maze.rows * maze.columns:
            if (i, j) not in visited:
                x = i
                y = j
                last_selected_position = i * maze.columns + j
                break
            j += 1
            if j >= maze.columns:
                j = 0
                i += 1
        
        # print(f"Selected next start cell as ({x}, {y})")




class Sculptor():
    '''
    Carves a maze in-place.
    '''
    def __init__(self, maze: Maze, seed: int = None) -> None:
        self.maze = maze
        self.frames = []
        self.seed = random.random() if seed is None else seed
        random.seed(self.seed)

        self.cell_colors = {}

    def add_frame(self, i, j):
        # Show the current cell as red
        self.cell_colors[f"{i}, {j}"] = self.maze.CURRENT_CELL_COLOR

        # Here you can modify the distance
        frame = self.maze.export(show=False, cell_colors=self.cell_colors)
        self.frames.append(frame)
        
        self.cell_colors[f"{i}, {j}"] = self.maze.VISITED_CELL_COLOR

    def export(self, path: str = "maze_carving_process.gif", speed=50, looping=False):
        '''
        Creates a GIF showing the carving process.
        '''
        if not path.endswith(".gif"):
            raise RuntimeError(f"'{path}' does not end with .gif")

        if looping:
            self.frames[0].save(path, format="GIF", append_images=self.frames, save_all=True, duration=speed, loop=1)
        else:
            # With no loop at all, it does not loop...
            self.frames[0].save(path, format="GIF", append_images=self.frames, save_all=True, duration=speed)


class BinaryTree(Sculptor):
    def __init__(self, maze: Maze, seed: int = None) -> None:
        super().__init__(maze, seed)

        for i in range(maze.rows):
            for j in range(maze.columns):
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

                self.add_frame(i, j)

class HuntAndKill(Sculptor):
    def __init__(self, maze: Maze, seed: int = None, x=0, y=0) -> None:
        super().__init__(maze, seed)

        visited = np.zeros((maze.rows, maze.columns))
        
        unvisited_row = 0
        unvisited_column = 0
        for iter in range(maze.rows * maze.columns + 1):
            visited[x][y] = 1

            possible_directions = []
            if maze.is_valid_position(x-1, y) and visited[x-1][y] == 0:
                possible_directions.append(Maze.NORTH)
            if maze.is_valid_position(x, y+1) and visited[x][y+1] == 0:
                possible_directions.append(Maze.EAST)
            if maze.is_valid_position(x+1, y) and visited[x+1][y] == 0:
                possible_directions.append(Maze.SOUTH)
            if maze.is_valid_position(x, y-1) and visited[x][y-1] == 0:
                possible_directions.append(Maze.WEST)
            
            # Perform grid search in order to update x, y
            if len(possible_directions) == 0:

                found_unvisited = False
                for i in range(0, maze.rows):
                    for j in range(0, maze.columns):
                        # Make a wall in a random (valid) direction (of an already visited cell) from the first unvisited cell found
                        if visited[i][j] == 0:
                            possible_directions = []
                            if maze.is_valid_position(i-1, j) and visited[i-1][j] == 1:
                                possible_directions.append(Maze.NORTH)
                            if maze.is_valid_position(i, j+1) and visited[i][j+1] == 1:
                                possible_directions.append(Maze.EAST)
                            if maze.is_valid_position(i+1, j) and visited[i+1][j] == 1:
                                possible_directions.append(Maze.SOUTH)
                            if maze.is_valid_position(i, j-1) and visited[i][j-1] == 1:
                                possible_directions.append(Maze.WEST)
                            
                            random.shuffle(possible_directions)

                            # Update the current position
                            self.add_frame(x, y)
                            x = i
                            y = j

                            if j + 1 == maze.columns:
                                unvisited_row = i+1
                                unvisited_column = 0
                            else:
                                unvisited_row = i
                                unvisited_column = j+1

                            maze.path(x, y, possible_directions[0])
                            self.add_frame(x, y)

                            found_unvisited = True
                            break
                    if found_unvisited:
                        break
                
            else:
                random.shuffle(possible_directions)
                maze.path(x, y, possible_directions[0])
                self.add_frame(x, y)

                # Update current position
                if possible_directions[0] == Maze.NORTH:
                    x = x - 1
                elif possible_directions[0] == Maze.EAST:
                    y = y + 1
                elif possible_directions[0] == Maze.SOUTH:
                    x = x + 1
                else:
                    y = y - 1
            
            