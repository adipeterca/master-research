import numpy as np
from PIL import Image
from amazed.modules.data_types import cells

class Vector2D():
    def __init__(self, x_or_pair, y=None):
        if y is None:
            if isinstance(x_or_pair, tuple) and len(x_or_pair) == 2:
                self.x, self.y = x_or_pair
            else:
                raise ValueError("Expected a tuple with 2 values.")
        else:
            self.x = x_or_pair
            self.y = y

    def to_tuple(self) -> tuple:
        return (self.x, self.y)

    def __add__(self, other):
        new_x = self.x + other.x
        new_y = self.y + other.y
        return Vector2D(new_x, new_y)
    
    def __sub__(self, other):
        if isinstance(other, tuple):
            new_x = self.x - other[0]
            new_y = self.y - other[1]
        else:
            new_x = self.x - other.x
            new_y = self.y - other.y
        return Vector2D(new_x, new_y)
    
    def __rsub__(self, other):
        if isinstance(other, tuple):
            new_x = other[0] - self.x
            new_y = other[1] - self.y

            return Vector2D(new_x, new_y)
        else:
            raise TypeError("Unsupported operand types")
    
    def __eq__(self, other):
        if isinstance(other, Vector2D):
            return self.x == other.x and self.y == other.y
        else:
            return False
    
    def __hash__(self):
        return hash(hash(str(self.x)) + hash(str(self.y)))

    def __str__(self):
        return f"({self.x}, {self.y})"
class Maze:
    # Old values. IF SOMETHING DOESN'T WORK THAT IS NOT RELATED TO REINFORCEMENT LEARNING, IS BECAUSE OF THIS
    # NORTH = 1
    # EAST = 2
    # SOUTH = 3
    # WEST = 4
    NORTH = Vector2D(-1, 0)
    EAST = Vector2D(0, 1)
    SOUTH = Vector2D(1, 0)
    WEST = Vector2D(0, -1)

    START_COLOR = (0, 255, 0)
    END_COLOR = (0, 255, 255)
    WALL_COLOR = (0, 0, 0)
    DEFAULT_COLOR = (255, 255, 255)
    CHECKERS_1 = (220, 220, 220)
    CHECKERS_2 = (240, 240, 240)
    CURRENT_CELL_COLOR = (219, 85, 7)
    VISITED_CELL_COLOR = (200, 250, 200)

    class Cell:
        '''
        Default class for maze cells.
        '''
        def __init__(self):
            self.walls = {
                Maze.NORTH : True,
                Maze.EAST : True,
                Maze.SOUTH : True,
                Maze.WEST : True
            }
            self.active = True

        def get_walls(self):
            walls = ""
            if self.walls[Maze.NORTH]: walls += "1"
            if self.walls[Maze.EAST]: walls += "1"
            if self.walls[Maze.SOUTH]: walls += "1"
            if self.walls[Maze.WEST]: walls += "1"

            return walls
        
        def __str__(self):
            return 'Cell '

    def __init__(self, rows:int=4, columns:int=4, constructor:Cell=Cell):
        '''
        Constructs a maze according to the number of rows/columns provided.
        '''
        self.data = []
        for i in range(rows):
            _ = []
            for j in range(columns):
                _.append(constructor())
            self.data.append(_)
        
        self.rows = rows
        self.columns = columns
        self.cell_type = constructor
        self.no_cells = rows * columns

        # Number of all walls (both external and internal)
        self.no_walls = rows * (columns - 1) + columns * (rows - 1) + (rows * 2 + columns * 2)

    def reset(self):
        self.data.clear()
        for i in range(self.rows):
            _ = []
            for j in range(self.columns):
                _.append(self.cell_type())
            self.data.append(_)
    
    def path(self, x, y, direction):
        '''
        Destroyes the wall in direction @direction corresponding to cell at positions @x, @y.\n
        Returns @True on success, @False on failure (incorrect path carving).
        '''
        if direction not in [Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST]:
            raise ValueError(f'Incorrect value provided for direction: {direction}\n')
        if not self.is_valid_position(x, y):
            raise ValueError(f'Incorrect values for x or/and y: ({x}, {y}). They must be between [0, {self.rows}])\n')

        try:
            if direction == Maze.NORTH:
                self.data[x-1][y].walls[Maze.SOUTH] = False
            elif direction == Maze.EAST:
                self.data[x][y+1].walls[Maze.WEST] = False
            if direction == Maze.SOUTH:
                self.data[x+1][y].walls[Maze.NORTH] = False
            if direction == Maze.WEST:
                self.data[x][y-1].walls[Maze.EAST] = False
            self.data[x][y].walls[direction] = False
            self.no_walls -= 1
            return True
        except:
            return False
    
    def wall(self, x, y, direction):
        '''
        Similar to self.path()
        Add the wall in direction @direction corresponding to cell at positions @x, @y.\n
        Returns @True on success, @False on failure (incorrect wall adding).
        '''
        if direction not in [Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST]:
            raise ValueError(f'[wall] Incorrect value provided for direction: {direction}\n')
        if not self.is_valid_position(x, y):
            raise ValueError(f'[wall] Incorrect values for x or/and y: ({x}, {y}). They must be between [0, {self.rows}])\n')

        try:
            if direction == Maze.NORTH:
                self.data[x-1][y].walls[Maze.SOUTH] = True
            elif direction == Maze.EAST:
                self.data[x][y+1].walls[Maze.WEST] = True
            if direction == Maze.SOUTH:
                self.data[x+1][y].walls[Maze.NORTH] = True
            if direction == Maze.WEST:
                self.data[x][y-1].walls[Maze.EAST] = True
            self.data[x][y].walls[direction] = True
            self.no_walls += 1
            return True
        except:
            return False

    def path_to_cell(self, x1, y1, x2, y2):
        '''
        Simillar to path, but it accepts two adjacent cells.

        '''
        if abs(x1-x2) != 1 and abs(y1-y2) != 1:
            raise ValueError(f'Incorrect values provided! Cells need to be adjacent and different: ({x1}, {y1}), ({x2}, {y2})')
        
        if not self.is_valid_position(x1, y1):
            raise ValueError(f'Incorrect values for x or/and y: ({x1}, {y1}). They must be between [0, {self.size})\n')
        
        if not self.is_valid_position(x2, y2):
            raise ValueError(f'Incorrect values for x or/and y: ({x2}, {y2}). They must be between [0, {self.size})\n')
        
        # Figure out the direction
        dir = None
        if x1 < x2:
            dir = Maze.SOUTH
        elif x1 > x2:
            dir = Maze.NORTH
        elif y1 < y2:
            dir = Maze.EAST
        else:
            dir = Maze.WEST
        
        self.path(x1, y1, dir)

    def possible_actions(self, x:int , y:int) -> list:
        '''
        An action represents a valid move from the given cell.\n
        A move is valid if there aren't any walls in that direction.\n
        Returns a list if at least one possible action can be made or None if there aren't any.
        '''

        if not self.is_valid_position(x, y):
            raise ValueError(f'Incorrect values for x or/and y: ({x}, {y}). They must be between x \in [0, {self.rows}] and y \in [0, {self.columns}])\n')
        
        possible_actions = []
        if self.is_valid_position(x-1, y) and not self.is_wall(x, y, x-1, y):
            possible_actions.append(Maze.NORTH)
        if self.is_valid_position(x, y+1) and not self.is_wall(x, y, x, y+1):
            possible_actions.append(Maze.EAST)
        if self.is_valid_position(x+1, y) and not self.is_wall(x, y, x+1, y):
            possible_actions.append(Maze.SOUTH)
        if self.is_valid_position(x, y-1) and not self.is_wall(x, y, x, y-1):
            possible_actions.append(Maze.WEST)

        return None if len(possible_actions) == 0 else possible_actions

    def is_valid_position(self, x, y):
        return x >= 0 and y >= 0 and x < self.rows and y < self.columns and self.data[x][y].active
    
    def is_wall(self, x1, y1, x2, y2):
        '''
        Is there a wall between cell [@x1][@y1] and [@x2][@y2]?
        '''
        if abs(x1-x2) != 1 and abs(y1-y2) != 1:
            raise ValueError(f'Incorrect values provided! Cells need to be adjacent and different: ({x1}, {y1}), ({x2}, {y2})')
        
        if not self.is_valid_position(x1, y1):
            raise ValueError(f'Incorrect values for x or/and y: ({x1}, {y1}). They must be between x \in [0, {self.rows}] and y \in [0, {self.columns}])\n')
        
        if not self.is_valid_position(x2, y2):
            raise ValueError(f'Incorrect values for x or/and y: ({x2}, {y2}). They must be between x \in [0, {self.rows}] and y \in [0, {self.columns}])\n')
        
        # Figure out the direction
        dir = None
        if x1 < x2:
            dir = Maze.SOUTH
        elif x1 > x2:
            dir = Maze.NORTH
        elif y1 < y2:
            dir = Maze.EAST
        else:
            dir = Maze.WEST
        
        return self.data[x1][y1].walls[dir]
    
    def is_valid_move(self, x, y, dir):
        if not self.is_valid_position(x, y):
            print(f"Not a valid start position: {x}, {y}")
            return False
        
        x2 = x
        y2 = y
        if dir == self.NORTH: x2 = x - 1
        elif dir == self.EAST: y2 = y + 1
        elif dir == self.SOUTH: x2 = x + 1
        else: y2 = y - 1
        

        if not self.is_valid_position(x2, y2):
            print(f"Not a valid end position: {x2}, {y2}")
            return False
        
        if self.is_wall(x, y, x2, y2):
            print(f"There is a wall between {x}, {y} and {x2}, {y2}")
            return False
        
        return True    

    def toggle(self):
        '''
        Toggles all walls for the current Maze object. \n
        Example: given a cell with walls on the North and South side, after this operation
        it will have walls on the East and West side.
        '''

        self.no_walls = 0
        for i in range(self.rows):
            for j in range(self.columns):
                for dir in [Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST]:
                    self.data[i][j].walls[dir] = not self.data[i][j].walls[dir]
                    
                    # Increment wall count if now a wall is present!
                    if self.data[i][j].walls[dir]:
                        self.no_walls += 1


    def get_wall_bitstring(self):
        '''
        First map all vertical walls, then horizontal. Only internal walls are checked.
        '''
        idv = []
        for i in range(self.rows):
            for j in range(self.columns - 1):
                if self.data[i][j].walls[Maze.EAST]:
                    idv.append("1")
                else:
                    idv.append("0")
        
        for i in range(self.rows - 1):
            for j in range(self.columns):
                if self.data[i][j].walls[Maze.SOUTH]:
                    idv.append("1")
                else:
                    idv.append("0")
        return idv

    def set_wall_bitstring(self, idv: list | str):
        '''
        First construct vertical mazes, then horizontal. \n
        The maze needs to be reseted first.
        '''
        if (len(idv) == 0):
            return None
        if isinstance(idv, str):
            idv = [_ for _ in idv]
        counter = 0
        for i in range(self.rows):
            for j in range(self.columns - 1):
                if idv[counter] == "0":
                    self.path(i, j, Maze.EAST)
                counter += 1
        for i in range(self.rows - 1):
            for j in range(self.columns):
                if idv[counter] == "0":
                    self.path(i, j, Maze.SOUTH)
                counter += 1


    def export(self, distance:int=10, output:str=None, show:bool=True, cell_colors:dict=None, checkers:bool=True):
        """
        Exports the maze to an image.
        @distance: the distance of each cell
        @output: path to file
        @show: display the final result
        @cell_colors: a dict with the following format:\n
                    {
                        "{row}, {column}" : (red, green, blue)
                    }
                    By default, all cells are colored with DEFAULT_COLOR.
        @checkers: default background color will change to a checkers pattern.
        """
        new_data = np.zeros((self.rows * distance + 1, self.columns * distance + 1, 3), dtype=np.uint8)

        # Setting default values
        if cell_colors is None:
            cell_colors = {}

        # cell_colors["0, 0"] = self.START_COLOR
        # cell_colors[f"{self.rows-1}, {self.columns-1}"] = self.END_COLOR


        for i in range(self.rows):
            for j in range(self.columns):

                for k1 in range(distance):
                    for k2 in range(distance):
                        key = f"{i}, {j}"
                        if key in cell_colors:
                            new_data[i*distance+k1][j*distance+k2][0] = cell_colors[key][0]
                            new_data[i*distance+k1][j*distance+k2][1] = cell_colors[key][1]
                            new_data[i*distance+k1][j*distance+k2][2] = cell_colors[key][2]
                        else:
                            if checkers:
                                if (i+j) % 2 == 0:
                                    new_data[i*distance+k1][j*distance+k2][0] = self.CHECKERS_1[0]
                                    new_data[i*distance+k1][j*distance+k2][1] = self.CHECKERS_1[1]
                                    new_data[i*distance+k1][j*distance+k2][2] = self.CHECKERS_1[2]
                                else:
                                    new_data[i*distance+k1][j*distance+k2][0] = self.CHECKERS_2[0]
                                    new_data[i*distance+k1][j*distance+k2][1] = self.CHECKERS_2[1]
                                    new_data[i*distance+k1][j*distance+k2][2] = self.CHECKERS_2[2]
                            else:
                                # Just make them white
                                new_data[i*distance+k1][j*distance+k2][0] = self.DEFAULT_COLOR[0]
                                new_data[i*distance+k1][j*distance+k2][1] = self.DEFAULT_COLOR[1]
                                new_data[i*distance+k1][j*distance+k2][2] = self.DEFAULT_COLOR[2]
                
                # West wall
                # For east wall, it should be j*distance+(distance-1)
                if self.data[i][j].walls[Maze.WEST]:
                    for k in range(distance):
                        new_data[i*distance+k][j*distance][0] = self.WALL_COLOR[0]
                        new_data[i*distance+k][j*distance][1] = self.WALL_COLOR[1]
                        new_data[i*distance+k][j*distance][2] = self.WALL_COLOR[2]
                
                # North wall
                # For south wall, it should be i*distance+(distance-1)
                if self.data[i][j].walls[Maze.NORTH]:
                    for k in range(distance):
                        new_data[i*distance][j*distance+k][0] = self.WALL_COLOR[0]
                        new_data[i*distance][j*distance+k][1] = self.WALL_COLOR[1]
                        new_data[i*distance][j*distance+k][2] = self.WALL_COLOR[2]
        
        # Add the EAST and SOUTH border
        for i in range(self.rows):
            new_data[i][-1][0] = self.WALL_COLOR[0]
            new_data[i][-1][1] = self.WALL_COLOR[1]
            new_data[i][-1][2] = self.WALL_COLOR[2]
        for i in range(self.columns):
            new_data[-1][i][0] = self.WALL_COLOR[0]
            new_data[-1][i][1] = self.WALL_COLOR[1]
            new_data[-1][i][2] = self.WALL_COLOR[2]

        img = Image.fromarray(new_data)
        if output is not None and type(output) is str:
            img.save(output)
        if show:
            img.show()

        return img

    def graph(self, file='graph.txt'):
        '''
        0s mark the presence of a wall.
        1s mark a path between cell 'i' and cell 'j'.
        The graph is undirected.
        A cell has no path to itself.
        '''
        G = np.zeros((self.rows**2, self.columns**2), dtype=np.uint8)
        
        for i in range(self.rows):
            for j in range(self.columns):
                k1 = i * self.rows + j
                if not self.data[i][j].walls[Maze.NORTH]:
                    k2 = (i-1) * self.rows + j
                    G[k1][k2] = 1
                    G[k2][k1] = 1
                if not self.data[i][j].walls[Maze.EAST]:
                    k2 = i * self.rows + (j+1)
                    G[k1][k2] = 1
                    G[k2][k1] = 1
                if not self.data[i][j].walls[Maze.SOUTH]:
                    k2 = (i+1) * self.rows + j
                    G[k1][k2] = 1
                    G[k2][k1] = 1
                if not self.data[i][j].walls[Maze.WEST]:
                    k2 = i * self.rows + (j-1)
                    G[k1][k2] = 1
                    G[k2][k1] = 1
        np.set_printoptions(threshold=np.inf, linewidth=G.size)
        open(file, 'w').write(G.__str__())
    
    def adjancency_list(self, file='list.txt'):
        L = []

        for i in range(self.rows):
            for j in range(self.columns):
                L.append([])
                k1 = i * self.rows + j
                if not self.data[i][j].walls[Maze.NORTH]:
                    k2 = (i-1) * self.rows + j
                    L[k1].append(k2)
                if not self.data[i][j].walls[Maze.EAST]:
                    k2 = i * self.rows + (j+1)
                    L[k1].append(k2)
                if not self.data[i][j].walls[Maze.SOUTH]:
                    k2 = (i+1) * self.rows + j
                    L[k1].append(k2)
                if not self.data[i][j].walls[Maze.WEST]:
                    k2 = i * self.rows + (j-1)
                    L[k1].append(k2)
        with open(file, 'w') as fout:
            for line in L:
                fout.write(f'{line}\n')

    def array(self, file=None) -> np.ndarray:
        '''
        Encodes the current maze into a numerical integer matrix, with values between [0, 15].\n
        If @file is specified, the array will be written to a file instead of being returned.
        '''
        arr = np.zeros((self.rows, self.columns))

        for i in range(self.rows):
            for j in range(self.columns):

                index = ''
                if self.data[i][j].walls[Maze.NORTH]:
                    index += ' NORTH '
                if self.data[i][j].walls[Maze.EAST]:
                    index += ' EAST '
                if self.data[i][j].walls[Maze.SOUTH]:
                    index += ' SOUTH '
                if self.data[i][j].walls[Maze.WEST]:
                    index += ' WEST '
                index = index.strip()
                index = index.replace('  ', ' ')
                
                arr[i][j] = cells['types'][index]
        
        if file is None:
            # np.set_printoptions(threshold=np.inf, linewidth=np.inf)
            # print(arr.flatten())
            return arr.flatten()
        else:
            np.set_printoptions(threshold=np.inf, linewidth=self.columns * 10)
            with open(file, 'w') as fout:
                fout.write(arr.__str__())

    def build_from_array(arr : np.ndarray, rows : int, columns : int):
        if rows * columns != arr.size:
            raise ValueError('The maze must have the number of rows and columns per total equal with the total number of elements in the array!')
        
        result = Maze(rows, columns)
        arr = arr.reshape((rows, columns))

        for i in range(rows):
            for j in range(columns):
                if 'NORTH' not in cells['types-numerical'][arr[i][j]]:
                    result.path(i, j, Maze.NORTH)
                if 'EAST' not in cells['types-numerical'][arr[i][j]]:
                    result.path(i, j, Maze.EAST)
                if 'SOUTH' not in cells['types-numerical'][arr[i][j]]:
                    result.path(i, j, Maze.SOUTH)
                if 'WEST' not in cells['types-numerical'][arr[i][j]]:
                    result.path(i, j, Maze.WEST)
        return result

    def print(self):
        for i in range(self.rows):
            for j in range(self.columns):
                print(f'Cell [{i}, {j}]')
                print(f'\tNORTH wall: {self.data[i][j].walls[Maze.NORTH]}')
                print(f'\tEAST wall: {self.data[i][j].walls[Maze.EAST]}')
                print(f'\tSOUTH wall: {self.data[i][j].walls[Maze.SOUTH]}')
                print(f'\tWEST wall: {self.data[i][j].walls[Maze.WEST]}')

    def __str__(self):
        output = np.full((self.rows * 2 + 1, self.columns * 2 + 1), '.')
        x = 0
        for i in range(1, 2 * self.rows, 2):
            y = 0
            for j in range(1, 2 * self.columns, 2):
                output[i][j] = '+'
                if not self.data[x][y].walls[Maze.NORTH]:
                    output[i-1][j] = ' '
                else:
                    output[i-1][j] = '='
                
                if not self.data[x][y].walls[Maze.EAST]:
                    output[i][j+1] = ' '
                else:
                    output[i][j+1] = '='
                if not self.data[x][y].walls[Maze.SOUTH]:
                    output[i+1][j] = ' '
                else:
                    output[i+1][j] = '='
                if not self.data[x][y].walls[Maze.WEST]:
                    output[i][j-1] = ' '
                else:
                    output[i][j-1] = '='
                y += 1
                if y >= self.columns:
                    break
            x += 1
            if x >= self.rows:
                break
        return output.__str__()

