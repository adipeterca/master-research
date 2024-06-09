from keras.models import load_model
import os
import numpy as np

from amazed.modules.maze import Maze

class GANModel():
    '''
    Use a pretrained GAN model to generate 64x64 mazes.
    '''

    def __init__(self, model="v2.4.1.G_v.2.3.6.D"):
        
        self.model_path = os.path.dirname(os.path.abspath(__file__)) + f"/trained_models/{model}.h5"
        self.generator = load_model(self.model_path)

    def generate(self) -> Maze:
        _input = np.random.random(size=(1, 100))
        output = self.generator.predict(_input, verbose=0)

        output = np.round((output + 1) * 7.5)
        output = output.reshape((64, 64))

        return Maze.build_from_array(output, 64, 64)