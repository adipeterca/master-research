from PIL import Image, ImageDraw
import numpy as np

class Pixels:
    BG_COLOR = (244, 255, 51)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

size = 512
image = Image.new('RGB', (size, size))
draw = ImageDraw.Draw(image)

# Draw the face shape
r = size / 2
draw.ellipse([(0, 0), (size, size)], fill=Pixels.BG_COLOR)

# Draw the left eye
x = (size / 4) * 1.4
y = size / 4
r = size * 0.2
draw.ellipse([(x-r, y-r), (x+r, y+r*2)], fill=Pixels.WHITE, outline=Pixels.BLACK)
draw.ellipse([(x-r*0.7, y-r*0.7), (x+r*0.7, y+r*1.8)], fill=Pixels.GREEN)

# Draw the right eye
x = size / 4 * 3
y = size / 4
r = size * 0.2
draw.ellipse([(x-r, y-r), (x+r, y+r*2)], fill=Pixels.WHITE, outline=Pixels.BLACK)
draw.ellipse([(x-r*0.7, y-r*0.7), (x+r*0.7, y+r*1.8)], fill=Pixels.GREEN)

# Draw the mouth
x1 = size / 12 * 3
y1 = size / 2
x2 = size - x1
y2 = y1 + size * 0.4
draw.chord((x1, y1, x2, y2), start=0, end=180, fill=Pixels.WHITE, outline=Pixels.BLACK)
# draw.chord((125, 50, 375, 200), start=30, end=270, fill=(255, 255, 0), outline=(0, 0, 0))
image.show()
# image.save('emoji.png')