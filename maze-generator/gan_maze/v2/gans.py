import os
import random
import numpy as np

import logger
import utils

from keras.models import Sequential
from keras.optimizers import Adam


def generate_latent_space(latent_dim_size, n_samples):
    return np.random.random(size=(n_samples, latent_dim_size))

def generate_real_samples(real_dataset, n_samples):
    x = random.choices(real_dataset, k=n_samples)
    x = np.array(x)
    x = np.expand_dims(x, axis=-1)
    # y = np.ones(shape=(n_samples, 1))
    y = np.zeros(shape=(n_samples, 1))

    return x, y

def generate_fake_samples(generator : Sequential, latent_dim_size=100, n_samples=16):
    latent_space = generate_latent_space(latent_dim_size, n_samples)
    
    x = generator.predict(latent_space)
    # y = np.zeros(shape=(n_samples, 1))
    y = np.ones(shape=(n_samples, 1))

    return x, y



def build(discriminator : Sequential, generator : Sequential):

    # Only for version 2:
    total_params = discriminator.count_params() + generator.count_params()
    if total_params > 1_000_000:
        logger.console.warning('Discriminator and generator combined exceed the maximum number of allowed params.')
        logger.console.warning(f'\tDifference: {total_params - 1_000_000}')
    logger.console.debug(f'Total params count: {total_params}')

    model = Sequential()

    discriminator.trainable = False
    model.add(generator)
    model.add(discriminator)

    lr = discriminator.optimizer.learning_rate.numpy()
    b1 = discriminator.optimizer.beta_1
    opt = Adam(learning_rate=lr, beta_1=b1)

    model.compile(
        optimizer=opt,
        loss='binary_crossentropy'
    )

    return model

# def train(generator : Sequential, discriminator : Sequential, dataset, latent_dim_size=100, epochs=10, batch_size=16, save_step=0):
#     '''
#     @dataset : Python list of numpy arrays representing maze array's!
#     @save_step : can have one of the following values:
#                         * -1 : only return the generator, do not save it!
#                         *  0 : save only the final generator
#                         * >0 : save generator according to the provided step (1 for all created generators)
#     '''

#     # Create the gan
#     gan = build(discriminator, generator)

#     # If we sample 8 real arrays, we also create 8 fake arrays, so the
#     # total number of arrays in a batch will be 8+8=16
#     batches_per_epoch = int((len(dataset) / batch_size))
#     half_batch = int(batches_per_epoch / 2)

#     # Used for plotting information
#     d_loss_real_list = []
#     d_loss_fake_list = []
#     gan_loss_list = []
#     d_acc_fake_list = []
#     d_acc_real_list = []

#     for epoch in range(epochs):
#         if save_step > 0 and epoch % save_step == 0 and epoch > 0:
#             logger.console.info(f'Saved generator for epoch {epoch}')
#             generator.save(f'{utils.DEBUG_PATH}/generator_epoch_{epoch}.h5')
#         for b in range(batches_per_epoch):
            
#             # First, train the discriminator
#             x_real, y_real = generate_real_samples(dataset, half_batch)
#             d_loss_real, d_acc_real = discriminator.train_on_batch(x_real, y_real)

#             x_fake, y_fake = generate_fake_samples(generator, latent_dim_size, half_batch)
#             d_loss_fake, d_acc_fake = discriminator.train_on_batch(x_fake, y_fake)


#             # Now, prepare the training data for GAN
#             x = generate_latent_space(latent_dim_size, batch_size)
#             y = np.ones(shape=(batch_size, 1))

#             gan_loss = gan.train_on_batch(x, y)
            
#             utils.LAST_TRAINED_MODEL = generator

#             # Add plotting information
#             d_loss_real_list.append(d_loss_real)
#             d_loss_fake_list.append(d_loss_fake)
#             gan_loss_list.append(gan_loss)
#             d_acc_real_list.append(d_acc_real)
#             d_acc_fake_list.append(d_acc_fake)

#             logger.console.debug(f'[epoch {epoch+1}/{epochs}][batch {b+1}/{batches_per_epoch}] d_loss_real: {d_loss_real:.4f}, d_loss_fake: {d_loss_fake:.4f}, gan_loss: {gan_loss:.4f}, d_acc_fake: {d_acc_fake * 100:.2f}%, d_acc_real: {d_acc_real * 100:.2f}%')
    
#     if save_step != -1:
#         generator.save(f'{utils.DEBUG_PATH}/generator_epoch_{epoch}.h5')

#     utils.create_plot(
#         d_loss_fake=d_loss_fake_list,
#         d_loss_real=d_loss_real_list,
#         gan_loss=gan_loss_list,
#         d_acc_fake=d_acc_fake_list,
#         d_acc_real=d_acc_real_list,
#     )

#     return generator

def train(generator : Sequential, discriminator : Sequential, settings : dict):
    '''
    Method for training the discriminator and generator in different ways.
    Check settings["disc_train_times"] to see how often should the discriminator be set. Same for the generator.

    @dataset : Python list of numpy arrays representing maze array's!
    @save_step : can have one of the following values:
                        * -1 : only return the generator, do not save it!
                        *  0 : save only the final generator
                        * >0 : save generator according to the provided step (1 for all created generators)
    '''

    # Create the gan
    gan = build(discriminator, generator)


    # If we sample 8 real arrays, we also create 8 fake arrays, so the
    # total number of arrays in a batch will be 8+8=16
    batches_per_epoch = int((len(settings["dataset"]) / settings["batch_size"]))
    half_batch = int(batches_per_epoch / 2)

    # Used for plotting information
    d_loss_real_list = []
    d_loss_fake_list = []
    gan_loss_list = []
    d_acc_fake_list = []
    d_acc_real_list = []

    for epoch in range(1, settings["epochs"]+1):
        if settings["save_step"] > 0 and epoch % settings["save_step"] == 0:
            logger.console.info(f'Saved generator for epoch {epoch}')
            generator.save(f'{utils.RUN_FOLDER}/{utils.RUN_CONFIG}/generator_epoch_{epoch}.h5')

        # Check for mode failure (both accuracies are 100%)
        mode_failure = False
        if epoch >= settings["epochs"] / 2:
            for i in range(1, 10):
                if d_acc_real_list[-i] == 1 and d_acc_fake_list[-i] == 1:
                    mode_failure = True
                    break
        
        if mode_failure:
            logger.console.error(f'Model may be in mode collapse.\n Before epoch {epoch}, the last 10 discriminator accuracies were 100% for both REAL and FAKE.')
            break

        for b in range(batches_per_epoch):
            
            disc_train_times = 1
            gen_train_times = 1

            if b <= int(batches_per_epoch * 0.25):
                disc_train_times = settings["disc_train_times"]
            elif b >= int(batches_per_epoch * 0.75):
                gen_train_times = settings["gen_train_times"]

            # First, train the discriminator
            for i in range(disc_train_times):
                x_real, y_real = generate_real_samples(settings["dataset"], half_batch)
                d_loss_real, d_acc_real = discriminator.train_on_batch(x_real, y_real)

                x_fake, y_fake = generate_fake_samples(generator, settings["latent_dim_size"], half_batch)
                d_loss_fake, d_acc_fake = discriminator.train_on_batch(x_fake, y_fake)

                d_loss_real_list.append(d_loss_real)
                d_loss_fake_list.append(d_loss_fake)

                d_acc_real_list.append(d_acc_real)
                d_acc_fake_list.append(d_acc_fake)

            # Now, prepare the training data for GAN
            for i in range(gen_train_times):
                x = generate_latent_space(settings["latent_dim_size"], settings["batch_size"])
                y = np.ones(shape=(settings["batch_size"], 1))

                gan_loss = gan.train_on_batch(x, y)

                utils.LAST_TRAINED_MODEL = generator
                
                gan_loss_list.append(gan_loss)
            
            logger.console.debug(f'[epoch {epoch}/{settings["epochs"]}][batch {b+1}/{batches_per_epoch}] d_loss_real: {d_loss_real:.4f}, d_loss_fake: {d_loss_fake:.4f}, gan_loss: {gan_loss:.4f}, d_acc_fake: {d_acc_fake * 100:.2f}%, d_acc_real: {d_acc_real * 100:.2f}%')

        logger.console.info(f'[epoch {epoch}] d_loss_real: {d_loss_real:.4f}, d_loss_fake: {d_loss_fake:.4f}, gan_loss: {gan_loss:.4f}, d_acc_fake: {d_acc_fake * 100:.2f}%, d_acc_real: {d_acc_real * 100:.2f}%')

        # Save some statistics for future use
        with open(f'{utils.RUN_FOLDER}/{utils.RUN_CONFIG}/stats_e{epoch}.txt', 'w') as fout:
            
            output = utils.scale_output(generator)

            for i in range(0, 16):
                occ = np.count_nonzero(output == i)
                fout.write(f'Value {i :>2} stats: {occ:>5}\t{occ / 4096 * 100:>5.2f} %\n')

    if settings["save_step"] != -1:
        generator.save(f'{utils.RUN_FOLDER}/{utils.RUN_CONFIG}/generator_epoch_{epoch}.h5')

    utils.create_plot(
        d_loss_fake=d_loss_fake_list,
        d_loss_real=d_loss_real_list,
        gan_loss=gan_loss_list,
        d_acc_fake=d_acc_fake_list,
        d_acc_real=d_acc_real_list
    )

    return generator