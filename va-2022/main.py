from PIL import Image
import os

class SkinRecognizer:
    def __init__(self, file_path = '1.jpg'):
        self.file_path = file_path
        self.original_rgb = Image.open(file_path)
        self.original_hsv = self.original_rgb.convert('HSV')
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
        # Create the new black/white image & the pixels list
        self.modified = Image.new('L', (self.width, self.height))

        image = self.original_hsv if _type == 'hsv' else self.original_rgb
        modified_pixels = []

        for pixel in list(image.getdata()):
            if self.is_skin(pixel, _type):
                modified_pixels.append(255)
            else:
                modified_pixels.append(0)
        
        save_path = self.file_path[:-len('.jpg')] + f'_{_type}_bw.jpg'
        print(f'Created image {save_path} for type {_type}.')
        self.modified.putdata(modified_pixels)
        self.modified.save(save_path)
        self.modified.show()
    
                
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
            print(f'[DEBUG] Received pixel value {pixel} for HSV.')
            h, s, v = pixel
            return h >= 0 and h <= 50 and s >= 0.23 and s <= 0.68 and v >= 0.35 and v <= 1
        else:
            raise ValueError(f'Invalid type provided for is_skin() function : <{_type}>')
    

skin_recog = SkinRecognizer('1.jpg')
skin_recog.convert_all()
# for path in os.listdir('.'):
#     if path.endswith('jpg'):
#         skin_recog = SkinRecognizer(path)
