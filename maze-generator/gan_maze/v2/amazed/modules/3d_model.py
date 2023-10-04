# Import libraries
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
 
def build_3d_model(data : np.array, axes):
    # Change the Size of Graph using
    # Figsize
    fig = plt.figure(figsize=(10, 10))
    
    # Generating a 3D sine wave
    ax = plt.axes(projection='3d')
    
    # Control Tranperency
    alpha = 0.9
    
    # Control colour
    colors = np.ones(axes + [4])
    colors = np.multiply(colors, [1, 0, 0, alpha])

    # colors[0] = [1, 0, 0, alpha]  # red
    # colors[1] = [1, 0, 0, alpha]  # red
    # colors[2] = [1, 0, 0, alpha]  # red
    # colors[3] = [1, 0, 0, alpha]  # red
    # colors[4] = [1, 0, 0, alpha]  # red
    
    # turn off/on axis
    plt.axis('off')
    
    # Voxels is used to customizations of
    # the sizes, positions and colors.
    ax.voxels(data, facecolors=colors, edgecolors='grey')

    plt.show()

size = 10
# Create axis
axes = [size, size, size]

# data = np.ones(axes)
data = np.random.randint(2, size=axes)
build_3d_model(data, axes)