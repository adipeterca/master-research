from both import GameMaster
from strategies import SimpleAgent

import random

if __name__ == "__main__":

    GENERATIONS = 5
    CHROMOSOME_LENGTH = SimpleAgent.CHROMOSOME_LENGTH
    POP_LENGHT = 10          # Aim for an even number (see crossover)
    POPULATION = []

    MUTATION_CHANCE = 0.1
    CROSSOVER_CHANCE = 0.95

    best_strategy = None
    best_score = 0
    gen_chance = 0

    for i in range(POP_LENGHT):
        individual = []
        for ii in range(CHROMOSOME_LENGTH):
            if random.random() >= 0.5:
                individual.append("0")
            else:
                individual.append("1")
        POPULATION.append(individual)

    scores = None
    for gen in range(1, GENERATIONS+1):
        print("-" * 20)
        print(f"[ GA ] Current generation: {gen:<2}")

        scores = {}

        for i, strategyA in enumerate(POPULATION):
            for j, strategyB in enumerate(POPULATION):

                print(f"[ GA ] Evaluating strategies {i} vs {j}")

                gm = GameMaster(seed=gen+i+j)
                gm.playerA.set_strategy(strategyA)
                gm.playerB.set_strategy(strategyB)

                # print("[ GA ] Strategy for PlayerA:")
                # print(f"\tdnext = {gm.playerA.dnext}")
                # print(f"\tdxnext = {gm.playerA.dxnext}")
                # print(f"\tmreq = {gm.playerA.mreq}")
                # print(f"\tmoff = {gm.playerA.moff}")
                # print(f"\tscore_threshold = {gm.playerA.score_threshold}")
                # print(f"\tdfs_exploration_chance = {gm.playerA.dfs_exploration_chance}")
                
                # print("[ GA ] Strategy for PlayerB:")
                # print(f"\tdnext = {gm.playerB.dnext}")
                # print(f"\tdxnext = {gm.playerB.dxnext}")
                # print(f"\tmreq = {gm.playerB.mreq}")
                # print(f"\tmoff = {gm.playerB.moff}")
                # print(f"\tscore_threshold = {gm.playerB.score_threshold}")
                # print(f"\tdfs_exploration_chance = {gm.playerB.dfs_exploration_chance}")


                gm.run(training=True)

                indexA = f"{i}-" + "".join(strategyA)
                indexB = f"{j}-" + "".join(strategyB)

                if indexA in scores:
                    scores[indexA] += gm.playerA.score / gm.iteration
                else:
                    scores[indexA] = gm.playerA.score / gm.iteration
                
                if indexB in scores:
                    scores[indexB] += gm.playerB.score / gm.iteration
                else:
                    scores[indexB] = gm.playerB.score / gm.iteration

                if gm.state == GameMaster.QUIT:
                    exit()

                for e, state in enumerate(gm.results):
                    if state == GameMaster.WIN_A:
                        print(f"[ GA ][ Round {e+1:<2} ] A won.")
                    elif state == GameMaster.WIN_B:
                        print(f"[ GA ][ Round {e+1:<2} ] B won.")
                    elif state == GameMaster.DRAW:
                        print(f"[ GA ][ Round {e+1:<2} ] Draw.")
                    else:
                        raise ValueError(f"What kind of state <{type(state)}> with value <{state}> did you append in round {e}?")
                    
        sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1]))
        print("[ GA ] Scores:")
        for key, value in sorted_scores.items():
            print(f"{key}: {value}")

        best_individual_index = max(scores, key=scores.get)
        best_individual_score = scores[best_individual_index]
        best_individual = best_individual_index.split("-")[1]
        print(f"[ GA ] Best individual strategy (for this game): {best_individual}")
        print(f"[ GA ] Best individual score (for this game): {best_individual_score}")

        if best_score < best_individual_score:
            best_score = best_individual_score
            best_strategy = best_individual
            gen_chance = gen

        total_fitness = sum(sorted_scores.values())
        probabilities = [f / total_fitness for f in sorted_scores.values()]

        cumulative_probabilities = [0]
        cumulative_sum = 0
        for p in probabilities:
            cumulative_sum += p
            cumulative_probabilities.append(cumulative_sum)

        # Selection using roulette wheel
        new_pop = []
        for i in range(POP_LENGHT):
            spin = random.random()
            for j in range(POP_LENGHT):
                if cumulative_probabilities[j] <= spin and spin < cumulative_probabilities[j+1]:
                    new_pop.append(POPULATION[j])
                    break

        # print("[ GA ] New population:")
        # print(*new_pop, sep="\n")

        # Crossover
        for i in range(0, POP_LENGHT, 2):
            if random.random() < CROSSOVER_CHANCE:
                crossover_point = CHROMOSOME_LENGTH // 2

                x = new_pop[i][:crossover_point] + new_pop[i+1][crossover_point:]
                y = new_pop[i+1][:crossover_point] + new_pop[i][crossover_point:]

                new_pop[i] = x
                new_pop[i+1] = y
        
        # print("[ GA ] New population (after crossover):")
        # print(*new_pop, sep="\n")

        for i in range(POP_LENGHT):
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
        
        if len(new_pop) != len(POPULATION):
            print(*new_pop, sep="\n")
            raise RuntimeError(f"how did you??")
        POPULATION = new_pop


    print(f"[ GA ] Best strategy (overall): {best_strategy}")
    print(f"[ GA ] Best score (overall): {best_score}")
    print(f"[ GA ] Set in generation: {gen_chance}")