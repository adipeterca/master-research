from keras.layers import Conv2D, Dense, Flatten, MaxPooling2D, Dropout, Activation, Reshape, Conv1D, MaxPooling1D, LeakyReLU
from keras.models import Sequential
from keras.optimizers import Adam

def build_v(version = 'v2.0.1') -> Sequential:
    '''
    Official method for creating the discriminator, version v2.0 of the program.
    Returns None if the version does not exist.

    @version: which version of the discriminator to use. 
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
    
    raise ValueError(f'Discriminator version "{version}" does not exist!')

def v2_0_0():
    '''
    Only for testing purposes.
    '''

    model = Sequential(name='v2.0.0.D')

    model.add(Dense(1, input_shape=(4096,)))
    model.add(Activation('sigmoid'))

    model.compile(optimizer='adam', metrics=['accuracy'], loss='binary_crossentropy')
    return model

def v2_0_1():
    model = Sequential(name='v2.0.1.D')

    model.add(Dense(100, input_shape=(4096,)))
    model.add(Activation('sigmoid'))
    model.add(Dropout(0.3))

    model.add(Dense(64))
    model.add(Activation('sigmoid'))
    model.add(Dropout(0.4))

    model.add(Dense(32))
    model.add(Activation('sigmoid'))
    model.add(Dropout(0.5))

    model.add(Dense(16))
    model.add(Activation('sigmoid'))
    model.add(Dropout(0.6))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(optimizer='adam', metrics=['accuracy'], loss='binary_crossentropy')
    return model

def v2_0_2():
    model = Sequential(name='v2.0.2.D')

    model.add(Dense(100, input_shape=(4096,)))
    model.add(Activation('relu'))
    model.add(Dropout(0.3))

    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.4))

    model.add(Dense(32))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))

    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dropout(0.6))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(optimizer='adam', metrics=['accuracy'], loss='binary_crossentropy')
    return model

def v2_1_1():
    model = Sequential(name='v2.1.1.D')

    model.add(Reshape((64, 64, 1), input_shape=(4096,)))

    model.add(Conv2D(256, kernel_size=(3, 3), strides=(1, 1), padding='same'))
    model.add(MaxPooling2D())
    model.add(Activation('relu'))

    model.add(Conv2D(128, kernel_size=(3, 3), strides=(1, 1), padding='same'))
    model.add(MaxPooling2D())
    model.add(Activation('relu'))

    model.add(Conv2D(64, kernel_size=(3, 3), strides=(1, 1), padding='same'))
    model.add(MaxPooling2D())
    model.add(Activation('relu'))

    model.add(Conv2D(32, kernel_size=(3, 3), strides=(1, 1), padding='same'))
    model.add(MaxPooling2D())
    model.add(Activation('relu'))

    model.add(Conv2D(32, kernel_size=(3, 3), strides=(1, 1), padding='same'))
    model.add(MaxPooling2D())
    model.add(Activation('relu'))

    model.add(Flatten())

    model.add(Dense(256))
    model.add(Activation('relu'))
    model.add(Dropout(0.4))

    model.add(Dense(128))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))

    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.6))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(optimizer='adam', metrics=['accuracy'], loss='binary_crossentropy')
    return model

def v2_1_2():
    model = Sequential(name='v2.1.2.D')

    # Downsample to 32x32x64
    model.add(Conv1D(64, (4), strides=(2), padding='same', input_shape=(4096, 1)))
    model.add(LeakyReLU(alpha=0.2))

    # Downsample to 16x16x64
    model.add(Conv1D(64, (4), strides=(2), padding='same', input_shape=(4096, 1)))
    model.add(LeakyReLU(alpha=0.2))

    # Downsample to 8x8x64
    model.add(Conv1D(64, (4), strides=(2), padding='same', input_shape=(4096, 1)))
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
