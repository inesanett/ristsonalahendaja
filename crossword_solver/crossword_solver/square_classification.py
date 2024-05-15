from enum import Enum
from crossword_solver.crossword_utils import Direction
import re

class SquareType(Enum):
    HINT = 1 # contains text, adjacent squares are empty or filled
    MULTIHINT = 2 # contains multiple strands of text, both bottom and right squares are empty or filled
    EMPTY = 3 # white backgroud, to be filled
    IRRELEVANT = 4 # anything else, black or some image

def classify_square(square):
    if square.brightness < 0.65:
        return SquareType.IRRELEVANT
    if check_if_clean_text_empty(square.text):
        return SquareType.EMPTY
    if "\n\n" in square.text:
        return SquareType.MULTIHINT
    return SquareType.HINT

def classify_all_squares(grid):
    # Initial classification
    for square in grid.flatten():
        square.type = classify_square(square)

    # Making some corrections in case of problems
    for square in grid.flatten():
        if square.type not in (SquareType.HINT, SquareType.MULTIHINT):
            continue
        
        bottom_empty_length = 0
        right_empty_length = 0
        bottom_squares = grid[square.grid_x, square.grid_y+1:]
        right_squares = grid[square.grid_x+1:, square.grid_y]

        for s in bottom_squares:
            if not s.type == SquareType.EMPTY:
                break
            bottom_empty_length+=1
        for s in right_squares:
            if not s.type == SquareType.EMPTY:
                break
            right_empty_length+=1
        
        
        if bottom_empty_length + right_empty_length == 0:
            square.type = SquareType.IRRELEVANT
            continue
        if bottom_empty_length and right_empty_length:
            square.type = SquareType.MULTIHINT
            square.bottom_hint_len = bottom_empty_length
            square.right_hint_len = right_empty_length
            continue
        if bottom_empty_length>right_empty_length:
            square.type = SquareType.HINT
            square.hint_direction = Direction.DOWN
            square.hint_len = bottom_empty_length
        else: 
            square.type = SquareType.HINT 
            square.hint_direction = Direction.RIGHT
            square.hint_len = right_empty_length

def check_if_clean_text_empty(text):
    clean = text.replace("\n", " ")
    clean = clean.replace("-", "...")
    clean = re.sub(r'([^\w\s.-]|_)','.', clean)
    clean = re.sub(r'\.{2,}','...', clean)
    clean = re.sub(r'(?<!\.)\.(?!\.)', ' ', clean)
    clean = re.sub(r' +', ' ', clean)
    clean = clean.strip()
    return clean == ""