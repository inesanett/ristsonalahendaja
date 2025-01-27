from enum import Enum
import itertools
import pickle
import numpy as np
        
class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3
    
class Hint():   
    def __init__(self, x, y, direction, hint, length, candidates=[]):
        self.x = x
        self.y = y
        self.direction = direction
        self.hint = hint
        self.length = length
        coordinates = []
        if direction == Direction.RIGHT:
            for i in range(1, length+1):
                coordinates.append((x+i, y))
        elif direction == Direction.LEFT:
            for i in range(1, length+1):
                coordinates.append((x-i, y))
        elif direction == Direction.UP:
            for i in range(1, length+1):
                coordinates.append((x, y-i))
        elif direction == Direction.DOWN:
            for i in range(1, length+1):
                coordinates.append((x, y+i))
        self.coordinates = coordinates
        self.x_max = max([c[0] for c in coordinates])
        self.x_min = min([c[0] for c in coordinates])
        self.y_max = max([c[1] for c in coordinates])
        self.y_min = min([c[1] for c in coordinates])
        self.candidates = candidates
        
    def __repr__(self):
        return self.hint

class Crossword():
    def __init__(self, width, height, hints, grid, image):
        self.width = width
        self.height = height
        self.hints = hints
        self.out_of_range_character = "■"
        self.unfilled_character = "_"
        self.hint_character = "1"
        self.multihint_character = "2"
        self.matrix = np.full((width, height), self.unfilled_character, dtype = str)
        self.score = 0
        self.intersections = 0
        self.grid = grid
        self.image = image

    def set_out_of_range_spaces(self, x_from, x_to, y_from, y_to):
        for x, y in itertools.product(range(x_from, x_to), range(y_from, y_to)):
            self.matrix[x, y] = self.out_of_range_character

    def __repr__(self):
        result = ""
        for row in self.matrix.T:
            result+=" ".join(row)+"\n"
        return result
    
def save_crossword(crossword, filepath):
    with open(filepath, "wb") as f:
        pickle.dump(crossword, f)

def load_crossword(filepath):
    with open(filepath, "rb") as f:
        file = pickle.load(f)
    return file