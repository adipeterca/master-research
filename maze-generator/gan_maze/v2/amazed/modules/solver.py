from maze import Maze

class MazeSolver:
    '''
    Class-template depicting a maze-solving algorithm.
    Each object will hold one and ONLY one path from start to finish.
    By default, the maze starts at (0, 0) and ends at (rows-1, columns-1).
    '''

    def __init__(self, maze : Maze, start=None, end=None):
        self.maze = maze
        self.steps = []

        self.start = (0, 0) if start is None else start
        self.end = (maze.rows-1, maze.columns-1) if end is None else end

    def solve(self):
        '''
        Virtual function which needs to be overwritten by all solving methods that inherit this class.
        '''
        raise NameError("Calling <solve()> from a template object!")

    def score(self):
        '''
        Euristich function used to determine how hard a maze was to solve.
        '''
        return len(self.steps)

    def gif(self, path):
        '''
        Creates a GIF at path @path by solving the maze.
        '''

class DFS(MazeSolver):
    def solve(self):
        '''
        Uses the Depth-First search approach to find the shortes path from start to finish.
        '''

class Lee(MazeSolver):
    '''
    DEPRECATED, NOT NEEDED!
    '''
    
    def solve(self):
        '''
        Applies the Lee Traversal Algorithm on the given maze.
        '''

        if len(self.steps) != 0:
            raise ValueError("Calling Lee() multiple times on the same maze!")
        
        self.unvisited_cells = [self.start]
        self.visit()


    def visit(self):
        if len(self.unvisited_cells) == 0:
            return
        
        row = self.unvisited_cells[0][0]
        col = self.unvisited_cells[0][1]

        if self.maze.is_valid_position(row-1, col) and not self.maze.is_wall(row, col, row-1, col):
            self.unvisited_cells.append((row-1, col))
        if self.maze.is_valid_position(row+1, col) and not self.maze.is_wall(row, col, row+1, col):
            self.unvisited_cells.append((row+1, col))
        if self.maze.is_valid_position(row, col-1) and not self.maze.is_wall(row, col, row, col-1):
            self.unvisited_cells.append((row, col-1))
        if self.maze.is_valid_position(row, col+1) and not self.maze.is_wall(row, col, row, col+1):
            self.unvisited_cells.append((row, col+1))
