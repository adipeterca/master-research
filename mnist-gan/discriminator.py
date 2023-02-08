# Creates a discriminator for MNIST dataset

import numpy as np
from keras.datasets import mnist
from keras.layers import Dense, Conv2D, LeakyReLU, Dropout, Flatten
from keras.models import Sequential
from keras.optimizers import Adam

def build_model():
    model = Sequential()
    model.add(Conv2D(filters=64, kernel_size=(3, 3), strides=(2, 2), padding='same', input_shape=(28, 28, 1)))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dropout(0.4))
    model.add(Conv2D(filters=64, kernel_size=(3, 3), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))
    model.add(Dropout(0.4))
    model.add(Flatten())
    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.002, beta_1=0.5), metrics=['accuracy'])
    model.summary()
    return model


# We only use input images (60.000)
(x_real, _), (_, _) = mnist.load_data()
x_real = x_real / 255
y_real = np.ones(shape=(len(x_real), 1))

x_fake = np.random.random(size=(len(x_real), 28, 28))
y_fake = np.zeros(shape=(len(x_real), 1))

x_train = np.concatenate((x_real, x_fake), axis=0)
y_train = np.concatenate((y_real, y_fake), axis=0)

x_test = x_train[-10_000:]
y_test = y_train[-10_000:]
x_train = x_train[:-10_000]
y_train = y_train[:-10_000]

model = build_model()
model.fit(x_train, y_train, batch_size=64, epochs=2, validation_data=(x_test, y_test))

_, acc = model.evaluate(x_test, y_test)
model.save('model.h5')
print(acc)