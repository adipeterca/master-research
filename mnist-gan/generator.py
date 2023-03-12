import numpy as np
from keras.layers import Dense, Conv2D, LeakyReLU, Dropout, Flatten, UpSampling2D, Reshape, Conv2DTranspose, Input
from keras.models import Sequential
from keras.optimizers import Adam

def build_model():
    model = Sequential()
    # Input: a vector of size (N, 1) with random values from the latent space
    # Output: a vector of size (28, 28, 1) with values between [0, 1]

    # Adding 128 7x7 "feature maps" of the input
    model.add(Dense(128 * 7 * 7, input_dim=100)) # Why not input_dim=(100, 1)? -> asa asteapa keras
    model.add(LeakyReLU(alpha=0.2))
    model.add(Reshape((7, 7, 128)))

    # Upsample to 14x14
    model.add(Conv2DTranspose(128, kernel_size=(4, 4), strides=(2, 2), padding='same')) # Why not kernel_size=(1, 1)
    model.add(LeakyReLU(alpha=0.2))

    # Upsample to 28x28
    model.add(Conv2DTranspose(128, kernel_size=(4, 4), strides=(2, 2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Conv2D(filters=1, kernel_size=(7, 7), activation='sigmoid', padding='same')) # why kernel_size=(7, 7)

    # model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model
