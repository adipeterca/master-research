from PIL import Image

class ImageConvertor:
    '''
    Class for converting a RGB image to Grayscale.
    '''
    def __init__(self, image_path = './test_image.jpg'):
        self.image = Image.open(image_path)
        self.width, self.height = self.image.size

    def simple_average(self, save=False):
        grayscale_pixels = []
        rgb_pixels = list(self.image.getdata())

        for (r, g, b) in rgb_pixels:
            grayscale_pixels.append((r + g + b) / 3)
        
        grayscale_image = Image.new('L', (self.width, self.height))
        grayscale_image.putdata(grayscale_pixels)
        grayscale_image.show()
        if save:
            grayscale_image.save('simple_average.jpg')
    
    def weighted_average(self, method = 1, save = False):
        grayscale_pixels = []
        rgb_pixels = list(self.image.getdata())

        for (r, g, b) in rgb_pixels:
            if method == 1:
                grayscale_pixels.append(r * 0.3 + g * 0.59 + b * 0.11)
            elif method == 2:
                grayscale_pixels.append(r * 0.2126 + g * 0.7152 + b * 0.0752)
            else:
                grayscale_pixels.append(r * 0.299 + g * 0.587 + b * 0.114)

        grayscale_image = Image.new('L', (self.width, self.height))
        grayscale_image.putdata(grayscale_pixels)
        grayscale_image.show()
        if save:
            grayscale_image.save('weighted_average.jpg')
    
    def desaturation(self, save = False):
        grayscale_pixels = []
        rgb_pixels = list(self.image.getdata())
        
        for pixel in rgb_pixels:
            grayscale_pixels.append((min(pixel) + max(pixel)) / 2)

        grayscale_image = Image.new('L', (self.width, self.height))
        grayscale_image.putdata(grayscale_pixels)
        grayscale_image.show()
        if save:
            grayscale_image.save('desaturation.jpg')
    
    def decomposition(self, method='max', save=False):
        grayscale_pixels = []
        rgb_pixels = list(self.image.getdata())

        for (r, g, b) in rgb_pixels:
            if method == 'max':
                grayscale_pixels.append(r * 0.3 + g * 0.59 + b * 0.11)
            else:
                grayscale_pixels.append(r * 0.299 + g * 0.587 + b * 0.114)

        grayscale_image = Image.new('L', (self.width, self.height))
        grayscale_image.putdata(grayscale_pixels)
        grayscale_image.show()
        if save:
            grayscale_image.save('decomposition.jpg')

    def single_color_channel(self, method='r', save=False):
        grayscale_pixels = []
        rgb_pixels = list(self.image.getdata())

        for (r, g, b) in rgb_pixels:
            if method == 'r':
                grayscale_pixels.append(r)
            elif method == 'g':
                grayscale_pixels.append(g)
            else:
                grayscale_pixels.append(b)

        grayscale_image = Image.new('L', (self.width, self.height))
        grayscale_image.putdata(grayscale_pixels)
        grayscale_image.show()
        if save:
            grayscale_image.save('single_color_channel.jpg')

    def gray_shades(self, shades=2, save=False):
        '''
        @param shades: how many distinct values of gray to use (must be lower than 256)
        '''
        grayscale_pixels = []
        rgb_pixels = list(self.image.getdata())

        # conversion_factor = 255 / (shades - 1)

        interval = [i * (255 / shades) for i in range(shades+1)]

        for (r, g, b) in rgb_pixels:
            # grayscale_pixels.append((((r+g+b)/3) / conversion_factor + 0.5) * conversion_factor)
            avg = r * 0.3 + g * 0.59 + b * 0.11
            i = 0

            # Stop at the first value bigger than avg
            while i < len(interval) and interval[i] < avg:
                i += 1
            
            # Return to the previous value
            i -= 1
            grayscale_pixels.append((interval[i] + interval[i+1])/2)
            
        grayscale_image = Image.new('L', (self.width, self.height))
        grayscale_image.putdata(grayscale_pixels)
        grayscale_image.show()
        if save:
            grayscale_image.save('gray_shades.jpg')

    def floyd_steinberg(self, save=False):
        image_arr = []
        rgb_pixels = list(self.image.getdata())
        for i in range(self.height):
            image_arr.append([])
            for j in range(self.width):
                # This also converts the image to grayscale
                # using simple average
                image_arr[i].append(sum(rgb_pixels[i * self.width + j]) / 3)
        
        grayscale_pixels = []
        # Go only until the edge, but exclude it
        # It will be completed later (because otherwise we would encounter a IndexError)
        for i in range(self.height-1):
            for j in range(self.width-1):
                grayscale_pixels.append(0 if image_arr[i][j] < 128 else 255)
                
                error = image_arr[i][j] - grayscale_pixels[-1]
                
                image_arr[i][j+1] += error * (7 / 16)
                image_arr[i+1][j-1] += error * (3 / 16)
                image_arr[i+1][j] += error * (5 / 16)
                image_arr[i+1][j+1] += error * (1 / 16)
            # Complete the column
            grayscale_pixels.append(image_arr[i][self.width-1])
        
        # Complete each row
        for i in range(self.width-1):
            grayscale_pixels.append(image_arr[self.height-1][i])
        
        grayscale_image = Image.new('L', (self.width, self.height))
        grayscale_image.putdata(grayscale_pixels)
        grayscale_image.show()
        if save:
            grayscale_image.save('floyd_steinberg.jpg')
        
    def burkes(self, save=False):
        image_arr = []
        rgb_pixels = list(self.image.getdata())
        for i in range(self.height):
            image_arr.append([])
            for j in range(self.width):
                # This also converts the image to grayscale
                # using simple average
                image_arr[i].append(sum(rgb_pixels[i * self.width + j]) / 3)
        
        grayscale_pixels = []
        for i in range(self.height-1):
            for j in range(self.width-2):
                grayscale_pixels.append(0 if image_arr[i][j] < 128 else 255)
                
                error = image_arr[i][j] - grayscale_pixels[-1]
                
                image_arr[i][j+1] += error * (7 / 16)
                image_arr[i+1][j-1] += error * (3 / 16)
                image_arr[i+1][j] += error * (5 / 16)
                image_arr[i+1][j+1] += error * (1 / 16)
            # Complete the column with default values
            grayscale_pixels.append(image_arr[i][self.width-2])
            grayscale_pixels.append(image_arr[i][self.width-1])
        
        # Complete the last line
        for i in range(self.width):
            grayscale_pixels.append(image_arr[self.height-1][i])
                
        
        grayscale_image = Image.new('L', (self.width, self.height))
        grayscale_image.putdata(grayscale_pixels)
        grayscale_image.show()
        if save:
            grayscale_image.save('burkes.jpg')

if __name__ == '__main__':
    img_conv = ImageConvertor()

    # img_conv.simple_average()
    # img_conv.weighted_average(method=1)
    # img_conv.desaturation()
    # img_conv.decomposition()
    # img_conv.single_color_channel()
    # img_conv.gray_shades()
    # img_conv.floyd_steinberg()
    img_conv.burkes()
