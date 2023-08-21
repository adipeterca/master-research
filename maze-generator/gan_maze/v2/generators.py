from keras.models import Sequential
from keras.layers import Dense, Conv2DTranspose, Reshape, Conv2D, BatchNormalization, Activation, Conv1DTranspose, UpSampling1D, LeakyReLU
from keras.initializers import RandomNormal

def build_v(version = 'v2.0.1') -> Sequential:
    '''
    Official method for creating the generator, version v2.0 of the program.
    Returns None if the version does not exist.

    @version: which version of the generator to use. 
    '''
    if version == 'v2.0.0':
        return v2_0_0()
    if version == 'v2.0.1':
        return v2_0_1()
    if version == 'v2.0.2':
        return v2_0_2()
    if version == 'v2.1.1':
        return v2_1_1()
    if version == 'v2.1.2':
        return v2_1_2()
    if version == 'v2.1.3':
        return v2_1_3()
    
    raise ValueError(f'Generator version "{version}" does not exist!')

def v2_0_0():
    '''
    Only for testing purposes.
    '''

    model = Sequential(name='v2.0.0.G')

    model.add(Dense(4096, input_shape=(100,)))
    model.add(Activation('sigmoid'))
    
    return model

def v2_0_1():
    '''
    Fully connected neural networn, without other layer types.
    '''
    
    model = Sequential(name='v2.0.1.G')

    model.add(Dense(128, input_shape=(100,)))
    model.add(Activation('sigmoid'))

    model.add(Dense(256))
    model.add(Activation('sigmoid'))
    
    model.add(Dense(512))
    model.add(Activation('sigmoid'))

    model.add(Dense(512))
    model.add(Activation('sigmoid'))

    model.add(Reshape((512, 1)))
    model.add(UpSampling1D(size=8))

    return model

def v2_0_2():
    '''
    Fully connected neural network, without other layer types.
    '''
    
    model = Sequential(name='v2.0.2.G')

    model.add(Dense(128, input_shape=(100,), kernel_initializer=RandomNormal(mean=0.5, stddev=0.05, seed=None)))
    model.add(Activation('sigmoid'))

    model.add(Dense(128))
    model.add(Activation('sigmoid'))

    model.add(Dense(128))
    model.add(Activation('sigmoid'))

    model.add(Dense(128))
    model.add(Activation('sigmoid'))

    model.add(Dense(128))
    model.add(Activation('sigmoid'))

    model.add(Dense(128))
    model.add(Activation('sigmoid'))

    model.add(Dense(128))
    model.add(Activation('sigmoid'))

    model.add(Dense(128))
    model.add(Activation('sigmoid'))

    model.add(Dense(128))
    model.add(Activation('sigmoid'))

    model.add(Dense(128))
    model.add(Activation('sigmoid'))

    model.add(Dense(128))
    model.add(Activation('sigmoid'))

    model.add(Dense(256))
    model.add(Activation('sigmoid'))

    model.add(Reshape((256, 1)))
    
    model.add(UpSampling1D(size=16))
    # model.add(Activation('sigmoid'))

    # model.add(UpSampling1D(size=4))
    # model.add(Activation('sigmoid'))

    return model


def v2_1_1():
    model = Sequential(name='v2.1.1.G')

    model.add(Dense(128, input_shape=(100,)))
    model.add(Activation('sigmoid'))

    model.add(Dense(128))
    model.add(Activation('sigmoid'))
    
    model.add(Dense(256))
    model.add(Activation('sigmoid'))

    model.add(Dense(256))
    model.add(Activation('sigmoid'))

    model.add(Reshape((16, 16, 1)))

    model.add(Conv2DTranspose(filters=128, kernel_size=2, strides=1, padding='same'))
    model.add(Activation('sigmoid'))

    model.add(Conv2DTranspose(filters=64, kernel_size=2, strides=1, padding='same'))
    model.add(Activation('sigmoid'))

    model.add(Conv2DTranspose(filters=32, kernel_size=2, strides=1, padding='same'))
    model.add(Activation('sigmoid'))
    
    model.add(Conv2DTranspose(filters=16, kernel_size=2, strides=1, padding='same'))
    model.add(Activation('sigmoid'))

    model.add(Reshape((4096, 1)))

    return model

def v2_1_2():
    model = Sequential(name='v2.1.2.G')

    model.add(Dense(128, input_shape=(100,)))
    model.add(Activation('relu'))

    model.add(Dense(256))
    model.add(Activation('relu'))
    
    model.add(Dense(256))
    model.add(Activation('relu'))
    
    model.add(Dense(256))
    model.add(Activation('relu'))
    
    model.add(Dense(256))
    model.add(Activation('relu'))

    model.add(Dense(256))
    model.add(Activation('relu'))

    model.add(Reshape((16, 16, 1)))

    model.add(Conv2DTranspose(filters=128, kernel_size=2, strides=1, padding='same'))
    model.add(Activation('relu'))

    model.add(Conv2DTranspose(filters=64, kernel_size=2, strides=1, padding='same'))
    model.add(Activation('relu'))

    model.add(Conv2DTranspose(filters=32, kernel_size=2, strides=1, padding='same'))
    model.add(Activation('relu'))
    
    model.add(Conv2DTranspose(filters=16, kernel_size=2, strides=1, padding='same'))
    model.add(Activation('sigmoid'))

    model.add(Reshape((4096, 1)))

    return model

def v2_1_3():
    '''
    Complex model with over 1.000.000 parameters.
    '''

    model = Sequential(name='v2.1.3.G')

    model.add(Dense(16*16*64, input_shape=(100,)))
    model.add(LeakyReLU(alpha=0.9))
    # model.add(Activation('sigmoid'))
    model.add(Reshape((16, 16, 64)))

    # Upsample to 32x32x64
    model.add(Conv2DTranspose(64, (4, 4), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.9))
    # model.add(Activation('sigmoid'))

    # Upsample to 64x64x64
    model.add(Conv2DTranspose(64, (4, 4), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.9))
    # model.add(Activation('sigmoid'))

    model.add(Conv2D(1, (16, 16), padding='same'))
    model.add(Activation('sigmoid'))

    model.add(Reshape((4096, 1)))
    return model

if __name__ == '__main__':
    import sys
    import gans as GAN
    import numpy as np

    from maze_building.modules.maze import Maze
    from logger import console

    np.set_printoptions(linewidth=np.inf, threshold=np.inf)

    console.info('Running in GENERATOR TESTING mode.')

    version = sys.argv[1]
    console.info(f'Version: {version}')

    gen = build_v(version)
    _input = GAN.generate_latent_space(100, 1)
    output = gen.predict(_input, verbose=0)
    output = output.reshape((64, 64))

    console.info('\n\nOutput before scaling')
    print(output)

    output = (output * 15).astype(int)
    console.info('\n\nOutput after scaling')
    print(output)

    maze = Maze.build_from_array(output, 64, 64)
    maze.export()