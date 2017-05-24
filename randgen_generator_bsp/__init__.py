# -*- coding: utf-8 -*-
import random
from randgen_maptools import coord_to_1d_index


__author__ = 'Dan Alexander'
__email__ = 'lxndrdagreat@gmail.com'
__version__ = '0.1.1'


"""
Parameter Schema
"""
schema = {
    'width': {
        'type': 'integer',
        'min': 25,
        'coerce': int,
        'required': True,
        'default': 50
    },
    'height': {
        'type': 'integer',
        'min': 25,
        'coerce': int,
        'required': True,
        'default': 50
    },
    'min_size': {
        'type': 'integer',
        'min': 3,
        'coerce': int,
        'required': True,
        'default': 5
    },
    'max_size': {
        'type': 'integer',
        'min': 5,
        'coerce': int,
        'required': True,
        'default': 12
    }
}


def tunnel(a, b, tiles, map_width, floor=0):
    """
    Used to connect two rooms together
    """
    x = a[0] + random.randint(0, a[2]-1)
    y = a[1] + random.randint(0, a[3]-1)

    ex = b[0] + random.randint(0, b[2]-1)
    ey = b[1] + random.randint(0, b[3]-1)

    while x != ex or y != ey:

        if x < ex:
            x += 1
        elif x > ex:
            x -= 1
        else:
            if y < ey:
                y += 1
            elif y > ey:
                y -= 1

        index = coord_to_1d_index(x, y, map_width)
        tiles[index] = floor


def connect(node, tiles, map_width, min_cell_width, min_cell_height, rooms, wall=1, floor=0):
    """
    Traverses the BSP tree recursively, connecting leaves.
    """
    if node['top'] and node['bottom']:
        top = connect(node['top'], tiles, map_width, min_cell_width, min_cell_height, rooms)
        bottom = connect(node['bottom'], tiles, map_width, min_cell_width, min_cell_height, rooms)

        tunnel(top, bottom, tiles, map_width, floor)

        return top
    elif node['left'] and node['right']:
        left = connect(node['left'], tiles, map_width, min_cell_width, min_cell_height, rooms)
        right = connect(node['right'], tiles, map_width, min_cell_width, min_cell_height, rooms)

        tunnel(left, right, tiles, map_width, floor)

        return left
    else:
        border = 1
        x = node['x'] + border
        y = node['y'] + border
        w = random.randint(min_cell_width, node['width'] - border * 2)
        h = random.randint(min_cell_height, node['height'] - border * 2)

        for xx in range(x, x + w):
            for yy in range(y, y + h):
                index = coord_to_1d_index(xx, yy, map_width)
                tiles[index] = floor

        rooms.append((x, y, w, h))

        return x, y, w, h


def bsp_rect(x, y, width, height, min_width, min_height):
    """
    Generates the BSP tree
    """
    this_rect = {
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'top': None,
        'bottom': None,
        'left': None,
        'right': None
    }

    split = random.randint(0, 100)
    chance = 50
    if width < height * 0.5:
        chance = 10
    elif height < width * 0.5:
        chance = 90

    if split < chance:
        if width < min_width * 2 + 2:
            # build a room here
            return this_rect
        else:
            split_x = random.randint(min_width, width - min_width)
            this_rect['left'] = bsp_rect(x, y, split_x, height, min_width, min_height)
            this_rect['right'] = bsp_rect(x + split_x, y, width - split_x, height, min_width, min_height)
    else:
        if height < min_height * 2 + 2:
            return this_rect
        else:
            split_y = random.randint(min_height, height - min_height)
            this_rect['top'] = bsp_rect(x, y, width, split_y, min_width, min_height)
            this_rect['bottom'] = bsp_rect(x, y + split_y, width, height - split_y, min_width, min_height)

    return this_rect


def main(params):
    width = params['width']
    height = params['height']
    min_room_size = params['min_size']
    max_room_size = params['max_size']
    seed = params['seed']

    random.seed(seed)

    wall = 1
    floor = 0

    tiles = [wall] * (width * height)

    # leave outer border alone
    bsp = bsp_rect(1, 1, width - 2, height - 2, max_room_size, max_room_size)

    rooms = []
    connect(bsp, tiles, width, min_room_size, min_room_size, rooms, wall, floor)

    dungeon = {
        "width": width,
        "height": height,
        "tiles": tiles,
        'rooms': rooms
    }

    return dungeon
