import generator
import discriminator
import numpy as np
from keras.models import Sequential
from keras.optimizers import Adam

gen = generator.build_model()
disc = discriminator.build_model()
disc.trainable = False

model = Sequential()
model.add(gen)
model.add(disc)
model.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.0002, beta_2=0.5), metrics=['accuracy'])