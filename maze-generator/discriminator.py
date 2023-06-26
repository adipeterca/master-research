import numpy as np
from keras.layers import Conv2D, Dense, Flatten, MaxPooling2D, Dropout
from keras.models import Sequential, load_model
import maze_dataset as md
import cv2
import os

def build_binary():
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

def build_nary():
    '''
    Build a model capable of discriminating between multiple types of mazez
    '''

def test():

    model = load_model('discriminator.h5')

    for file in os.listdir(f'test_dataset/'):
        img = cv2.imread(f'test_dataset/{file}', cv2.IMREAD_GRAYSCALE)
        img = np.expand_dims(img, axis=0)
        img = np.expand_dims(img, axis=-1)

        output = model(img).numpy()[0, 0]
        print(f'File {file} {"is" if output > 0.5 else "is not"} a maze!')

def train():
    (x_train, y_train), (x_test, y_test) = md.load_dataset()

    model = build_binary()

    model.fit(x_train, y_train, batch_size=16, epochs=5)
    model.evaluate(x_test, y_test)

    model.save('discriminator.h5')


if __name__ == '__main__':

    # train()
    test()