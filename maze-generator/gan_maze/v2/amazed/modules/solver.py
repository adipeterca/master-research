from amazed.modules.maze import Maze

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
        
        if len(self.steps) == 0:
            self.solve()

        frames = []
        for step in self.steps:
            frames.append(self.maze.export(current_cell=step, show=False))

        frames[0].save(path, format="GIF", append_images=frames, save_all=True, duration=100, loop=0)

    def image(self, path):
        '''
        Creates a static image at path @path representing the calculated solution.
        '''

        if len(self.steps) == 0:
            self.solve()

        # image = self.maze.export(current_cell=self.steps, show=False)
        image = self.maze.export(current_cell=self.steps, show=False)
        image.save(path)




class DFS(MazeSolver):
    def solve(self):
        '''
        Uses the Depth-First search approach to find the shortes path from start to finish.
        It uses a deterministic approach to search for the next path (clock-wise).
        '''

        self.cells = [self.start]
        self.visited = [self.start]

        while self.cells[-1] != self.end:       
            if len(self.cells) == 0:
                raise ValueError(f"Could not find a connected path from {self.start} to {self.finish}!")

            (x, y) = self.cells[-1]

            # North
            if self.maze.is_valid_position(x-1, y) and not self.maze.is_wall(x, y, x-1, y) and not (x-1, y) in self.visited:
                self.cells.append((x-1, y))
                self.visited.append((x-1, y))
                continue
            
            # East
            if self.maze.is_valid_position(x, y+1) and not self.maze.is_wall(x, y, x, y+1) and not (x, y+1) in self.visited:
                self.cells.append((x, y+1))
                self.visited.append((x, y+1))
                continue

            # South
            if self.maze.is_valid_position(x+1, y) and not self.maze.is_wall(x, y, x+1, y) and not (x+1, y) in self.visited:
                self.cells.append((x+1, y))
                self.visited.append((x+1, y))
                continue
            
            # West
            if self.maze.is_valid_position(x, y-1) and not self.maze.is_wall(x, y, x, y-1) and not (x, y-1) in self.visited:
                self.cells.append((x, y-1))
                self.visited.append((x, y-1))
                continue

            self.cells.pop()
            
        # Deep copy the list
        for cell in self.cells:
            self.steps.append(cell)
            # self.maze.export(output=f"tmp/step_{i}.png", current_cell=cell, show=False)

    
class Lee(MazeSolver):
    '''
    Used to find the shortest possible path from start to finish.
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
