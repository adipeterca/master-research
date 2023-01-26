from PIL import Image
import pytesseract
import cv2
from skimage.util import random_noise
import numpy as np
import os

ground_truth = {
    "test_1.jpg" : "Further information may be obtained\nM.A., Fellow and Lecturer in Chemistry,\nfrom Prof. A. Gilligan, D.Sc., Departmen\nLeeds, and from Mr. A. H. Worrall, M.A.,\nCollege, Jersey.",
    "test_2.jpg" : "Tesseract Will\nFail With Noisy\nBackgrounds"
}


def accuracy(output_text : str, expected_text : str):
    '''
    Idea to modify: search for the first letter from the expected_text, discarding each letter that does not match from the output_text until no letters are left or the correct one
    is found
    '''
    output_chars = list(output_text.lower())
    expected_chars = list(expected_text.lower())

    acc = 0
    for char in output_chars:
        if char in expected_chars:
            acc += 1
            expected_chars.remove(char)
    
    print("------------------------------")
    print("The original text: \n")
    print(expected_text)
    print("------------------------------")
    print("The output text: \n")
    print(output_text)
    print("------------------------------\n\n")
    print(f"Accuracy (may not be that precise): {acc}\nInitial number of characters: {len(expected_text)}\nOutput number of characters: {len(output_text)}")

def noise(image : cv2.Mat, _type = 's&p'):
    '''
    Supported types: s&p, gaussian
    '''
    if _type == 's&p':
        # Values greater than 0.1 will make first image almost unrecognizable for Tessaract.
        new_image = random_noise(image, mode='s&p', amount=0.05)
    elif _type == 'gaussian':
        new_image = random_noise(image, mode='gaussian')
    
    new_image = np.array(255*new_image, dtype='uint8')
    return new_image

def rotate(image : cv2.Mat, angle = cv2.ROTATE_90_CLOCKWISE):
    '''
    Rotate the image using -angle- degrees
    '''
    if angle == cv2.ROTATE_180:
        new_image = cv2.rotate(image, cv2.ROTATE_180)
    elif angle == cv2.ROTATE_90_CLOCKWISE:
        new_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == cv2.ROTATE_90_COUNTERCLOCKWISE:
        new_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return new_image

def shear(image : cv2.Mat, axis = 'x'):
    '''
    Shear the image along the -axis- axis.
    Source: https://www.thepythoncode.com/article/image-transformations-using-opencv-in-python#Image_Shearing
    '''
    rows, cols = image.shape
    if axis == 'x':
        M = np.float32([[1, 1, 0],
                        [0, 1, 0],
                        [0, 0, 1]])
        new_image = cv2.warpPerspective(image, M, (int(cols*1.5), int(rows*1.5)))
    else:
        M = np.float32([[1,   0, 0],
                        [0.5, 1, 0],
                        [0,   0, 1]])
        new_image = cv2.warpPerspective(image, M, (int(cols*1.5), int(rows*1.5)))
    return new_image

def resize(image : cv2.Mat, scale_ratio_width = 200, scale_ratio_height = 200):
    '''
    Scale ratio over 100 will upscale the image,
    scale ratio under 100 will downscale the image.
    Source: https://docs.opencv.org/3.4/da/d54/group__imgproc__transform.html#ga5bb5a1fea74ea38e1a5445ca803ff121
    '''
    width = int(image.shape[1] * scale_ratio_width / 100)
    height = int(image.shape[0] * scale_ratio_height / 100)

    return cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)

def blur(image : cv2.Mat, _type = 'gaussian', ksize = 3):
    '''
    Available types: gaussian, median, normal
    Source: https://docs.opencv.org/4.x/d4/d13/tutorial_py_filtering.html
    '''
    if ksize % 2 == 0:
        print('[ERROR] Ksize must be an odd number (3, 5, 7, ...)')
        exit(-1)
    if _type == 'gaussian':
        new_image = cv2.GaussianBlur(image, (ksize, ksize), 0)
    elif _type == 'median':
        new_image = cv2.medianBlur(image, ksize)
    elif _type == 'normal':
        new_image = cv2.blur(image, (ksize, ksize))

    return new_image

def sharpen(image : cv2.Mat):
    '''
    Sharpen an image using a default kernel
    '''
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    # -1 for ddepth because we want to keep aspect ratio
    new_image = cv2.filter2D(image, -1, kernel)
    return new_image

def erosion(image : cv2.Mat, ksize = 3):
    '''
    Source: https://www.geeksforgeeks.org/erosion-dilation-images-using-opencv-python/
    '''
    if ksize % 2 == 0:
        print('[ERROR] Ksize must be an odd number (3, 5, 7, ...)')
        exit(-1)
    
    new_image = cv2.erode(image, (ksize, ksize))
    return new_image

def dilation(image : cv2.Mat, ksize = 3):
    '''
    Source: https://www.geeksforgeeks.org/erosion-dilation-images-using-opencv-python/
    '''
    if ksize % 2 == 0:
        print('[ERROR] Ksize must be an odd number (3, 5, 7, ...)')
        exit(-1)
    
    new_image = cv2.dilate(image, (ksize, ksize))
    return new_image

def opening(image : cv2.Mat, ksize = 3):
    '''
    Source: https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
    '''
    new_image = erosion(image, ksize)
    new_image = dilation(new_image, ksize)
    return new_image

def closing(image : cv2.Mat, ksize = 3):
    '''
    Source: https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
    '''
    # We could also use
    # new_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, (ksize, ksize))

    new_image = dilation(image, ksize)
    new_image = erosion(new_image, ksize)
    return new_image

def threshold(image : cv2.Mat, _type = cv2.THRESH_BINARY):
    '''
    Source: https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
    '''
    new_image = cv2.threshold(image, 0, 255, _type)[1]
    return new_image

if __name__ == '__main__':
    path = 'test_1.jpg'

    image_rgb = cv2.imread(path)
    image_gray = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2GRAY)

    # image_new = image_gray
    image_new = noise(image_gray)
    # image_new = rotate(image_gray)
    # image_new = shear(image_gray, 'x')
    # image_new = resize(image_gray, 50, 400)
    # image_new = blur(image_gray, 'gaussian', 21)
    # image_new = sharpen(image_gray)
    # image_new = erosion(image_gray)
    # image_new = dilation(image_gray)
    # image_new = opening(image_gray)
    # image_new = closing(image_gray)
    # image_new = threshold(image_gray)

    new_path = 'gray_modified_' + path
    cv2.imwrite(new_path, image_new)

    text = pytesseract.image_to_string(Image.open('gray_modified_' + path))
    accuracy(text, ground_truth[path])
