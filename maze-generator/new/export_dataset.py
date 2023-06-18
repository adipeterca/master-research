import numpy as np
from PIL import Image

# for i in range(50001):
for i in range(1):
    img = Image.open(f'dataset/maze_{i}.png').convert('L')
    arr = np.asarray(img)

    print(arr.shape)
    print(arr)

