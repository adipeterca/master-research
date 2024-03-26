import random
import threading
import time
import numpy as np

from amazed.modules.maze import Maze


class Sculptor():
    '''
    Carves a maze in-place.
    '''
    def __init__(self, maze: Maze, seed: int = None, gif: bool = True) -> None:
        self.maze = maze
        self.frames = []
        self.seed = random.random() if seed is None else seed
        random.seed(self.seed)

        self.cell_colors = {}

        if gif:
            self.progress_thread = threading.Thread(target=self.__progress__)
            self.progress_thread.daemon = True
            self.progress_thread.start()

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

        if len(self.frames) == 0:
            raise ValueError("\n\nNo frames available for GIF creation. Maybe you specified 'gif: False' when creating the object?")

        if looping:
            self.frames[0].save(path, format="GIF", append_images=self.frames, save_all=True, duration=speed, loop=1)
        else:
            # With no loop at all, it does not loop...
            self.frames[0].save(path, format="GIF", append_images=self.frames, save_all=True, duration=speed)

    def __progress__(self):
        '''
        Function used by the __init__ method for displaying a somewhat informative progress of the GIF creation.\n
        It takes into account an approximate amount of steps.\n
        It MUST NOT be called outside of __init__.
        '''
        total = self.maze.rows * self.maze.columns
        progress_steps = [0, 10, 25, 50, 75, 90, 100]
        while len(self.frames) <= total and len(progress_steps) > 0:
            actual_p = int(len(self.frames) / total * 100)
            
            if actual_p >= progress_steps[0]:
                print(f"GIF creation {actual_p}%")
                
                del progress_steps[0]
            time.sleep(0.1)
        
        if len(progress_steps) > 0:
            print(f"GIF creation 100%")


class BinaryTree(Sculptor):
    def __init__(self, maze: Maze, seed: int = None, gif: bool = True) -> None:
        super().__init__(maze, seed, gif)

        if gif:
            self.add_frame(0, 0)
        
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
    
                if gif:
                    self.add_frame(i, j)

class HuntAndKill(Sculptor):
    def __init__(self, maze: Maze, seed: int = None, gif: bool = True, x: int = 0, y: int = 0) -> None:
        super().__init__(maze, seed, gif)

        visited = np.zeros((maze.rows, maze.columns))
        
        unvisited_row = 0
        unvisited_column = 0
        self.add_frame(x, y)
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
                while unvisited_row < maze.rows:
                    while unvisited_column < maze.columns:
                        # Make a wall in a random (valid) direction (of an already visited cell) from the first unvisited cell found
                        if visited[unvisited_row][unvisited_column] == 0:
                            possible_directions = []
                            if maze.is_valid_position(unvisited_row-1, unvisited_column) and visited[unvisited_row-1][unvisited_column] == 1:
                                possible_directions.append(Maze.NORTH)
                            if maze.is_valid_position(unvisited_row, unvisited_column+1) and visited[unvisited_row][unvisited_column+1] == 1:
                                possible_directions.append(Maze.EAST)
                            if maze.is_valid_position(unvisited_row+1, unvisited_column) and visited[unvisited_row+1][unvisited_column] == 1:
                                possible_directions.append(Maze.SOUTH)
                            if maze.is_valid_position(unvisited_row, unvisited_column-1) and visited[unvisited_row][unvisited_column-1] == 1:
                                possible_directions.append(Maze.WEST)
                            
                            random.shuffle(possible_directions)

                            # Update the current position
                            # if gif: 
                            #     self.add_frame(x, y)
                            x = unvisited_row
                            y = unvisited_column

                            maze.path(x, y, possible_directions[0])
                            if gif:
                                self.add_frame(x, y)

                            found_unvisited = True
                            break

                        unvisited_column += 1

                    if unvisited_column == maze.columns:
                        unvisited_row += 1
                        unvisited_column = 0

                    if found_unvisited:
                        break
                        
                    
            else:
                random.shuffle(possible_directions)
                maze.path(x, y, possible_directions[0])

                if gif:
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
        
        if gif:
            self.add_frame(x, y)

class DepthFirstSearch(Sculptor):
    def __init__(self, maze: Maze, seed: int = None, gif: bool = True, x: int = 0, y: int = 0, randomized: bool = True, biased_dirs: list = None, biased_level: int = 0) -> None:
        super().__init__(maze, seed, gif)

        if gif:
            self.add_frame(x, y)

        visited = np.zeros((maze.rows, maze.columns))
        stack = list()

        stack.append((-1, -1, x, y))
        while len(stack) > 0:
            (from_x, from_y, x, y) = stack.pop()
            
            
            if visited[x][y] == 1:
                continue

            visited[x][y] = 1

            if from_x != -1 and from_y != -1:
                maze.path_to_cell(from_x, from_y, x, y)
                if gif:
                    self.add_frame(x, y)
            
            # Search for a valid next position
            possible_directions = []
            if maze.is_valid_position(x-1, y) and visited[x-1][y] == 0:

                # Bias control
                if biased_dirs is not None and biased_level > 0:
                    if Maze.NORTH in biased_dirs:
                        for _ in range(biased_level):
                            possible_directions.append((x-1, y))

                possible_directions.append((x-1, y))
            if maze.is_valid_position(x, y+1) and visited[x][y+1] == 0:
                
                # Bias control
                if biased_dirs is not None and biased_level > 0:
                    if Maze.EAST in biased_dirs:
                        for _ in range(biased_level):
                            possible_directions.append((x, y+1))

                possible_directions.append((x, y+1))
            if maze.is_valid_position(x+1, y) and visited[x+1][y] == 0:
                
                # Bias control
                if biased_dirs is not None and biased_level > 0:
                    if Maze.SOUTH in biased_dirs:
                        for _ in range(biased_level):
                            possible_directions.append((x+1, y))

                possible_directions.append((x+1, y))
            if maze.is_valid_position(x, y-1) and visited[x][y-1] == 0:
                
                # Bias control
                if biased_dirs is not None and biased_level > 0:
                    if Maze.WEST in biased_dirs:
                        for _ in range(biased_level):
                            possible_directions.append((x, y-1))

                possible_directions.append((x, y-1))

            # No more new directions available
            if len(possible_directions) == 0:
                continue

            if randomized:
                random.shuffle(possible_directions)

            for dir in possible_directions:
                (to_x, to_y) = dir
                stack.append((x, y, to_x, to_y))
                
        if gif:
            self.add_frame(0, 0)
            
class RandomKruskal(Sculptor):
    def __init__(self, maze: Maze, seed: int = None, gif: bool = True) -> None:
        super().__init__(maze, seed, gif)
        
        if gif:
            self.add_frame(0, 0)

        list_of_cells = []
        for i in range(maze.rows):
            for j in range(maze.columns):
                list_of_cells.append([ [i, j] ])
        
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
                if gif:
                    self.add_frame(x1, y1)
                    self.add_frame(x2, y2)

class AldousBroder(Sculptor):
    def __init__(self, maze: Maze, seed: int = None, gif: bool = True) -> None:
        super().__init__(maze, seed, gif)

        visited = np.full((maze.rows, maze.columns), False)

        # Random start position
        x = random.randint(0, maze.rows-1)
        y = random.randint(0, maze.columns-1)

        if gif:
            self.add_frame(x, y)
        while not np.all(visited):
            visited[x][y] = True

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
            found_dir = False
            for dir in possible_directions:
                if not visited[dir[0]][dir[1]]:
                    if gif:
                        self.add_frame(x, y)
                    maze.path_to_cell(x, y, dir[0], dir[1])
                    
                    x, y = dir
                    found_dir = True
                    break
            
            if not found_dir:
                if gif:
                    self.add_frame(x, y)
                x, y = possible_directions[0]

class RandomCarving(Sculptor):
    def __init__(self, maze: Maze, seed: int = None, gif: bool = True, original_chance:int = 0.05, multicell:bool = True, adaptive:bool = True, adaptive_function = None) -> None:
        super().__init__(maze, seed, gif)

        '''
        Break walls at random in the given @maze. Can be used as a method of creating multiple paths in a single-solution maze.

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
        
        adaptive_function = self.__adaptive_function__ if adaptive_function is None else adaptive_function

        if gif:
            self.add_frame(0, 0)

        chance = original_chance
        streak = 0

        for row in range(maze.rows):
            for col in range(maze.columns):
                valid_dir = []
                if gif:
                    self.add_frame(row, col)
                if maze.is_valid_position(row-1, col):
                    valid_dir.append(Maze.NORTH)
                if maze.is_valid_position(row, col+1):
                    valid_dir.append(Maze.EAST)
                if maze.is_valid_position(row+1, col):
                    valid_dir.append(Maze.SOUTH)
                if maze.is_valid_position(row, col-1):
                    valid_dir.append(Maze.WEST)

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

    def __adaptive_function__(self, choice: float, streak: int) -> float:
        return choice + streak * 0.01
    
class Spiral(Sculptor):
    def __init__(self, maze: Maze, seed: int = None, gif: bool = True, x:int = 0, y:int = 0, max_len:int = 10) -> None:
        super().__init__(maze, seed, gif)

        '''
        Inspired by hunt and kill.
        Select the starting node as (x, y)\n.
        While the current node is NOT visited or NOT outside the maze, select a random direction and follow it until you end up
        with a visited cell or you run out of the maze. Next, starting from (0, 0), perform a grid search and select the next
        unvisited cell and repeat.\n
        can be paired nicely with RandomCarving object.

        @max_len    : represents how long a hallway can be
        '''

        if gif:
            self.add_frame(x, y)

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
                        if gif:
                            self.add_frame(x, y)
                        last_selected_position = i * maze.columns + j
                        break
                    j += 1
                    if j >= maze.columns:
                        j = 0
                        i += 1
                

                continue
            

            # Increase chances to not follow the same direction
            if last_dir is not None:
                aux = possible_directions
                for _ in aux:
                    if _ != last_dir:
                        possible_directions.append(_)
            _dir = random.choice(possible_directions)
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
                if gif:
                    self.add_frame(x, y)

            # If there is no other cell unvisted adjaced to the current position, then search for a new start position.
            if maze.is_valid_position(x-1, y) and (x-1, y) not in visited or \
                maze.is_valid_position(x, y+1) and (x, y+1) not in visited or \
                maze.is_valid_position(x+1, y) and (x+1, y) not in visited or \
                maze.is_valid_position(x, y-1) and (x, y-1) not in visited:
                continue
            

            # Select the next unvisited cell
            i = last_selected_position // maze.columns
            j = last_selected_position % maze.columns
            while maze.columns * i + j < maze.rows * maze.columns:
                if (i, j) not in visited:
                    x = i
                    y = j
                    last_selected_position = i * maze.columns + j
                    if gif:
                        self.add_frame(x, y)
                    break
                j += 1
                if j >= maze.columns:
                    j = 0
                    i += 1