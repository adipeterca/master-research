from amazed.modules.build import hunt_and_kill
from amazed.modules.build import binary_tree
from amazed.modules.build import random_kruskal
from amazed.modules.build import random_carving

from amazed.modules.solver import DFSRandom
from amazed.modules.solver import DFS
from amazed.modules.solver import AStar

from amazed.modules.maze import Maze

import timeit
import random

def standard_euclidian(start, end):
    (x, y) = start
    (endx, endy) = end
    return ((x-endx)**2 + (y-endy)**2) ** 0.5 

def modified_euclidian(start, end):
    (x, y) = start
    (endx, endy) = end
    return ((x-endx)**2 + (y-endy)**2)

def standard_manhattan(start, end):
    (x, y) = start
    (endx, endy) = end
    return abs(x-endx) + abs(y-endy)

def standard_minkowski(start, end, p=3):
    '''
    With p = 1, it's the same as Manhattan distance.\n
    With p = 2, it's the same as Euclidian distance.\n
    With p = inf, it's the same as Chebyshev distance.\n
    '''
    (x, y) = start
    (endx, endy) = end
    return (abs(x-endx)**p + abs(y-endy)**p) ** (1/p)

max_iter = 10
rc = 0.2

for size in (16, 32, 64):
    total_time = {
        "AStar_manh" : 0,
        "AStar_eucl" : 0,
        "AStar_mink" : 0,
        "DFS" : 0,
        "DFSRandom" : 0
    }

    random_sample_iter = random.randint(0, max_iter-1)

    for iter in range(max_iter):
        m = Maze(size, size)
        hunt_and_kill(m)
        if (iter+1) % 100 == 0: 
            print(f"Iteration {iter+1}")

        a1 = AStar(m)
        start = timeit.default_timer()
        a1.solve(h=standard_manhattan)
        total_time["AStar_manh"] += timeit.default_timer() - start
    
        a2 = AStar(m)
        start = timeit.default_timer()
        a2.solve(h=standard_euclidian)
        total_time["AStar_eucl"] += timeit.default_timer() - start

        a3 = AStar(m)
        start = timeit.default_timer()
        a3.solve(h=standard_minkowski)
        total_time["AStar_mink"] += timeit.default_timer() - start

        a4 = DFS(m)
        start = timeit.default_timer()
        a4.solve()
        total_time["DFS"] += timeit.default_timer() - start
        
        a5 = DFSRandom(m)
        start = timeit.default_timer()
        a5.solve()
        total_time["DFSRandom"] += timeit.default_timer() - start

        if iter == random_sample_iter:
            m.export(output="tmp/s_tester_maze_sample.png", show=False)
            a1.image("tmp/s_Astar1.png")
            a2.image("tmp/s_Astar2.png")
            a3.image("tmp/s_Astar3.png")
            a4.image("tmp/s_DFS.png")
            a5.image("tmp/s_DFSRandom.png")

    print(f"[Single solution][{size}x{size}][A* Manh] Average time: {total_time['AStar_manh'] / max_iter:.4f}s")
    print(f"[Single solution][{size}x{size}][A* Eucl] Average time: {total_time['AStar_eucl'] / max_iter:.4f}s")
    print(f"[Single solution][{size}x{size}][A* Mink] Average time: {total_time['AStar_mink'] / max_iter:.4f}s")
    print(f"[Single solution][{size}x{size}][DFS] Average time: {total_time['DFS'] / max_iter:.4f}s")
    print(f"[Single solution][{size}x{size}][DFSR] Average time: {total_time['DFSRandom'] / max_iter:.4f}s")

    for iter in range(max_iter):
        m = Maze(size, size)
        hunt_and_kill(m)
        random_carving(m, rc)
        if (iter+1) % 100 == 0: 
            print(f"Iteration {iter+1}")

        a1 = AStar(m)
        start = timeit.default_timer()
        a1.solve()
        total_time["AStar_manh"] += timeit.default_timer() - start
        
        a2 = AStar(m)
        start = timeit.default_timer()
        a2.solve()
        total_time["AStar_eucl"] += timeit.default_timer() - start
        
        a3 = AStar(m)
        start = timeit.default_timer()
        a3.solve()
        total_time["AStar_mink"] += timeit.default_timer() - start

        a4 = DFS(m)
        start = timeit.default_timer()
        a4.solve()
        total_time["DFS"] += timeit.default_timer() - start
        
        a5 = DFSRandom(m)
        start = timeit.default_timer()
        a5.solve()
        total_time["DFSRandom"] += timeit.default_timer() - start

        if iter == random_sample_iter:
            m.export(output="tmp/m_tester_maze_sample.png", show=False)
            a1.image("tmp/m_Astar1.png")
            a2.image("tmp/m_Astar2.png")
            a3.image("tmp/m_Astar3.png")
            a4.image("tmp/m_DFS.png")
            a5.image("tmp/m_DFSRandom.png")

    print(f"[Multiple solution (rc={rc})][{size}x{size}][A* Manh] Average time: {total_time['AStar_manh'] / max_iter:.4f}s")
    print(f"[Multiple solution (rc={rc})][{size}x{size}][A* Eucl] Average time: {total_time['AStar_eucl'] / max_iter:.4f}s")
    print(f"[Multiple solution (rc={rc})][{size}x{size}][A* Mink] Average time: {total_time['AStar_mink'] / max_iter:.4f}s")
    print(f"[Multiple solution (rc={rc})][{size}x{size}][DFS] Average time: {total_time['DFS'] / max_iter:.4f}s")
    print(f"[Multiple solution (rc={rc})][{size}x{size}][DFSR] Average time: {total_time['DFSRandom'] / max_iter:.4f}s")

'''
[Single solution][16x16][A* Manh] Average time: 0.0029s
[Single solution][16x16][A* Eucl] Average time: 0.0030s
[Single solution][16x16][A* Mink] Average time: 0.0031s
[Single solution][16x16][DFS] Average time: 0.0003s    
[Single solution][16x16][DFSR] Average time: 0.0006s
[Multiple solution (rc=0.005)][16x16][A* Manh] Average time: 0.0061s
[Multiple solution (rc=0.005)][16x16][A* Eucl] Average time: 0.0063s
[Multiple solution (rc=0.005)][16x16][A* Mink] Average time: 0.0063s
[Multiple solution (rc=0.005)][16x16][DFS] Average time: 0.0005s
[Multiple solution (rc=0.005)][16x16][DFSR] Average time: 0.0013s

[Single solution][32x32][A* Manh] Average time: 0.0333s
[Single solution][32x32][A* Eucl] Average time: 0.0358s
[Single solution][32x32][A* Mink] Average time: 0.0362s
[Single solution][32x32][DFS] Average time: 0.0018s
[Single solution][32x32][DFSR] Average time: 0.0067s
[Multiple solution (rc=0.005)][32x32][A* Manh] Average time: 0.0786s
[Multiple solution (rc=0.005)][32x32][A* Eucl] Average time: 0.0809s
[Multiple solution (rc=0.005)][32x32][A* Mink] Average time: 0.0810s
[Multiple solution (rc=0.005)][32x32][DFS] Average time: 0.0032s
[Multiple solution (rc=0.005)][32x32][DFSR] Average time: 0.0139s

[Single solution][64x64][A* Manh] Average time: 0.7458s
[Single solution][64x64][A* Eucl] Average time: 0.7797s
[Single solution][64x64][A* Mink] Average time: 0.7692s
[Single solution][64x64][DFS] Average time: 0.0170s
[Single solution][64x64][DFSR] Average time: 0.0600s
[Multiple solution (rc=0.005)][64x64][A* Manh] Average time: 1.5156s
[Multiple solution (rc=0.005)][64x64][A* Eucl] Average time: 1.5418s
[Multiple solution (rc=0.005)][64x64][A* Mink] Average time: 1.5295s
[Multiple solution (rc=0.005)][64x64][DFS] Average time: 0.0636s
[Multiple solution (rc=0.005)][64x64][DFSR] Average time: 0.1634s
'''