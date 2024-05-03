import cv2
import numpy as np

from crossword_solver.crossword_helpers import Crossword, Hint, Direction
from crossword_solver.crossword_detection_utils import get_grid_from_image
from crossword_solver.square_classification import classify_all_squares, SquareType
from crossword_solver.text_detection import detect_text_for_all_squares, clean_hint_text


def detect_crossword_from_file(path):
    img = cv2.imread(path)
    return detect_crossword(img)

def detect_crossword(image):
    grid = get_grid_from_image(image)
    detect_text_for_all_squares(grid)
    classify_all_squares(grid)
    hints = []
    for square in grid.flatten():
        square.text = clean_hint_text(square.text)
        if square.type == SquareType.HINT:
            hints.append(
                Hint(
                    square.grid_x, 
                    square.grid_y, 
                    square.hint_direction,
                    square.text,
                    square.hint_len))
        if square.type == SquareType.MULTIHINT:
            # TODO fix hints withmultiple \n\n 
            hint_texts = square.text.split("\n\n")
            right_hint = hint_texts[0]
            bottom_hint = hint_texts[-1]
            hints.append(
                Hint(
                    square.grid_x, 
                    square.grid_y, 
                    Direction.RIGHT,
                    right_hint,
                    square.right_hint_len))
            hints.append(
                Hint(
                    square.grid_x, 
                    square.grid_y, 
                    Direction.DOWN,
                    bottom_hint,
                    square.bottom_hint_len))

    crossword = Crossword(grid.shape[0], grid.shape[1], hints)
    
    for square in grid.flatten():
        if square.type == SquareType.IRRELEVANT:
            crossword.matrix[square.grid_x, square.grid_y] = crossword.out_of_range_character
        if square.type == SquareType.HINT:
            crossword.matrix[square.grid_x, square.grid_y] = crossword.hint_character
        if square.type == SquareType.MULTIHINT:
            crossword.matrix[square.grid_x, square.grid_y] = crossword.multihint_character

    return crossword