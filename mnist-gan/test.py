from PIL import Image
from keras.models import load_model
import numpy as np

model = load_model('model.h5')

img = Image.open('almost_fake.png')
img = img.convert('L')
x = np.array(list(img.getdata())).reshape((1, 28, 28, 1))

print('Testing...\n\n')
output = model.predict(x)
if output == 0:
    print('The provided sample is FAKE')
else:
    print('The provided sample is REAL')
img.show()
print('Done!')

