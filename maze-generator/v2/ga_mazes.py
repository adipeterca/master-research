from amazed.modules.maze import Maze
from amazed.modules.solver import DFSHeuristic
import random

if __name__ == "__main__":
    MAZE_SIZE = 10
    GENERATIONS = 500
    CHROMOSOME_LENGTH = MAZE_SIZE * (MAZE_SIZE - 1) + MAZE_SIZE * (MAZE_SIZE - 1)
    POP_SIZE = 70
    POPULATION = []

    MUTATION_CHANCE = 0.1
    CROSSOVER_CHANCE = 0.6

    K_ELITISM = int(POP_SIZE * 10 / 100)

    best_idv = ''
    best_score = 0
    gen_chance = 0

    from amazed.modules.build import HuntAndKill
    from amazed.modules.solver import Lee
    from amazed.modules.solver import flood_fill

    for i in range(POP_SIZE):
        individual = []
        for ii in range(CHROMOSOME_LENGTH):
            if random.random() >= 0.5:
                individual.append("0")
            else:
                individual.append("1")
        POPULATION.append(individual)
    # for i in range(POP_SIZE // 2):
    #     maze = Maze(MAZE_SIZE, MAZE_SIZE)
    #     HuntAndKill(maze, gif=False)
    #     POPULATION.append(maze.get_wall_bitstring())

    scores = None
    for gen in range(1, GENERATIONS+1):
        print("-" * 20)
        print(f"[ GA ] Current generation: {gen:<2}")

        scores = []

        unsolvable = 0
        for index in range(POP_SIZE):
            idv = POPULATION[index]
            assert isinstance(idv, list)

            maze = Maze(MAZE_SIZE, MAZE_SIZE)
            maze.set_wall_bitstring(idv)

            # # Actual dead ends
            # deadends = []
            # for i in range(maze.rows):
            #     for j in range(maze.columns):
            #         walls = 0
            #         for wall in (Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST):
            #             if maze.data[i][j].walls[wall]:
            #                 walls += 1
            #         if walls == 3:
            #             deadends.append((i, j))
            # # Calculate the score for this individual
            # max_score = -1
            # for start in deadends:
            #     for finish in deadends:
            #         if start != finish:
            #             s = DFSHeuristic(maze, start=start, end=finish)
            #             try:
            #                 s.solve()
            #                 score = s.score() / (MAZE_SIZE ** 2)
            #             except:
            #                 score = -1
                        
            #             if score > max_score:
            #                 max_score = score

            # if max_score == -1:
            #     unsolvable += 1
            # scores[index] = max_score

            #   [ GA ] Best strategy (overall): 110000100001000011100001001001111000100100101000100100011100011101000011001100110000101000100100100011111000101101010001001100000111000010110010011010101110010010001000000110010110   
            #   [ GA ] Best score (overall): 0.61
            #   [ GA ] Set in generation: 71

            # T intersections
            intersections = 0
            blocked_cells = 0
            for i in range(maze.rows):
                for j in range(maze.columns):
                    walls = 0
                    for wall in (Maze.NORTH, Maze.EAST, Maze.SOUTH, Maze.WEST):
                        if maze.data[i][j].walls[wall]:
                            walls += 1
                    if walls == 0:
                        intersections += -0.1
                    if walls == 1:
                        intersections += 0.1
                    if walls == 2:
                        intersections += 0.4
                    if walls == 3:
                        intersections += 0.2
                    if walls == 4:
                        intersections += -1

            curr_score = intersections / (MAZE_SIZE ** 2)
            areas = flood_fill(maze)
            curr_score = curr_score + 1 / areas
            # s = Lee(maze)

            # try:
            #     s.solve()
            #     curr_score += 4
            # except:
            #     pass
            
            # if not s.is_connected():
                
            #     unsolvable += 1
            scores.append((index, curr_score))
            
        # print(f"unsolvable = {unsolvable} / {POP_SIZE}")
        if gen == GENERATIONS:
            break

        sorted_scores = sorted(scores, key=lambda item: item[1])


        best_individual_index = sorted_scores[-1][0]
        best_individual_score = sorted_scores[-1][1]
        best_individual = POPULATION[best_individual_index]

        if best_score <= best_individual_score:
            best_score = best_individual_score
            best_idv = best_individual
            gen_chance = gen
            

        total_fitness = sum(_[1] for _ in sorted_scores)
        probabilities = [f / total_fitness for _, f in sorted_scores]

        cumulative_probabilities = [0]
        cumulative_sum = 0
        for p in probabilities:
            cumulative_sum += p
            cumulative_probabilities.append(cumulative_sum)

        # Selection using roulette wheel
        new_pop = []
        for i in range(POP_SIZE):
            spin = random.random()
            for j in range(POP_SIZE):
                if cumulative_probabilities[j] <= spin and spin < cumulative_probabilities[j+1]:
                    new_pop.append(POPULATION[j])
                    break

        # print("[ GA ] New population:")
        # print(*new_pop, sep="\n")

        # Crossover
        for i in range(0, POP_SIZE, 2):
            if random.random() < CROSSOVER_CHANCE:
                crossover_point = random.randint(1, CHROMOSOME_LENGTH-1)

                x = new_pop[i][:crossover_point] + new_pop[i+1][crossover_point:]
                y = new_pop[i+1][:crossover_point] + new_pop[i][crossover_point:]

                new_pop[i] = x
                new_pop[i+1] = y
        
        # print("[ GA ] New population (after crossover):")
        # print(*new_pop, sep="\n")

        for i in range(POP_SIZE):
            for j in range(CHROMOSOME_LENGTH):
                if random.random() < MUTATION_CHANCE:
                    if new_pop[i][j] == "0":
                        new_pop[i][j] = "1"
                    elif new_pop[i][j] == "1":
                        new_pop[i][j] = "0"
                    else:
                        raise ValueError(f"[ GA ] What :keklmao: {new_pop[i][j]}")
                    
        # print("[ GA ] New population (after mutation):")
        # print(*new_pop, sep="\n")

        # Elitism
        for k in range(K_ELITISM):
            idv_index = sorted_scores[-k][0]
            new_pop[-k] = POPULATION[idv_index]

        if len(new_pop) != len(POPULATION):
            print(*new_pop, sep="\n")
            raise RuntimeError(f"how did you??")
        POPULATION = new_pop


    print(f"[ GA ] Best strategy (overall): {''.join(best_idv)}")
    print(f"[ GA ] Best score (overall): {best_score:.3f}")
    print(f"[ GA ] Set in generation: {gen_chance}")

    print("Top 10 scores for the last generation:")
    for i in range(1, 11):
        index, score = sorted_scores[-i]
        print(f"Individual {i} has score {score:.3f}.")

    maze = Maze(MAZE_SIZE, MAZE_SIZE)
    maze.set_wall_bitstring(best_idv)

    maze.export(output="tmp/maze_ga_best.png", show=False)

    best_individual_index = sorted_scores[-1][0]
    best_individual_score = sorted_scores[-1][1]
    best_individual = POPULATION[best_individual_index]

    maze = Maze(MAZE_SIZE, MAZE_SIZE)
    maze.set_wall_bitstring(best_individual)

    maze.export(output="tmp/maze_ga_individual.png", show=False)





