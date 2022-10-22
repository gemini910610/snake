import msvcrt
import os
import threading

'''
TODO
use seven-segment-led to display current length
'''


def show_map():
    os.system('cls')
    global map
    for row in range(8):
        for col in range(8):
            if map[col][7 - row] == 0:
                print('□', end='')
            elif map[col][7 - row] == 1:
                print('■', end='')
            else:
                print('x', end='')
        print()


def get_keyboard():
    global map, direction
    pressed = {'w': 0, 'd': 1, 's': 2, 'a': 3}
    while True:
        next_direction = pressed.get(msvcrt.getwch(), None)
        if (direction + 2) % 4 == next_direction or next_direction is None:
            continue
        direction = next_direction


def move(target, direction):
    match direction:
        case 0:
            target[1] += 1
        case 1:
            target[0] += 1
        case 2:
            target[1] -= 1
        case 3:
            target[0] -= 1
    if target[0] < 0:
        target[0] = 7
    elif target[0] > 7:
        target[0] = 0
    if target[1] < 0:
        target[1] = 7
    elif target[1] > 7:
        target[1] = 0


map = []
for i in range(8):
    map.append([0] * 8)
direction = 1  # 0: up, 1: right, 2: down, 3: left
head_position = [2, 0]
tail_position = [0, 0]
map[head_position[0]][head_position[1]] = 1
map[1][0] = 1
map[tail_position[0]][tail_position[1]] = 1
show_map()

lfsr = 1 << 15 | 1
def random():
    global bit, lfsr
    bit = (lfsr ^ (lfsr >> 1) ^ (lfsr >> 3) ^ (lfsr >> 12)) & 1
    lfsr = (lfsr >> 1) | (bit << 15)
    return lfsr % 8
for i in range(32):
    random()

fruit_x = 0
fruit_y = 0
def generate_fruit():
    global fruit_x, fruit_y
    x = random()
    y = random()
    while map[x][y] != 0:
        x = random()
        y = random()
    map[x][y] = -1
    fruit_x = x
    fruit_y = y
def eat_fruit():
    global length, fruit_x, fruit_y
    length += 1
    map[fruit_x][fruit_y] = 1
    generate_fruit()

generate_fruit()

threading.Thread(target=get_keyboard, daemon=True).start()
clock = 0
history = '0101'
length = 2
while True:
    clock = clock + 1
    if clock < 5000000:
        continue
    move(head_position, direction)
    history = history + f'{bin(direction)[2:]:>02}'
    if head_position[0] == fruit_x and head_position[1] == fruit_y:
        eat_fruit()
    elif map[head_position[0]][head_position[1]] == 1:
        print('you dead')
        break
    else:
        map[head_position[0]][head_position[1]] = 1
        map[tail_position[0]][tail_position[1]] = 0
        # TODO: modify following condition, maybe need to save all history direction, maybe use like queue to save
        # set                       get
        # 3 -> 11                   110101  -> 11                                 -> 0101
        # 1 -> 1101                 0101    -> 01                                 -> 01
        # 1 -> 110101               01      -> 01                                 -> 0
        # x -> history * 4 + x      history -> history >> (length * 2) -> history % 2**(length * 2)
        body_direction = int(bin(int(history, 2) >> (length * 2))[2:], 2)
        history = bin(int(history, 2) % 2 ** (length * 2))[2:]
        move(tail_position, body_direction)
    show_map()
    clock = 0
