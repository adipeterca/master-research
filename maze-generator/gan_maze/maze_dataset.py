import os
import numpy as np
import cv2

def load_dataset(shuffle=True):
    '''
    Only loads the hunt_and_kill dataset (for now!)
    '''

    x = np.empty(shape=(20000, 64, 64))
    y = np.concatenate((np.ones(shape=(10000, 1)), np.zeros(shape=(10000, 1))))

    for i, file in enumerate(os.listdir('dataset/hunt_and_kill')):
        img = cv2.imread(f'dataset/hunt_and_kill/{file}', cv2.IMREAD_GRAYSCALE)
        x[i] = img
    for i, file in enumerate(os.listdir('dataset/no_maze')):
        img = cv2.imread(f'dataset/no_maze/{file}', cv2.IMREAD_GRAYSCALE)
        x[10000+i] = img

    x = np.expand_dims(x, axis=-1)

    if shuffle:
        permutation = np.random.permutation(len(x))
        x = x[permutation]
        y = y[permutation]
        

    x_train = x[:int(len(x)*0.9)]
    y_train = y[:int(len(y)*0.9)]

    x_test = x[int(len(x)*0.9):]
    y_test = y[int(len(y)*0.9):]

    return (x_train, y_train), (x_test, y_test)