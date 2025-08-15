#utils.py

import math

X = 0
Y = 1

def get_distance(pos1:tuple[float, float],pos2:tuple[float, float]):
    return math.sqrt(pow((pos1[X] - pos2[X]),2) + pow((pos1[Y] - pos2[Y]),2))

def min(values: list):
    min = values[0]
    for value in values:
        if value < min:
            min = value
    return min

def max(values: list, index=0):
    max = values[index]

    for index, value in enumerate(values):
        if value > max:
            max = value
            max_index = index
    return max, max_index