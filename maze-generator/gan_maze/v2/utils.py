import numpy as np
import signal
import os

from keras.models import Sequential
from matplotlib import pyplot

from logger import console
from amazed.modules.maze import Maze
import gans as GAN

# Global variables

# Path to the current test folder in which generators and photos are saved.
RUN_FOLDER = None

# The current configuration for generators & discriminator
RUN_CONFIG = None

# Variable used to store the last trained model for training back-up.
LAST_TRAINED_MODEL = None

# Can add support for the following:
# LAST_TRAINED_EPOCH = 
# TOTAL_BATCHES = 
# TOTAL_EPOCHS = 


def signal_handler(sig, frame):
    global LAST_TRAINED_MODEL

    console.warning('Received CTRL+C signal. Aborting training...\n\n')

    console.warning('Pulling last trained model to save to disk...')
    gan = LAST_TRAINED_MODEL
    if not isinstance(gan, Sequential):
        console.error(f'Saved GAN is not a Sequential object, rather a {type(gan)}')
    else:
        gan.save(f'{RUN_FOLDER}/interupted_model.h5')
    
    exit()

signal.signal(signal.SIGINT, signal_handler)



def load_dataset(path='dataset_1000_hk.npz') -> np.ndarray:
    '''
    Loads the training dataset based on the provided folder.
    All training datasets must be saved using NumPy and indexed using the "data" key for the dictionary.
    '''
    
    d = np.load('datasets/' + path)['data']
    return d

def create_dataset(func, name='hk', size=1000):
    '''
    Function for dataset creation.
    '''
    d = np.zeros((size, 4096,))
    for i in range(size):
        m = Maze(64, 64)
        func(m)
        d[i:] = m.array()
        print(f'Added maze with ID {i}')
    np.savez_compressed(f'dataset_{size}_{name}.npz', data=d)


def create_run_folder():

    global RUN_FOLDER

    console.debug('Creating new RUN FOLDER...')

    current_test_version = 1
    while os.path.exists(f'RUN_{current_test_version}'):
        current_test_version += 1
    
    RUN_FOLDER = f'RUN_{current_test_version}'

    os.mkdir(RUN_FOLDER)

    console.debug(f'Created RUN FOLDER {RUN_FOLDER}')

def create_run_config(gen_name, disc_name):
    
    global RUN_FOLDER
    global RUN_CONFIG

    console.debug('Creating new CONFIG FOLDER...')

    RUN_CONFIG = f'{gen_name}_{disc_name}'

    os.mkdir(f'{RUN_FOLDER}/{RUN_CONFIG}')

    console.debug(f'Created CONFIG FOLDER {RUN_FOLDER}/{RUN_CONFIG}')


def create_plot(d_loss_fake, d_loss_real, gan_loss, d_acc_fake, d_acc_real):
    
    # First plot the losses
    pyplot.subplot(2, 2, 1)
    pyplot.plot(d_loss_fake, label='d-loss-fake')
    pyplot.plot(d_loss_real, label='d-loss-real')
    pyplot.plot(gan_loss, label='gan-loss')
    pyplot.legend()

    # Then plot the accuracies
    pyplot.subplot(2, 1, 2)
    pyplot.plot(d_acc_fake, label='d-acc-fake')
    pyplot.plot(d_acc_real, label='d-acc-real')
    pyplot.legend()

    pyplot.suptitle(RUN_CONFIG)
    pyplot.savefig(f'{RUN_FOLDER}/{RUN_CONFIG}/history_plot.png')
    pyplot.close()


def scale_output(generator : Sequential) -> np.ndarray:
    _input = GAN.generate_latent_space(100, 1)

    output = generator.predict(_input, verbose=0)

    # # Sigmoid
    # output = (output * 15).astype(int)
    
    # Tanh
    output = np.round((output + 1) * 7.5)


    output = output.reshape((64, 64))
    
    return output