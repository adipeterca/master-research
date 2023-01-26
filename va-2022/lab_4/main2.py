import tensorflow as tf
from tensorflow import keras
import numpy as np
from keras import layers
from keras import backend
from keras.models import load_model
from PIL import Image
import os
import time


def resize(input_image, size=128):
    return tf.image.resize(input_image, (size, size), method="nearest")

def normalize(input_image, grayscale=False):
    if grayscale:
        img_size = len(input_image)
        img = np.array([round(v / 255) for v in np.array(input_image).reshape(img_size * img_size)]).reshape((img_size, img_size, 1))
    else:
        img = np.array(tf.cast(input_image, tf.float32) / 255.0)
    return img

def load_image(path, size, grayscale=False):
    # Maybe add memoisation?
    if grayscale:
        img = Image.open(path).convert('L')
        img = np.array(list(img.getdata()), dtype=np.uint8).reshape((img.height, img.width, 1))
    else:
        img = Image.open(path)
        img = np.array(list(img.getdata()), dtype=np.uint8).reshape((img.height, img.width, 3))
    
    img = resize(img, size)
    img = normalize(img, grayscale)

    return img

class KerasObject(keras.utils.Sequence):
    def __init__(self, batch_size, size, input_paths, output_paths, name):
        self.batch_size = batch_size
        self.size = size
        self.input_paths = input_paths
        self.output_paths = output_paths

        # Number of batches in the entire dataset
        self.len = len(self.input_paths) // self.batch_size
        
        self.name = name
        print(f'Created {name} dataset with {self.len} number of batches, each batch with {batch_size} tuples of (input, output).')

    def __len__(self):
        return self.len
    
    def __getitem__(self, index):
        '''
        Index represents the batch --index-- number.
        Each KerasObject is like a list of batches.
        
        Returns a tuple of (batch_size, size, size, 3) for RGB and (batch_size, size, size, 1) for grayscale.
        '''

        start = index * self.batch_size
        end = start + self.batch_size

        inputs = np.zeros((self.batch_size, self.size, self.size, 3))
        i = 0
        for path in self.input_paths[start:end]:
            inputs[i] = load_image(path, self.size)
            i += 1

        outputs = np.zeros((self.batch_size, self.size, self.size, 1))
        i = 0
        for path in self.output_paths[start:end]:
            outputs[i] = load_image(path, self.size, True)
            i += 1

        return inputs, outputs


def jaccard_index(y_true, y_pred):
    intersection = backend.sum(y_true * y_pred)
    t_sum = backend.sum(y_true)
    i_sum = backend.sum(y_pred)
    union = t_sum + i_sum - intersection
    if t_sum == 0 and i_sum == 0:
        return 1.0

    return intersection / union

def dice_coefficient(y_true, y_pred):
    intersection = backend.sum(y_true * y_pred)
    t_sum = backend.sum(y_true)
    i_sum = backend.sum(y_pred)
    union = t_sum + i_sum - intersection
    if t_sum == 0 and i_sum == 0:
        return 1.0

    return (2 * intersection) / (union + intersection)


def double_conv_block(x, n_filters):
    # Conv2D then ReLU activation
    x = layers.Conv2D(n_filters, 3, padding = "same", activation = "relu", kernel_initializer = "he_normal")(x)
    # Conv2D then ReLU activation
    x = layers.Conv2D(n_filters, 3, padding = "same", activation = "relu", kernel_initializer = "he_normal")(x)
    return x

def upsample_block(x, conv_features, n_filters):
    # upsample
    x = layers.Conv2DTranspose(n_filters, 3, 2, padding="same")(x)
    # concatenate
    x = layers.concatenate([x, conv_features])
    # dropout
    x = layers.Dropout(0.3)(x)
    # Conv2D twice with ReLU activation
    x = double_conv_block(x, n_filters)

    return x

def downsample_block(x, n_filters):
    f = double_conv_block(x, n_filters)
    p = layers.MaxPool2D(2)(f)
    p = layers.Dropout(0.3)(p)
    return f, p


def build_unet_model():
    # inputs
    inputs = layers.Input(shape=(128,128,3))

    # encoder: contracting path - downsample
    # 1 - downsample
    f1, p1 = downsample_block(inputs, 64)
    # 2 - downsample
    f2, p2 = downsample_block(p1, 128)
    # 3 - downsample
    f3, p3 = downsample_block(p2, 256)
    # 4 - downsample
    f4, p4 = downsample_block(p3, 512)

    # 5 - bottleneck
    bottleneck = double_conv_block(p4, 1024)

    # decoder: expanding path - upsample
    # 6 - upsample
    u6 = upsample_block(bottleneck, f4, 512)
    # 7 - upsample
    u7 = upsample_block(u6, f3, 256)
    # 8 - upsample
    u8 = upsample_block(u7, f2, 128)
    # 9 - upsample
    u9 = upsample_block(u8, f1, 64)

    # outputs
    outputs = layers.Conv2D(3, 1, padding="same", activation = "softmax")(u9)

    # unet model with Keras Functional API
    unet_model = tf.keras.Model(inputs, outputs, name="U-Net")

    # Pixel accuracy - "accuracy"
    # Jaccard index - jaccard_index
    # Dice coefficient - dice_coefficient
    unet_model.compile(optimizer=tf.keras.optimizers.Adam(),
                  loss="sparse_categorical_crossentropy",
                  metrics=["accuracy", jaccard_index, dice_coefficient])

    return unet_model

if __name__ == '__main__':
    print('\n' * 10)
    print('Starting program execution...\n')
    start = time.time()

    dsize = 10015 # Original value
    # dsize = 100
    batch_size = 32
    # batch_size = 4
    train_proc = 0.7
    print(f'Train set size: {dsize}\nBatch size: {batch_size}\nNumber of batches (rounded): {dsize // batch_size}\nTrain/Test procentages: {train_proc * 100:>.2f}% / {(1-train_proc) * 100:>.2f}%\n')

    # Prepare training & testing data
    print('Loading input image paths...')
    input_image_paths = ['input/' + path for path in os.listdir('input')[:dsize]]
    print('Done!\n')

    print('Loading output image paths...')
    output_image_paths = ['output/' + path for path in os.listdir('output')[:dsize]]
    print('Done!\n')

    print('Building model (errors are ignored)...')
    try:
        unet_model = build_unet_model()
    except:
        pass
    print('Done!\n')


    train_input_image_paths = input_image_paths[0:int(dsize * train_proc)]
    train_output_image_paths = output_image_paths[0:int(dsize * train_proc)]

    train_object = KerasObject(batch_size, 128, train_input_image_paths, train_output_image_paths, 'TRAIN')
    unet_model.fit(train_object, epochs=5)
    unet_model.save('model.h5')
    # unet_model = load_model('model.h5')

    test_input_image_paths = input_image_paths[int(dsize * train_proc):]
    test_output_image_paths = output_image_paths[int(dsize * train_proc):]

    test_object = KerasObject(batch_size, 128, test_input_image_paths, test_output_image_paths, 'TEST')
    # loss, acc = unet_model.evaluate(test_object)
    loss, acc, ji, dc = unet_model.evaluate(test_object, custom_objects={'jaccard_index' : jaccard_index, 'dice_coefficient' : dice_coefficient})

    print(f'Loss: {loss}\nPixel accuracy: {acc}\nJaccard index: {ji}\nDice coefficient: {dc}\n')

    end = time.time() - start
    print(f'\n\nProgram finished in {end % 60} minutes and {end // 60} seconds!')