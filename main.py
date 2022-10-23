import msvcrt
import os
import threading

def number_to_segment(number):
    match number:
        case 0:
            return [1, 1, 1, 1, 1, 1, 0]
        case 1:
            return [0, 1, 1, 0, 0, 0, 0]
        case 2:
            return [1, 1, 0, 1, 1, 0, 1]
        case 3:
            return [1, 1, 1, 1, 0, 0, 1]
        case 4:
            return [0, 1, 1, 0, 0, 1, 1]
        case 5:
            return [1, 0, 1, 1, 0, 1, 1]
        case 6:
            return [0, 0, 1, 1, 1, 1, 1]
        case 7:
            return [1, 1, 1, 0, 0, 0, 0]
        case 8:
            return [1, 1, 1, 1, 1, 1, 1]
        case 9:
            return [1, 1, 1, 0, 0, 1, 1]

def display_count():
    global length
    digit_2 = length // 10
    digit_1 = length % 10
    segment_2 = number_to_segment(digit_2)
    segment_1 = number_to_segment(digit_1)
    print(' ', end='')
    print('─' if segment_2[0] == 1 else ' ', end='')
    print('   ', end='')
    print('─' if segment_1[0] == 1 else ' ')
    print('│' if segment_2[5] == 1 else ' ', end='')
    print(' ', end='')
    print('│' if segment_2[1] == 1 else ' ', end='')
    print(' ', end='')
    print('│' if segment_1[5] == 1 else ' ', end='')
    print(' ', end='')
    print('│' if segment_1[1] == 1 else ' ')
    print(' ', end='')
    print('─' if segment_2[6] == 1 else ' ', end='')
    print('   ', end='')
    print('─' if segment_1[6] == 1 else ' ')
    print('│' if segment_2[4] == 1 else ' ', end='')
    print(' ', end='')
    print('│' if segment_2[2] == 1 else ' ', end='')
    print(' ', end='')
    print('│' if segment_1[4] == 1 else ' ', end='')
    print(' ', end='')
    print('│' if segment_1[2] == 1 else ' ')
    print(' ', end='')
    print('─' if segment_2[3] == 1 else ' ', end='')
    print('   ', end='')
    print('─' if segment_1[3] == 1 else ' ')

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
    display_count()


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


def random():
    global bit, lfsr
    bit = (lfsr ^ (lfsr >> 1) ^ (lfsr >> 3) ^ (lfsr >> 12)) & 1
    lfsr = (lfsr >> 1) | (bit << 15)
    return lfsr % 8


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


map = []
for i in range(8):
    map.append([0] * 8)
direction = 1  # 0: up, 1: right, 2: down, 3: left
head_position = [2, 0]
tail_position = [0, 0]
map[head_position[0]][head_position[1]] = 1
map[1][0] = 1
map[tail_position[0]][tail_position[1]] = 1

lfsr = 1 << 15 | 1
for i in range(32):
    random()
fruit_x = 0
fruit_y = 0
generate_fruit()

threading.Thread(target=get_keyboard, daemon=True).start()
clock = 0
history = '0101'
length = 2

show_map()
while True:
    clock = clock + 1
    if clock < 5000000:
        continue
    move(head_position, direction)
    # 3 -> 11
    # 1 -> 1101
    # 1 -> 110101
    # x -> history << 2 + x
    history = history + f'{bin(direction)[2:]:>02}'
    if head_position[0] == fruit_x and head_position[1] == fruit_y:
        eat_fruit()
    elif map[head_position[0]][head_position[1]] == 1:
        print('you dead')
        break
    else:
        map[head_position[0]][head_position[1]] = 1
        map[tail_position[0]][tail_position[1]] = 0
        # 110101 -> 11 + 0101
        # 0101 -> 01 + 01
        # 01 -> 01 + 0
        # history -> history >> (length * 2) + history % 2 ** (length * 2)
        body_direction = int(bin(int(history, 2) >> (length * 2))[2:], 2)
        history = bin(int(history, 2) % 2 ** (length * 2))[2:]
        move(tail_position, body_direction)
    show_map()
    clock = 0
