import keras.backend as K

def squared_relu(x):
    return K.relu(x) ** 2