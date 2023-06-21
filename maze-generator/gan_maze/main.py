import os
import cv2
import random
import numpy as np

from keras.models import Sequential
import keras.backend as K

import discriminator
import generator

np.set_printoptions(threshold=np.inf, linewidth=np.inf)

def build_gan(discriminator : Sequential, generator : Sequential):
    model = Sequential()

    discriminator.trainable = False
    model.add(generator)
    model.add(discriminator)

    model.compile(loss='binary_crossentropy', optimizer='adam')

    return model

def generate_latent_space(latent_dim_size, n_samples):
    return np.random.random(size=(n_samples, latent_dim_size))

def generate_real_samples(real_dataset, n_samples):
    x = random.choices(real_dataset, k=n_samples)
    x = np.array(x)
    x = np.expand_dims(x, axis=-1)
    y = np.ones(shape=(n_samples, 1))

    return x, y

def generate_fake_samples(generator : Sequential, latent_dim_size=100, n_samples=16):
    latent_space = generate_latent_space(latent_dim_size, n_samples)
    
    x = generator.predict(latent_space)
    y = np.zeros(shape=(n_samples, 1))

    return x, y

def train_gan(generator : Sequential, discriminator : Sequential, gan : Sequential, dataset, latent_dim_size=100, epochs=10, batch_size=16):
    '''
    @dataset : Python list of numpy arrays representing images
    '''

    # If we sample 8 real images, we also create 8 fake images, so the
    # total number of images in a batch will be 8+8=16
    batches_per_epoch = int((len(dataset) / batch_size))
    half_batch = int(batches_per_epoch / 2)

    for epoch in range(epochs):
        if epoch % 10 == 0 and epoch > 0:
            print(f'Saved generator for epoch {epoch}')
            generator.save(f'generator_epoch_{epoch}.h5')
        for b in range(batches_per_epoch):
            
            # First, train the discriminator
            x_real, y_real = generate_real_samples(dataset, half_batch)
            d_loss_real, _ = discriminator.train_on_batch(x_real, y_real)

            x_fake, y_fake = generate_fake_samples(generator, latent_dim_size, half_batch)
            d_loss_fake, _ = discriminator.train_on_batch(x_fake, y_fake)


            # Now, prepare the training data for GAN
            x = generate_latent_space(latent_dim_size, batch_size)
            y = np.ones(shape=(batch_size, 1))

            gan_loss = gan.train_on_batch(x, y)
            
            print(f'[epoch {epoch+1}/{epochs}][batch {b+1}/{batches_per_epoch}] d_loss_real: {d_loss_real:.4f}, d_loss_fake: {d_loss_fake:.4f}, gan_loss: {gan_loss:.4f}')
    
    generator.save(f'generator_final_epoch_{epochs}.h5')



def build_and_train():
    g = generator.build_grayscale()
    d = discriminator.build_binary()
    gan = build_gan(d, g)

    dataset = []
    for file in os.listdir('dataset/hunt_and_kill/'):
        img = cv2.imread(f'dataset/hunt_and_kill/{file}', cv2.IMREAD_GRAYSCALE)
        img = img / 255.0
        dataset.append(img)
        
        if len(dataset) % 1000 == 0:
            print(f'Loaded {len(dataset)} images')

    train_gan(g, d, gan, dataset, epochs=50, batch_size=512)

def squared_relu(x):
    return K.relu(x) ** 2

def test():
    from keras.models import load_model
    from keras.utils import custom_object_scope

    with custom_object_scope({'squared_relu': squared_relu}):
        model = load_model('generator_epoch_10.h5')

    for i in range(25):

        latent_input = generate_latent_space(100, 1)
        # latent_input = np.ones(shape=(1, 100))

        output = model.predict(latent_input)
        output = np.squeeze(output, axis=0)
        # output = output * 255
        cv2.imwrite(f'10/no_threshold_{i}.png', output * 255)
        output = np.where(output > 0.5, 255, 0)
        cv2.imwrite(f'10/{i}.png', output)
    # cv2.waitKey()

if __name__ == '__main__':
    test()
    # build_and_train()

# import tensorflow as tf
# physical_devices = tf.config.list_physical_devices('GPU')
# if physical_devices:
#     for device in physical_devices:
#         tf.config.experimental.set_memory_growth(device, True)
#     print("Num GPUs Available: ", len(physical_devices))
# else:
#     print("No GPUs Available")
# exit()

