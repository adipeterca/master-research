from PIL import Image
import os
import sys
import random

class SkinRecognizer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = file_path.split('/')[-1]
        self.original_rgb = Image.open(file_path)
        self.width, self.height = self.original_rgb.size

        print(f'Loaded image {file_path} of size {self.width}x{self.height} ({self.width * self.height} pixels)')


    def convert_all(self):
        '''
        Convert the given image to all possible types.
        '''
        self.convert('rgb')
        self.convert('ycbcr')
        self.convert('hsv')


    def convert(self, _type = 'rgb'):
        '''
        Convert the original image to type _type and return the pixels as a list.
        @returns : a list of pixels from the converted image
        '''
        # Create the new black/white image & the pixels list
        # self.modified = Image.new('L', (self.width, self.height))

        image = self.original_rgb.convert('HSV') if _type == 'hsv' else self.original_rgb
        
        original_pixels = list(image.getdata())
        modified_pixels = []

        for pixel in original_pixels:
            if self.is_skin(pixel, _type):
                modified_pixels.append(255)
            else:
                modified_pixels.append(0)

        # # Uncomment if you want to display the created black-white image
        # self.modified.putdata(modified_pixels)
        # self.modified.show()
        return modified_pixels


    def portrait(self):
        '''
        Assuming the provided image is a portrait, the function tries to frame the human face. 
        It does this by searching for a the biggest possible skin pixels square it can find, 
        using a random search algorithm.
        '''
        modified_pixels = list(self.original_rgb.getdata())

        # Number of iterations
        iters = 300

        # len = 300
        len = int(self.width * 0.6)

        # The best ratio found so far
        best_ratio = 0
        # Best crop found so far
        best_image = None

        stagnations = 0

        for i in range(iters):
            print(f'At iteration {i+1}. Current best ratio is {best_ratio}')
            if best_ratio > 0.9:
                    break
            x = random.randint(0, self.width - len)
            y = random.randint(0, self.height - len)
            image = self.original_rgb.crop((x, y, x+len, y+len))
            
            count = 0
            for pixel in list(image.getdata()):
                if self.is_skin(pixel, 'rgb'):
                    count += 1
            ratio = count / (image.size[0] * image.size[1])
            if ratio > best_ratio:
                best_ratio = ratio
                best_image = image.copy()
                stagnations = 0
            else:
                stagnations += 1
                # The parameter for self.width can be modified
                # in order to achieve better results
                if stagnations == 20 and len > self.width * 0.4:
                    len = int(len * 0.9)
                    stagnations = 0

        best_image.show()
        exit()
        modified_image = Image.new('RGB', (self.width, self.height))
        modified_image.putdata(modified_pixels)
        modified_image.show()


    def get_results(self, test_image_path, _type = 'rgb'):
        '''
        Converts the original image to skin pixels using _type method,
        returning the a confusion matrix and an accuracy measure.
        @returns: a confusion matrix [[TP, FN], [FP, TN]] and the accuracy
        '''

        converted_pixels = self.convert(_type)
        original_image = Image.open(test_image_path).convert('HSV') if _type == 'hsv' else Image.open(test_image_path)

        original_pixels = list(original_image.convert('L').getdata())
        
        if len(original_pixels) != len(converted_pixels):
            raise IndexError('Pixels list are not the same size.')

        # Calculate the confusion matrix
        tp = 0
        tn = 0
        fp = 0
        fn = 0

        for i in range(len(converted_pixels)):
            if original_pixels[i] == 255 and converted_pixels[i] == 255:
                tp += 1
            elif original_pixels[i] == 255 and converted_pixels[i] == 0:
                fn += 1
            elif original_pixels[i] == 0 and converted_pixels[i] == 255:
                fp += 1
            else:
                tn += 1
        
        accuracy = (tp + tn) / (tp + fn + fp + tn)
        return [[tp, fn], [fp, tn]], accuracy


    def is_skin(self, pixel : tuple, _type = 'rgb'):
        '''
        @param pixel : a tuple representing RGB values.
        @returns : whether or not the given pixel is a skin pixel.
        '''
        if _type == 'rgb':
            r, g, b = pixel

            return r > 95 and g > 40 and b > 20 and \
            max(pixel) - min(pixel) > 15 and \
            abs(r - g) > 15 and r > g and r > b

        elif _type == 'ycbcr':
            r, g, b = pixel

            y = 0.299 * r + 0.587 * g + 0.114 * b
            cb = -0.1687 * r - 0.3313 * g + 0.5 * b + 128
            cr = 0.5 * r - 0.4187 * g - 0.0813 * b + 128

            return y > 80 and 85 < cb and cb < 135 and 135 < cr and cr < 180
        
        elif _type == 'hsv':
            h, s, v = pixel
            # Scale values
            s = s / 255
            v = v / 255
            return h >= 0 and h <= 50 and s >= 0.23 and s <= 0.68 and v >= 0.35 and v <= 1
        else:
            raise ValueError(f'Invalid type provided for is_skin() function : <{_type}>')


if __name__ == '__main__':
    
    # Point a)
    if len(sys.argv) == 2 and sys.argv[1] == 'convert_all':
        for path in os.listdir('./input_images'):
            if path.endswith('jpg'):
                skin_recog = SkinRecognizer('./input_images/' + path)
                skin_recog.convert_all()

    # Point b)
    elif len(sys.argv) == 2 and sys.argv[1] == 'dataset':
        input_images = ['dataset/input_images/' + x for x in os.listdir('dataset/input_images')]
        ground_truth_images = ['dataset/ground_truth_images/' + x for x in os.listdir('dataset/ground_truth_images')]

        for i in range(len(input_images)):
            skin_recog = SkinRecognizer(input_images[i])
            for t in ['rgb', 'ycbcr', 'hsv']:
                conf_matrix, acc = skin_recog.get_results(ground_truth_images[i], t)
                print(f'Results for input image {input_images[i]}: \n{conf_matrix}\naccuracy = {acc}')

    # Testing for a specific image (main.py test INPUT_PATH EXPECTED_OUTPUT_PATH)
    elif len(sys.argv) == 4 and sys.argv[1] == 'test':
        skin_recog = SkinRecognizer(sys.argv[2])
        conf_matrix, acc = skin_recog.get_results(sys.argv[3], 'rgb')
        print(f'Results RGB for input image {sys.argv[2]}: \n{conf_matrix}\naccuracy = {acc}')
        
    # Point c)
    elif len(sys.argv) == 3 and sys.argv[1] == 'face':
        SkinRecognizer(sys.argv[2]).portrait()
        # It works for 
        # dataset\input_images\2.jpg (self.width * 0.6)
        # dataset\input_images\9.jpg (self.width * 0.6)
        # dataset\input_images\18.jpg (self.width * 0.6)
        # dataset\input_images\19.jpg (self.width * 0.4)
        # dataset\input_images\25.jpg (self.width * 0.4)
        # dataset\input_images\33.jpg (self.width * 0.3)
        
        
    