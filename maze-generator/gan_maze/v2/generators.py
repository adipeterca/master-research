from keras.models import Sequential, load_model
from keras.layers import Dense, Conv2DTranspose, Reshape, Conv2D, BatchNormalization, Activation, Conv1DTranspose, UpSampling1D, LeakyReLU, Conv1D, Dropout
from keras.initializers import RandomUniform, RandomNormal, GlorotUniform
import random

def build_v(version = 'v2.0.1') -> Sequential:
    '''
    Official method for creating the generator, version v2.0 of the program.
    Returns None if the version does not exist.

    @version: which version of the generator to use. 
    '''
    if version == 'v2.0.0':
        return v2_0_0()
    if version == 'v2.1.0':
        return v2_1_0()
    if version == 'v2.2.0':
        return v2_2_0()
    if version == 'v2.3.0':
        return v2_3_0()
    if version == 'v2.3.1':
        return v2_3_1()
    if version == 'v2.3.2':
        return v2_3_2()
    if version == 'v2.3.3':
        return v2_3_3()
    if version == 'v2.3.4':
        return v2_3_4()
    if version == 'v2.4.0':
        return v2_4_0()
    if version == 'v2.4.1':
        return v2_4_1()
    
    raise ValueError(f'Generator version "{version}" does not exist!')

def v2_4_1():

    model = Sequential(name='v2.4.1.G')

    model.add(Dense(4 * 4 * 256, input_shape=(100,)))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.9))

    model.add(Reshape((4, 4, 256)))

    model.add(Conv2DTranspose(256, kernel_size=(8, 8), strides=(1, 1), padding='same'))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.9))

    model.add(Conv2DTranspose(128, kernel_size=(4, 4), strides=(2, 2), padding='same'))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.9))

    model.add(Conv2DTranspose(64, kernel_size=(4, 4), strides=(2, 2), padding='same'))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.9))

    model.add(Conv2DTranspose(32, kernel_size=(4, 4), strides=(2, 2), padding='same'))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.9))

    model.add(Conv2DTranspose(1, kernel_size=(8, 8), strides=(2, 2), padding='same'))
    model.add(Activation('tanh'))

    model.add(Reshape((4096, 1)))

    return model

def v2_4_0():
    '''
    This model will make use of 2D convolutions, based on the idea that
    a maze is built not only by looking at each individual cell, but also
    at the surrounding area.
    '''

    model = Sequential(name='v2.4.0.G')

    model.add(Dense(4 * 4 * 256, input_shape=(100,)))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))

    model.add(Reshape((4, 4, 256)))

    model.add(Conv2DTranspose(256, kernel_size=(8, 8), strides=(1, 1), padding='same'))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))

    model.add(Conv2DTranspose(128, kernel_size=(4, 4), strides=(2, 2), padding='same'))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))

    model.add(Conv2DTranspose(64, kernel_size=(4, 4), strides=(2, 2), padding='same'))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))

    model.add(Conv2DTranspose(32, kernel_size=(4, 4), strides=(2, 2), padding='same'))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))

    model.add(Conv2DTranspose(1, kernel_size=(8, 8), strides=(2, 2), padding='same'))
    model.add(Activation('tanh'))

    model.add(Reshape((4096, 1)))

    return model


def v2_3_4():
    model = Sequential(name='v2.3.4.G')

    init = RandomNormal(stddev=0.02)

    model.add(Dense(128 * 16 * 16, kernel_initializer=init, input_shape=(100, )))

    model.add(Activation('elu'))
    model.add(Dropout(0.4))
    model.add(Reshape((16, 16, 128)))

    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same', kernel_initializer=init))
    model.add(Activation('elu'))
    model.add(Dropout(0.4))
    
    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same', kernel_initializer=init))
    model.add(Activation('elu'))
    model.add(Dropout(0.4))
    
    model.add(Conv2D(1, (16,16), activation='sigmoid', padding='same', kernel_initializer=init))
    model.add(Reshape((4096, 1)))
    return model

def v2_3_3():
    model = Sequential(name='v2.3.3.G')

    init = RandomNormal(stddev=0.02)

    model.add(Dense(128 * 16 * 16, kernel_initializer=init, input_shape=(100, )))

    model.add(Activation('tanh'))
    model.add(Dropout(0.4))
    model.add(Reshape((16, 16, 128)))

    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same', kernel_initializer=init))
    model.add(Activation('tanh'))
    model.add(Dropout(0.4))
    
    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same', kernel_initializer=init))
    model.add(Activation('tanh'))
    model.add(Dropout(0.4))
    
    model.add(Conv2D(1, (16,16), activation='sigmoid', padding='same', kernel_initializer=init))
    model.add(Reshape((4096, 1)))
    return model

def v2_3_2():
    model = Sequential(name='v2.3.2.G')

    init = RandomNormal(stddev=0.02)

    model.add(Dense(128 * 16 * 16, kernel_initializer=init, input_shape=(100, )))

    model.add(Activation('relu'))
    model.add(Dropout(0.4))
    model.add(Reshape((16, 16, 128)))

    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same', kernel_initializer=init))
    model.add(Activation('relu'))
    model.add(Dropout(0.4))
    
    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same', kernel_initializer=init))
    model.add(Activation('relu'))
    model.add(Dropout(0.4))
    
    model.add(Conv2D(1, (16,16), activation='sigmoid', padding='same', kernel_initializer=init))
    model.add(Reshape((4096, 1)))
    return model

def v2_3_1():
    model = Sequential(name='v2.3.1.G')

    init = RandomNormal(stddev=0.02)

    model.add(Dense(128 * 16 * 16, kernel_initializer=init, input_shape=(100, )))

    model.add(Activation('tanh'))
    model.add(Reshape((16, 16, 128)))

    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same', kernel_initializer=init))
    model.add(Activation('tanh'))
    
    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same', kernel_initializer=init))
    model.add(Activation('tanh'))
    
    model.add(Conv2D(1, (16,16), activation='sigmoid', padding='same', kernel_initializer=init))
    model.add(Reshape((4096, 1)))
    return model

def v2_3_0():

    model = Sequential(name='v2.3.0.G')

    init = RandomNormal(stddev=0.02)

    model.add(Dense(128 * 16 * 16, kernel_initializer=init, input_shape=(100, )))

    model.add(LeakyReLU(alpha=0.2))
    model.add(Reshape((16, 16, 128)))

    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same', kernel_initializer=init))
    model.add(LeakyReLU(alpha=0.2))
    
    model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same', kernel_initializer=init))
    model.add(LeakyReLU(alpha=0.2))
    
    model.add(Conv2D(1, (16,16), activation='sigmoid', padding='same', kernel_initializer=init))
    model.add(Reshape((4096, 1)))
    return model

def v2_2_0():
    '''
    Input: (100, 1)
    Output: (4096, 1)
    Total parmas: 1.802.369
    Uses 2D.
    '''

    model = Sequential(name='v2.2.0.G')

    init = RandomUniform(minval=-1, maxval=1)
    # init = GlorotUniform()

    model.add(Dense(16*16*256, kernel_initializer=init, input_shape=(100,)))
    model.add(Activation('tanh'))
    model.add(Reshape((16, 16, 256)))

    # Upsample to 32x32x64
    model.add(Conv2DTranspose(64, (4, 4), strides=(2, 2), padding='same'))
    # model.add(Activation('tanh'))

    # Upsample to 64x64x64
    model.add(Conv2DTranspose(64, (4, 4), strides=(2, 2), padding='same'))
    # model.add(Activation('tanh'))

    model.add(Conv2D(1, (16, 16), padding='same'))
    model.add(Activation('sigmoid'))

    model.add(Reshape((4096, 1)))
    return model

def v2_1_0():

    '''
    Input: (100, 1)
    Output: (4096, 1)
    Total param count: 939.905
    Only uses 1D.
    '''

    model = Sequential(name='v2.1.0.G')

    # init = RandomUniform(minval=-0.5, maxval=0.5, seed=random.randint(0, 100))
    # init = RandomNormal(mean=1, stddev=5)

    model.add(Dense(512, kernel_initializer=RandomUniform(minval=-0.5, maxval=0.5, seed=random.randint(0, 100)), input_shape=(100,)))
    # model.add(Activation('elu'))

    model.add(Dense(512, kernel_initializer=RandomUniform(minval=-0.5, maxval=0.5, seed=random.randint(0, 100))))
    # model.add(Activation('elu'))

    model.add(Dense(1024, kernel_initializer=RandomUniform(minval=-0.5, maxval=0.5, seed=random.randint(0, 100))))
    model.add(Activation('tanh'))

    model.add(Reshape((1024, 1)))

    model.add(Conv1DTranspose(128, kernel_size=4, strides=2, padding='same', kernel_initializer=RandomUniform(minval=-0.5, maxval=0.5, seed=random.randint(0, 100))))
    # model.add(Activation('tanh'))

    model.add(Conv1DTranspose(128, kernel_size=4, strides=2, padding='same', kernel_initializer=RandomUniform(minval=-0.5, maxval=0.5, seed=random.randint(0, 100))))
    # model.add(Activation('tanh'))

    model.add(Conv1DTranspose(128, kernel_size=2, strides=1, padding='same', kernel_initializer=RandomUniform(minval=-0.5, maxval=0.5, seed=random.randint(0, 100))))
    model.add(Activation('tanh'))

    model.add(Conv1D(1, 8, padding='same'))
    model.add(Activation('sigmoid'))

    return model

def v2_0_0():
    '''
    Only for testing purposes.
    '''

    model = Sequential(name='v2.0.0.G')

    model.add(Dense(4096, input_shape=(100,)))
    model.add(Activation('sigmoid'))
    
    return model

if __name__ == '__main__':
    import sys
    import numpy as np

    from amazed.modules.maze import Maze
    from logger import console
    import utils

    np.set_printoptions(linewidth=np.inf, threshold=np.inf)

    console.info('Running in GENERATOR TESTING mode.')

    # gen = load_model('v2_test_5/generator_epoch_1.h5')
    # gen = load_model('v2_test_8/interupted_model.h5')

    # version = sys.argv[1]
    # console.info(f'Version: {version}')
    # gen = build_v(version)
    gen = load_model("RUN_2/v2.4.0.G_v2.3.7.D/generator_epoch_5.h5")

    if len(sys.argv) == 3 and sys.argv[2] == 'summary':
        gen.summary()
        exit()

    output = utils.scale_output(gen)

    for i in range(0, 16):
        occ = np.count_nonzero(output == i)
        console.info(f'Value {i :>2} stats: {occ:>5}\t{occ / 4096 * 100:>5.2f} %')        

    maze = Maze.build_from_array(output, 64, 64)
    maze.export()