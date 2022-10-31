import numpy as np
import pickle
import gzip

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get(_set, index):
    '''
    Return input array, value to expect
    '''
    return _set[0][index], _set[1][index]


with gzip.open('mnist.pkl.gz', 'rb') as fin:
    train_set, valid_set, test_set = pickle.load(fin, encoding='latin')

    rng_state = np.random.get_state()
    np.random.shuffle(train_set[0])
    np.random.set_state(rng_state)
    np.random.shuffle(train_set[1])
    
    rng_state = np.random.get_state()
    np.random.shuffle(valid_set[0])
    np.random.set_state(rng_state)
    np.random.shuffle(valid_set[1])
    

img_width = 28
img_height = 28