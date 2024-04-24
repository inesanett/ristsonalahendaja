from dataclasses import dataclass
from enum import Enum
import itertools
import pickle
from crossword_solver.candidate_search_helpers import search_candidates, Candidate
        
class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3
    
class Hint():   
    def __init__(self, x, y, direction, hint, length):
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
        candidates = search_candidates(self.hint)
        filtered_candidates = [c for c in candidates if c.length() == self.length]
        self.candidates = sorted(filtered_candidates, key = lambda x: x.weight, reverse = True)
        
    def __repr__(self):
        return self.hint

class Crossword():
    def __init__(self, width, height, hints):
        self.width = width
        self.height = height
        self.hints = hints
        self.out_of_range_character = "■"
        self.unfilled_character = "_"
        self.matrix = [[self.unfilled_character]*width]*height
        self.score = 0
        for i in range(height): 
            # For loop to create new lists instead of instances of one list
            self.matrix[i] = self.matrix[i].copy()
        
    def set_out_of_range_spaces(self, x_from, x_to, y_from, y_to):
        for x, y in itertools.product(range(x_from, x_to), range(y_from, y_to)):
            self.matrix[y][x] = self.out_of_range_character

    def __repr__(self):
        result = ""
        for row in self.matrix:
            result+=" ".join(row)+"\n"
        return result
    
def save_crossword(crossword, filepath):
    with open(filepath, "wb") as f:
        pickle.dump(crossword, f)

def load_crossword(filepath):
    with open(filepath, "rb") as f:
        file = pickle.load(f)
    return file