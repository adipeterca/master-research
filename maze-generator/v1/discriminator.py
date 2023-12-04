from keras.layers import Conv2D, Dense, Flatten, MaxPooling2D, Dropout
from keras.models import Sequential

def build_binary():
    '''
    Deprecated method for building a descriminating model.
    '''
    model = Sequential()

    model.add(Conv2D(filters=32, kernel_size=(3, 3), strides=1, padding='same', input_shape=(64, 64, 1)))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=2)) # 32, 32, 32
    model.add(Dropout(0.3))

    model.add(Conv2D(filters=16, kernel_size=(3, 3), strides=1, padding='same'))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=2)) # 16, 16, 16
    model.add(Dropout(0.3))

    model.add(Conv2D(filters=8, kernel_size=(3, 3), strides=1, padding='same'))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=2)) # 8, 8, 8
    model.add(Dropout(0.3))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='adam', metrics=['accuracy'], loss='binary_crossentropy')

    return model