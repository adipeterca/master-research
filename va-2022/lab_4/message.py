import os.path
from keras.models import load_model
from keras import backend as K
import keras.utils
import numpy as np
import tensorflow as tf
from keras import layers
from keras.utils import plot_model
from keras.optimizers import Adam
import pandas as pd
import random
import cv2
from PIL import Image
from sklearn.model_selection import train_test_split

height = 450
width = 600
augment_last_index = 0
images_dict = {}
segmentation_dict = {}


class Ham(keras.utils.Sequence):
    """Helper to iterate over the data (as Numpy arrays)."""

    def __init__(self, batch_size, img_size, input_img_paths, target_img_paths):
        self.batch_size = batch_size
        self.img_size = img_size
        self.input_img_paths = input_img_paths
        self.target_img_paths = target_img_paths

    def __len__(self):
        return len(self.target_img_paths) // self.batch_size

    def __getitem__(self, index):
        """Returns tuple (input, target) correspond to batch #index."""
        i = index * self.batch_size

        batch_input_img_paths = self.input_img_paths[i: i + self.batch_size]
        batch_target_img_paths = self.target_img_paths[i: i + self.batch_size]

        # x = np.zeros((self.batch_size,) + self.img_size + (3,), dtype="float32")
        x = np.zeros((self.batch_size, 128, 128, 3), dtype='float32')
        # (32, 128, 3)

        for j, path in enumerate(batch_input_img_paths):
            if path in images_dict:
                x[j] = images_dict[path]
            else:
                img = load_image(path, self.img_size)
                images_dict[path] = img
                x[j] = img

        y = np.zeros((self.batch_size,) + self.img_size + (1,), dtype="float32")
        
        for j, path in enumerate(batch_target_img_paths):
            if path in segmentation_dict:
                y[j] = segmentation_dict[path]
            else:
                img = load_image(path, self.img_size, True)
                segmentation_dict[path] = img
                y[j] = img
        return x, y


def jaccard(inputs, target):
    intersection = K.sum(target * inputs)
    t_sum = K.sum(target)
    i_sum = K.sum(inputs)
    union = t_sum + i_sum - intersection
    if t_sum == 0 and i_sum == 0:
        return 1.0

    return intersection / union


def dice_metric(inputs, target):
    intersection = K.sum(target * inputs)
    t_sum = K.sum(target)
    i_sum = K.sum(inputs)
    union = t_sum + i_sum - intersection
    if t_sum == 0 and i_sum == 0:
        return 1.0

    return (2 * intersection) / (union + intersection)


def read_metadata():
    metadata = pd.read_csv("dataverse_files/HAM10000_metadata_unaugmented", header=0)
    return metadata


def augment_image(img_path, seg_path, img_id):
    img = cv2.imread(img_path)
    seg = cv2.imread(seg_path)

    # HFlip
    random_ratio = random.randint(0, 9)
    if random_ratio % 2 == 0:
        img = cv2.flip(img, 1)
        seg = cv2.flip(seg, 1)

    # VFlip
    random_ratio = random.randint(0, 9)
    if random_ratio % 2 == 0:
        img = cv2.flip(img, 0)
        seg = cv2.flip(seg, 0)

    # Rotation
    random_ratio = random.randint(0, 360)
    ratio = random.uniform(-random_ratio, random_ratio)
    matrix = cv2.getRotationMatrix2D((width // 2, height // 2), ratio, 1)
    img = cv2.warpAffine(img, matrix, (width, height))
    seg = cv2.warpAffine(seg, matrix, (width, height))

    cv2.imwrite(os.path.join('input', img_id + '.jpg'), img)
    cv2.imwrite(os.path.join('segmentation', img_id + '_segmentation.png'), seg)
    return img_id


def augment_data(metadata):
    global augment_last_index
    augment_last_index = get_last_aug()
    max_data_count = max(metadata["dx"].value_counts())
    modified = False

    with open('other_input/HAM10000_metadata_unaugmented', 'a') as wr:
        for dx_type in set(metadata['dx']):
            data_count = list(metadata['dx']).count(dx_type)
            if data_count < max_data_count:
                necessary_data = max_data_count - data_count
                imgs = list(metadata.loc[metadata['dx'] == dx_type]['image_id'])

                while necessary_data > 0:
                    modified = True
                    index = random.randint(0, len(imgs) - 1)
                    data = metadata.loc[metadata['image_id'] == imgs[index]].values[0]

                    img_id = f'IAUG_{augment_last_index}'
                    entry_id = f'AUG_{augment_last_index}'

                    augment_image(os.path.join('input', imgs[index] + '.jpg'),
                                  os.path.join('segmentation', imgs[index] + '_segmentation.png'), img_id)
                    wr.write(f'{entry_id},{img_id},{data[2]},{data[3]},{data[4]},{data[5]},{data[6]},augmentation\n')

                    augment_last_index += 1
                    necessary_data -= 1
                    if necessary_data % 100 == 0:
                        print(necessary_data)
    return modified


def get_last_aug():
    augs = list(filter(lambda x: 'AUG_' in x, open('other_input/HAM10000_metadata_unaugmented', 'r').read().split('\n')))
    augs = [int(l.split('AUG_')[1].split(',')[0]) for l in augs]
    if len(augs) == 0:
        return 0
    return max(augs) + 1


def resize(img, size):
    img = tf.image.resize(img, size, method="nearest")
    return img


def normalize(img, mask=False):
    if not mask:
        img = np.array(tf.cast(img, tf.float32) / 255.0)
    else:
        img_size = len(img)
        img = np.array([round(v / 255) for v in np.array(img).reshape(img_size ** 2)]).reshape((img_size, img_size, 1))
    return img


def double_conv_block(x, n_filters):
    # Conv2D then ReLU activation
    x = layers.Conv2D(n_filters, 3, padding="same", activation="relu", kernel_initializer="he_normal")(x)
    # Conv2D then ReLU activation
    x = layers.Conv2D(n_filters, 3, padding="same", activation="relu", kernel_initializer="he_normal")(x)
    return x


def downsample_block(x, n_filters):
    f = double_conv_block(x, n_filters)
    p = layers.MaxPool2D(2)(f)
    p = layers.Dropout(0.3)(p)

    return f, p


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


def create_model():
    # inputs
    inputs = layers.Input(shape=(128, 128, 3))

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
    outputs = layers.Conv2D(3, 1, padding="same", activation="softmax")(u9)

    # unet model with Keras Functional API
    unet_model = tf.keras.Model(inputs, outputs, name="U-Net")
    unet_model.compile(optimizer=Adam(), loss='sparse_categorical_crossentropy',
                       metrics=['accuracy', jaccard, dice_metric])

    plot_model(unet_model, to_file='model.png', show_shapes=True)

    return unet_model


def load_image(path, size, mask=False):
    '''
    mask = false inseamna ca i grayscale
    '''
    if mask:
        img = Image.open(path).convert('L')
    else:
        img = Image.open(path)
    img = np.array(list(img.getdata()), dtype=np.uint8).reshape((img.height, img.width, 3 if not mask else 1))
    img = resize(img, size)
    img = normalize(img, mask)

    return img


def get_sets(md):
    md['cell_type_idx'] = pd.Categorical(md['dx']).codes
    md['img_path'] = md['image_id'].map('input/{}.jpg'.format)
    md['seg_path'] = md['image_id'].map('output/{}_segmentation.png'.format)

    features = md.drop(columns=['seg_path'], axis=1)
    target = md['seg_path']
    # x_train_o, x_test_o, y_train_o, y_test_o = train_test_split(features, target, test_size=0.30, random_state=1234)
    x_train_o, x_test_o, y_train_o, y_test_o = train_test_split(features, target, test_size=0.30, shuffle=False)

    x_train = np.asarray(x_train_o['img_path'].tolist())
    x_test = np.asarray(x_test_o['img_path'].tolist())
    y_train = np.asarray(y_train_o.tolist())
    y_test = np.asarray(y_test_o.tolist())

    return x_train, y_train, x_test, y_test


def less_data(x_train, y_train, x_test, y_test):
    coef = 0.1
    train_indexes = random.sample(range(0, len(x_train)), int(len(x_train) * coef))
    test_indexes = random.sample(range(0, len(x_test)), int(len(x_test) * coef))

    return np.asarray([x_train[index] for index in train_indexes]), \
           np.asarray([y_train[index] for index in train_indexes]), \
           np.asarray([x_test[index] for index in test_indexes]), \
           np.asarray([y_test[index] for index in test_indexes])


def execute():
    # Read data
    md = read_metadata()
    
    # Augment data if needed
    # modified = augment_data(md)
    # if modified:
    #     md = read_metadata()

    # Get sets
    x_train, y_train, x_test, y_test = get_sets(md)
    
    # output:
    #     7010 ['input/ISIC_0031426.jpg' 'input/ISIC_0027887.jpg'
    #  'input/ISIC_0032288.jpg' ... 'input/ISIC_0032950.jpg'
    #  'input/ISIC_0029630.jpg' 'input/ISIC_0030772.jpg']
    # 7010 ['output/ISIC_0031426_segmentation.png'
    #  'output/ISIC_0027887_segmentation.png'
    #  'output/ISIC_0032288_segmentation.png' ...
    #  'output/ISIC_0032950_segmentation.png'
    #  'output/ISIC_0029630_segmentation.png'
    #  'output/ISIC_0030772_segmentation.png']
    
    
    # x_train, y_train, x_test, y_test = less_data(x_train, y_train, x_test, y_test)

    # Load images
    train_set = Ham(32, (128, 128), x_train, y_train)
    test_set = Ham(32, (128, 128), x_test, y_test)

    
    exit()
    if os.path.exists('model.h5'):
        # Load model
        model = load_model('model.h5')
    else:
        # Create model
        model = create_model()
        
        # Train
        epochs = 20
        print('\n\n\n\nstarted training')
        model.fit(train_set, epochs=epochs)

        model.save('model.h5')

    scores = model.evaluate(test_set)
    print(scores)


execute()
