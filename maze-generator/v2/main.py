import os

from keras.models import load_model

import gans as GAN
import generators as G
import discriminators as D

from amazed.modules.maze import Maze

import utils

def gans_testing(available_generators : list, available_discriminators : list):
    '''
    Main method for cross-validation and testing of various GAN builds.
    For now, the following are static:
    -> dataset
    -> epochs
    -> batch_size

    @available_generators : a list of various build versions for generators
    @available_discriminators : a list of various build versions for discriminators
    '''

    utils.console.debug('Initiating GAN testing...')
    if len(available_generators) == 0:
        raise ValueError('No generators found in the provided list!')
    if len(available_discriminators) == 0:
        raise ValueError('No discriminators found in the provided list!')

    utils.create_run_folder()

    settings = {}

    # Written like this so future me can modify it easily
    dataset_size = 10000
    dataset_type = 'hk'

    utils.console.debug(f'Loading dataset dataset_{dataset_size}_{dataset_type}.npz')
    settings["dataset"] = utils.load_dataset(f'dataset_{dataset_size}_{dataset_type}.npz')
    utils.console.debug('Dataset loaded successfully!')

    settings["latent_dim_size"] = 100

    settings["epochs"] = 250
    settings["batch_size"] = 32
    settings["save_step"] = 50

    settings["disc_train_times"] = 5
    settings["gen_train_times"] = 2
    
    if settings["save_step"] > 0:
        utils.console.warning('Intermediate saving: ON')
    else:
        utils.console.warning('Intermediate saving: OFF')

    utils.console.info('Starting training...')

    for gen_ver in available_generators:
        for disc_ver in available_discriminators:

            # Both the generator and the discriminator need to be built at each step.
            gen = G.build_v(gen_ver)
            assert gen.name.startswith('v2')
            utils.console.info(f'Training using GENERATOR version {gen.name}')


            disc = D.build_v(disc_ver)
            assert disc.name.startswith('v2')
            utils.console.info(f'Training using DISCRIMINATOR version {disc.name}')

            utils.create_run_config(gen.name, disc.name)

            GAN.train(
                generator=gen, discriminator=disc, 
                settings=settings
            )

            utils.console.info('Finished training.')
            

if __name__ == '__main__':

    available_generators = [
        # 'v2.1.0',
        # 'v2.2.0',
        # 'v2.3.0',
        # 'v2.3.1',
        # 'v2.3.2',
        # 'v2.3.3',
        # 'v2.3.4',
        'v2.4.1',
        # 'v2.4.0'
    ]

    available_discriminators = [
        # 'v2.1.0',
        # 'v2.2.0',
        # 'v2.3.0',
        # 'v2.3.1',
        # 'v2.3.2',
        # 'v2.3.3',
        # 'v2.3.4',
        # 'v2.3.5',
        'v2.3.6',
        # 'v2.3.7',
        # 'v2.3.8'
    ]

    # gans_testing(available_generators, available_discriminators)

    
    from amazed.modules.build import hunt_and_kill
    from amazed.modules.build import binary_tree
    from amazed.modules.build import random_kruskal
    from amazed.modules.build import random_carving
    from amazed.modules.solver import DFSRandom
    from amazed.modules.solver import DFS
    from amazed.modules.solver import AStar
    from amazed.modules.solver import Lee
    import time

    # m = Maze(50, 50)
    # random_carving(m, original_chance=0.95, multicell=False, adaptive=False)
    # random_carving(m, original_chance=0.65, multicell=False, adaptive=False)
    # random_carving(m, original_chance=0.35, multicell=False, adaptive=False)
    # hunt_and_kill(m)
    # # random_kruskal(m)
    # # binary_tree(m)

    # m.export(output="./tmp/maze.png", show=False)
    
    m = Maze(64, 64)
    hunt_and_kill(m)
    random_carving(m, 0.001)
    # binary_tree(m)
    m.export(output="./tmp/maze.png", show=False)

    a = AStar(m)
    start = time.time_ns()
    a.solve()
    a.image("tmp/astar.png")
    total = (time.time_ns() - start)
    print(f"Miliseconds to solve: {total} s")

    a = DFS(m)
    start = time.time_ns()
    a.solve()
    a.image("tmp/dfs.png")
    total = (time.time_ns() - start)
    print(f"Miliseconds to solve: {total} s")

    a = DFSRandom(m)
    start = time.time_ns()
    a.solve()
    a.image("tmp/dfsrandom.png")
    total = (time.time_ns() - start)
    print(f"Miliseconds to solve: {total} s")




    
    exit()
    # a.gif("tmp/lee.gif")

    # a = DFSRandom(m)
    a = DFS(m)
    a.solve()
    a.image("tmp/dfs_random_1.png")
    # a.gif("tmp/dfs_random_1.gif")
    # print("Done with DFS random")
    # a = DFSRandom(m)
    # a.solve()
    # a.image("tmp/dfs_random_2.png")
    # print("Done with DFS random")
    # a = DFSRandom(m)
    # a.solve()
    # a.image("tmp/dfs_random_3.png")
    # print("Done with DFS random")