import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Conv2DTranspose, Reshape, Conv2D, BatchNormalization, Activation
import keras.backend as K

def squared_relu(x):
    return K.relu(x) ** 2

def build_grayscale():
    '''
    Builds a generator that creates grayscale images.
    '''
    model = Sequential()

    # Latent space of 100
    model.add(Dense(256, input_shape=(100,)))
    model.add(BatchNormalization(momentum=0.9))
    model.add(Activation(squared_relu))
    
    model.add(Dense(256))
    model.add(BatchNormalization(momentum=0.9))
    model.add(Activation(squared_relu))

    model.add(Dense(256))
    model.add(BatchNormalization(momentum=0.9))
    model.add(Activation(squared_relu))
    
    model.add(Reshape((16, 16, 1)))

    model.add(Conv2DTranspose(filters=64, kernel_size=(3, 3), strides=(2, 2), padding='same'))
    model.add(BatchNormalization(momentum=0.9))
    model.add(Activation(squared_relu))

    model.add(Conv2DTranspose(filters=32, kernel_size=(3, 3), strides=(2, 2), padding='same'))
    model.add(BatchNormalization(momentum=0.9))
    model.add(Activation(squared_relu))

    model.add(Conv2DTranspose(filters=1, kernel_size=(3, 3), strides=(1, 1), padding='same'))
    model.add(BatchNormalization(momentum=0.9))
    model.add(Activation(squared_relu))

    # model.add(Conv2DTranspose(filters=32, kernel_size=(3, 3), strides=(2, 2), padding='same', activation='relu'))
    # model.add(LeakyReLU(0.2))
    # model.add(Conv2DTranspose(filters=16, kernel_size=(3, 3), strides=(1, 1), padding='same'))
    # model.add(LeakyReLU(0.2))

    # model.add(Conv2D(filters=1, kernel_size=(3, 3), padding='same'))

    # Output shape of (64, 64, 1)
    return model

def build_data_maze():
    '''
    Builds a generator that creates a data maze (64x64 matrix with each cell corresponding to something)
    '''

if __name__ == '__main__':
    model = build_grayscale()

    model.summary()