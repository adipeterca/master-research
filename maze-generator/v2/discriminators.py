from keras.layers import Conv2D, Dense, Flatten, MaxPooling2D, Dropout, Activation, Reshape, Conv1D, MaxPooling1D, LeakyReLU
from keras.models import Sequential
from keras.optimizers import Adam

def build_v(version = 'v2.0.0') -> Sequential:
    '''
    Official method for creating the discriminator, version v2.0 of the program.
    Returns None if the version does not exist.

    @version: which version of the discriminator to use. 
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
    if version == 'v2.3.5':
        return v2_3_5()
    if version == 'v2.3.6':
        return v2_3_6()
    if version == 'v2.3.7':
        return v2_3_7()
    if version == 'v2.3.8':
        return v2_3_8()
    
    raise ValueError(f'Discriminator version "{version}" does not exist!')

def v2_3_8():
    model = Sequential(name='v2.3.8.D')

    model.add(Reshape((64, 64, 1), input_shape=(4096, 1)))

    model.add(Conv2D(64, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(
        optimizer=Adam(learning_rate=0.01, beta_1=0.9), 
        metrics=['accuracy'], 
        loss='binary_crossentropy'
    )
    return model


def v2_3_7():
    model = Sequential(name='v2.3.7.D')

    model.add(Reshape((64, 64, 1), input_shape=(4096, 1)))

    model.add(Conv2D(64, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(
        optimizer=Adam(learning_rate=0.001, beta_1=0.9), 
        metrics=['accuracy'], 
        loss='binary_crossentropy'
    )
    return model

def v2_3_6():
    model = Sequential(name='v2.3.6.D')

    model.add(Reshape((64, 64, 1), input_shape=(4096, 1)))

    model.add(Conv2D(64, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(
        optimizer=Adam(learning_rate=0.0001, beta_1=0.9), 
        metrics=['accuracy'], 
        loss='binary_crossentropy'
    )
    return model

def v2_3_5():
    model = Sequential(name='v2.3.5.D')

    model.add(Reshape((64, 64, 1), input_shape=(4096, 1)))

    model.add(Conv2D(64, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(
        optimizer=Adam(learning_rate=0.01, beta_1=0.5), 
        metrics=['accuracy'], 
        loss='binary_crossentropy'
    )
    return model

def v2_3_4():
    model = Sequential(name='v2.3.4.D')

    model.add(Reshape((64, 64, 1), input_shape=(4096, 1)))

    model.add(Conv2D(64, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(
        optimizer=Adam(learning_rate=0.001, beta_1=0.5), 
        metrics=['accuracy'], 
        loss='binary_crossentropy'
    )
    return model

def v2_3_3():
    model = Sequential(name='v2.3.3.D')

    model.add(Reshape((64, 64, 1), input_shape=(4096, 1)))

    model.add(Conv2D(64, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(
        optimizer=Adam(learning_rate=0.0001, beta_1=0.5), 
        metrics=['accuracy'], 
        loss='binary_crossentropy'
    )
    return model

def v2_3_2():
    model = Sequential(name='v2.3.2.D')

    model.add(Reshape((64, 64, 1), input_shape=(4096, 1)))

    model.add(Conv2D(64, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(
        optimizer=Adam(learning_rate=0.01, beta_1=0.1), 
        metrics=['accuracy'], 
        loss='binary_crossentropy'
    )
    return model

def v2_3_1():
    model = Sequential(name='v2.3.1.D')

    model.add(Reshape((64, 64, 1), input_shape=(4096, 1)))

    model.add(Conv2D(64, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(
        optimizer=Adam(learning_rate=0.001, beta_1=0.1), 
        metrics=['accuracy'], 
        loss='binary_crossentropy'
    )
    return model

def v2_3_0():
    model = Sequential(name='v2.3.0.D')

    model.add(Reshape((64, 64, 1), input_shape=(4096, 1)))

    model.add(Conv2D(64, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(MaxPooling2D((2, 2), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(
        optimizer=Adam(learning_rate=0.0001, beta_1=0.1), 
        metrics=['accuracy'], 
        loss='binary_crossentropy'
    )
    return model

def v2_2_0():
    model = Sequential(name='v2.2.0.D')

    model.add(Reshape((64, 64, 1), input_shape=(4096, 1)))

    model.add(Conv2D(64, kernel_size=4, strides=2, padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(128, kernel_size=4, strides=2, padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Flatten())
    model.add(Dropout(0.2))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(
        optimizer=Adam(learning_rate=0.0002, beta_1=0.5), 
        metrics=['accuracy'], 
        loss='binary_crossentropy'
    )
    return model

def v2_1_0():
    model = Sequential(name='v2.1.0.D')

    # Downsample to 32x32x64
    model.add(Conv1D(64, (4), strides=(2), padding='same', input_shape=(4096, 1)))
    model.add(LeakyReLU(alpha=0.2))

    # Downsample to 16x16x64
    model.add(Conv1D(64, (4), strides=(2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    # Downsample to 8x8x64
    model.add(Conv1D(64, (4), strides=(2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Flatten())
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(
        optimizer=Adam(learning_rate=0.0002, beta_1=0.5), 
        metrics=['accuracy'], 
        loss='binary_crossentropy'
    )
    return model

def v2_0_0():
    '''
    Only for testing purposes.
    '''

    model = Sequential(name='v2.0.0.D')

    model.add(Dense(1, input_shape=(4096,)))
    model.add(Activation('sigmoid'))

    model.compile(optimizer='adam', metrics=['accuracy'], loss='binary_crossentropy')
    return model

if __name__ == "__main__":

    import numpy as np
    import sys

    from logger import console
    from utils import load_dataset

    console.info('Running in DISCRIMINATOR TESTING mode.')

    version = sys.argv[1]
    console.info(f'Version: {version}')
    disc = build_v(version)

    if len(sys.argv) == 3 and sys.argv[2] == 'summary':
        disc.summary()
        exit()


    # Random noise
    true = 0
    for i in range(100):
            
        _input = np.random.random((1, 4096, 1))
        _input = _input * (2*i) - i

        output = disc.predict(_input, verbose=0)
        if output[0, 0] > 0.5:
            true += 1
    console.info(f'[RANDOM NOISE]   Untrained accuracy: {true:>2}% cataloged as MAZES')
    
    # Actual mazes
    true = 0
    dataset = load_dataset()
    for i in range(100):
            
        _input = dataset[i]
        _input = np.expand_dims(_input, axis=-1)
        _input = np.expand_dims(_input, axis=0)
        
        output = disc.predict(_input, verbose=0)
        if output[0, 0] > 0.5:
            true += 1
    console.info(f'[DATASET]        Untrained accuracy: {true:>2}% cataloged as MAZES')
