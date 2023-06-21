import numpy as np
from PIL import Image

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

    def __init__(self, rows = 4, columns = 4):
        self.data = []
        for i in range(rows):
            _ = []
            for j in range(columns):
                _.append(Maze.Cell())
            self.data.append(_)
        
        self.rows = rows
        self.columns = columns
    
    def path(self, x, y, direction):
        '''
        Destroyes the wall in direction @direction corresponding to cell at positions @x, @y
        '''
        if direction not in [Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST]:
            raise ValueError(f'Incorrect value provided for direction: {direction}\n')
        if not self.is_valid_position(x, y):
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
    
    def is_valid_position(self, x, y):
        return x >= 0 and y >= 0 and x < self.rows and y < self.columns

    def export(self, distance = 10, output = None, show=True, current_cell=None, visited_cells=None):
        '''
        Exports the maze to an image.
        @distance: the distance of each cell
        @output: path to file
        @show: display the final result
        @current_cell: if set, it will color with red the current cell. Used for GIF creation. MUST BE A set() OBJECT
        @visited_cells: if set, it will color any cell from the visited_cells set() object. Used for GIF creation.
        '''
        new_data = np.zeros((self.rows * distance, self.columns * distance, 3), dtype=np.uint8)

        for i in range(self.rows):
            for j in range(self.columns):

                # Assign no walls at first
                if current_cell != None and current_cell == (i, j):
                    for k1 in range(distance):
                        for k2 in range(distance):
                            new_data[i*distance+k1][j*distance+k2][0] = 255
                            new_data[i*distance+k1][j*distance+k2][1] = 0
                            new_data[i*distance+k1][j*distance+k2][2] = 0
                elif visited_cells != None and (i, j) in visited_cells:
                    for k1 in range(distance):
                        for k2 in range(distance):
                            new_data[i*distance+k1][j*distance+k2][0] = 0
                            new_data[i*distance+k1][j*distance+k2][1] = 255
                            new_data[i*distance+k1][j*distance+k2][2] = 0
                else:
                    for k1 in range(distance):
                        for k2 in range(distance):
                            new_data[i*distance+k1][j*distance+k2][0] = 255
                            new_data[i*distance+k1][j*distance+k2][1] = 255
                            new_data[i*distance+k1][j*distance+k2][2] = 255
                
                # West wall
                # For east wall, it should be j*distance+(distance-1)
                if self.data[i][j].walls[Maze.WEST]:
                    for k in range(distance):
                        new_data[i*distance+k][j*distance][0] = 0
                        new_data[i*distance+k][j*distance][1] = 0
                        new_data[i*distance+k][j*distance][2] = 0
                
                # North wall
                # For south wall, it should be i*distance+(distance-1)
                if self.data[i][j].walls[Maze.NORTH]:
                    for k in range(distance):
                        new_data[i*distance][j*distance+k][0] = 0
                        new_data[i*distance][j*distance+k][1] = 0
                        new_data[i*distance][j*distance+k][2] = 0

        img = Image.fromarray(new_data)
        if output is not None and type(output) is str:
            img.save(output)
        if show:
            img.show()

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

    def array(self, file='array.txt'):
        arr = np.zeros((self.rows, self.columns))
        
        _dict = {}
        _next = 0

        for i in range(self.rows):
            for j in range(self.columns):
                north = self.data[i][j].walls[Maze.NORTH]
                east = self.data[i][j].walls[Maze.EAST]
                south = self.data[i][j].walls[Maze.SOUTH]
                west = self.data[i][j].walls[Maze.WEST]

                if (north, east, south, west) not in _dict:
                    _dict[(north, east, south, west)] = _next
                    _next += 1
                
                arr[i][j] = _dict[(north, east, south, west)]
        
        np.set_printoptions(threshold=np.inf, linewidth=self.columns * 10)
        with open(file, 'w') as fout:
            fout.write(arr.__str__())



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

