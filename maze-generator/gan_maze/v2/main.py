import os

from keras.models import load_model

import gans as GAN
import generators as G
import discriminators as D

from amazed.modules.maze import Maze

import utils

def generate_test_images(epochs):
    '''
    Used to generate images by loading the created generators from RUN_FOLDER/RUN_CONFIG.
    The generators must be saved under "generator_epoch_EPOCH.h5", where EPOCH is a number.
    '''
    for gen_i in range(1, epochs+1):
        gen_path = f'{utils.RUN_FOLDER}/{utils.RUN_CONFIG}/generator_epoch_{gen_i}.h5'
        if not os.path.exists(gen_path):
            utils.console.warning(f'Did not find generator at path {gen_path}')
            continue
        
        utils.console.info(f'Loaded generator from path {gen_path}')
        created_gen = load_model(gen_path)

        for i in range(3):
            scaled_output = utils.scale_output(created_gen)

            maze = Maze.build_from_array(scaled_output, 64, 64)
            maze.export(
                output=f'{utils.RUN_FOLDER}/{utils.RUN_CONFIG}/epoch_{gen_i}.{i}.png',
                show=False
            )

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

    settings["epochs"] = 25
    settings["batch_size"] = 32
    settings["save_step"] = 5

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

            generate_test_images(settings["epochs"])
            utils.console.info('Finished generating test photos')

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
        'v2.4.0'
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
        'v2.3.7',
        'v2.3.8'
    ]

    # gans_testing(available_generators, available_discriminators)

    from amazed.modules.build import hunt_and_kill
    from amazed.modules.solver import DFS

    m = Maze(50, 50)
    hunt_and_kill(m)

    d = DFS(m)
    d.solve()
    d.gif("tmp/maze.gif")
    d.image("tmp/maze.png")

