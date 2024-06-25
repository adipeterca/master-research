from colab import GameMaster
from strategies import SimpleAgent

import random
import logging
from datetime import datetime

if __name__ == "__main__":

    logger = logging.getLogger("GeneticAlgorithm")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("genetic-algorithm.log", mode="w")
    file_handler.setFormatter(logging.Formatter("[ %(levelname)s ] %(message)s"))
    logger.addHandler(file_handler)

    start_time = datetime.now()

    GENERATIONS = 20
    CHROMOSOME_LENGTH = SimpleAgent.CHROMOSOME_LENGTH
    POP_SIZE = 8          # Aim for an even number (see crossover)
    POPULATION = []

    MUTATION_CHANCE = 0.1
    CROSSOVER_CHANCE = 0.8

    best_strategy = None
    best_score = 0
    gen_chance = 0

    for i in range(POP_SIZE):
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
        logger.info(f"Current generation: {gen:<2} with population:")

        for i in POPULATION:
            logger.info(i)
        for i in POPULATION:
            logger.info(SimpleAgent.str_strategy(i))

        scores = {}
        for i, idv in enumerate(POPULATION):
            scores[f"{i}-" + "".join(idv)] = 0

        for i, strategyA in enumerate(POPULATION):
            for j, strategyB in enumerate(POPULATION):

                # print(f"[ GA ] Evaluating strategies {i} vs {j}")
                logger.info(f"Evaluating strategies {i} vs {j}.")

                gm = GameMaster(seed=None)
                gm.playerA.set_strategy(strategyA)
                gm.playerB.set_strategy(strategyB)


                gm.run(rounds=1, training=True)
                # Based of the number of rounds * 2 (maximum score for a win)
                # The lowest is number of rounds * -2 (when all rounds end in too many iterations)
                maximum_score = 2 * 1

                indexA = f"{i}-" + "".join(strategyA)
                indexB = f"{j}-" + "".join(strategyB)

                # Cap it between [-1, 1]
                scores[indexA] += gm.playerA.individual_score / maximum_score
                scores[indexB] += gm.playerB.individual_score / maximum_score

                # for result, iterations, in gm.results:
                #     if result == gm.WIN_A:
                #         scores[indexA] += 1 / iterations
                #     elif result == gm.WIN_B:
                #         scores[indexB] += 1 / iterations
                #     else:
                #         # If they DRAW because the maximum iteration count was reached, the score
                #         # is increased by a very small number, which is negligable.
                #         scores[indexA] += 1 / iterations
                #         scores[indexB] += 1 / iterations

                if gm.state == GameMaster.QUIT:
                    exit()

                # for e, result in enumerate(gm.results):
                #     state, _ = result
                #     if state == GameMaster.WIN_A:
                #         print(f"[ GA ][ Round {e+1:<2} ] A won.")
                #     elif state == GameMaster.WIN_B:
                #         print(f"[ GA ][ Round {e+1:<2} ] B won.")
                #     elif state == GameMaster.DRAW:
                #         print(f"[ GA ][ Round {e+1:<2} ] Draw.")
                #     else:
                #         raise ValueError(f"What kind of state <{type(state)}> with value <{state}> did you append in round {e}?")
                    
        sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1]))
        print("[ GA ] Scores:")
        logger.info("Scores:")
        total_score = 0
        for key, value in sorted_scores.items():
            print(f"{key}: {value}")
            logger.info(f"{key}: {value}")
            total_score += value

        print(f"[ GA ] Total score for this population: {total_score}")

        best_individual_index = max(scores, key=scores.get)
        best_individual_score = scores[best_individual_index]
        best_individual = best_individual_index.split("-")[1]
        print(f"[ GA ] Best individual strategy (for this game): {best_individual}")
        print(f"[ GA ] Best individual score (for this game): {best_individual_score}")

        if best_score < best_individual_score:
            best_score = best_individual_score
            best_strategy = best_individual
            gen_chance = gen
            print(f"[ GA ] New best overall individual found <{best_individual}> with score {best_score}!")
            logger.info(f"New best overall individual found <{best_individual}> with score {best_score}!")
            

        total_fitness = sum(sorted_scores.values())
        probabilities = [f / total_fitness for f in sorted_scores.values()]

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
        
        if len(new_pop) != len(POPULATION):
            print(*new_pop, sep="\n")
            raise RuntimeError(f"how did you??")
        POPULATION = new_pop


    print(f"[ GA ] Best strategy (overall): {best_strategy}")
    print(f"[ GA ] Best score (overall): {best_score}")
    print(f"[ GA ] Set in generation: {gen_chance}")

    logger.info(f"Best strategy (overall): {best_strategy}")
    logger.info(f"Best score (overall): {best_score}")
    logger.info(f"Set in generation: {gen_chance}")

    end_time = datetime.now()

    print(f"Started at {start_time}.")
    print(f"Ended at {end_time}.")

    logger.info(f"Started at {start_time}.")
    logger.info(f"Ended at {end_time}.")
