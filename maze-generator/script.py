from PIL import Image
import numpy as np
from random import randint, random
FILL = 0
EMPTY = 255

def array2d_to_list(arr, n) :
    res = []
    for i in range(n):
        for j in range(n):
            res.append(arr[i][j])
    return res

def generate(max_count, _map, i_start, j_start):
    i = i_start
    j = j_start
    count = 0
    while i >= 0 and j >= 0 and i < size and j < size and count < max_count:
        _map[i][j] = EMPTY
        i += randint(-1, 1)
        j += randint(-1, 1)
        count += 1

def generate2(_map):
    for i in range(len(_map)):
        for j in range(len(_map[0])):
            if j % 2 == 0 and i % 2 == 0:
                _map[i][j] = EMPTY
    
    for i in range(len(_map)):
        for j in range(len(_map[0])):
            if j % 2 == 1 and random() < 0.4:
                _map[i][j] = EMPTY
                if random() < 0.7:
                    j += randint(1, 4)

def generate3(_map, start_i, start_j, max_count = 1000):
    min_dist = 2
    max_dist = 10
    i = start_i
    j = start_j
    count = 0
    while i >= 0 and j >= 0 and i < size and j < size and count < max_count:
        direction = randint(1, 4)
        distance = randint(min_dist, max_dist)
        count += 1
        if direction == 1:
            while i >= 0 and j >= 0 and i < size and j < size and distance > 0:
                _map[i][j] = EMPTY
                i += -1
                j += 0
                distance -= 1
        elif direction == 2:
            while i >= 0 and j >= 0 and i < size and j < size and distance > 0:
                _map[i][j] = EMPTY
                i += 0
                j += 1
                distance -= 1
        elif direction == 3:
            while i >= 0 and j >= 0 and i < size and j < size and distance > 0:
                _map[i][j] = EMPTY
                i += 1
                j += 0
                distance -= 1
        else:
            while i >= 0 and j >= 0 and i < size and j < size and distance > 0:
                _map[i][j] = EMPTY
                i += 0
                j += -1
                distance -= 1

size = 256
img = Image.new('L', (size, size))
l = np.zeros((size, size))

# for i in range(800):
#     generate(50, l, randint(0, size-1), randint(0, size-1))
# for i in range(2500):
#     generate(15, l, randint(0, size-1), randint(0, size-1))
# generate2(l)

# Best approach
for i in range(size):
    for j in range(size):
        if i % (size // 10) == 0 and j % (size // 10) == 0:
            generate3(l, i, j, 50)

img.putdata(array2d_to_list(l, size))
img.save('phto.png')