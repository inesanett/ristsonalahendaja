import cv2
import re
from crossword_solver.crossword_utils import Crossword, Hint, Direction
from crossword_solver.grid_detection import get_grid_from_image, crop_image_to_crossword_outline
from crossword_solver.square_classification import classify_all_squares, SquareType
from crossword_solver.text_detection import detect_text_for_all_squares

def detect_crossword_from_file(path):
    img = cv2.imread(path)
    return detect_crossword(img)

def detect_crossword(image):
    cropped_image = crop_image_to_crossword_outline(image)
    grid = get_grid_from_image(cropped_image)
    detect_text_for_all_squares(grid)
    classify_all_squares(grid)
    hints = []
    for square in grid.flatten():
        if square.type == SquareType.HINT:
            clean = join_rows(square.text)
            clean = clean_text(clean)
            square.text = clean
            hints.append(
                Hint(
                    square.grid_x, 
                    square.grid_y, 
                    square.hint_direction,
                    square.text,
                    square.hint_len))
        if square.type == SquareType.MULTIHINT:
            clean = join_rows(square.text)
            if "\n\n" in clean:
                split_hints = clean.split("\n\n")
                hint1 = " ".join(split_hints[:-1])
                hint2 = " ".join(split_hints[1:])
            else:
                hint1 = hint2 = clean
            hint1 = clean_text(hint1)
            hint2 = clean_text(hint2)
            hints.append(
                Hint(
                    square.grid_x, 
                    square.grid_y, 
                    Direction.RIGHT,
                    hint1,
                    square.right_hint_len))
            hints.append(
                Hint(
                    square.grid_x, 
                    square.grid_y, 
                    Direction.DOWN,
                    hint2,
                    square.bottom_hint_len))
    crossword = Crossword(grid.shape[0], grid.shape[1], hints, grid, cropped_image)
    
    for square in grid.flatten():
        if square.type == SquareType.IRRELEVANT:
            crossword.matrix[square.grid_x, square.grid_y] = crossword.out_of_range_character
        if square.type == SquareType.HINT:
            crossword.matrix[square.grid_x, square.grid_y] = crossword.hint_character
        if square.type == SquareType.MULTIHINT:
            crossword.matrix[square.grid_x, square.grid_y] = crossword.multihint_character

    return crossword

def join_rows(text):
    clean = text.strip()
    clean = clean.replace("-\n\n", "")
    clean = clean.replace("-\n", "")
    return clean

def clean_text(text):
    clean = text.replace("\n", " ")
    clean = clean.replace("-", "...")
    clean = re.sub(r'([^\w\s.-]|_)','.', clean)
    clean = re.sub(r'\.{2,}','...', clean)
    clean = re.sub(r'(?<!\.)\.(?!\.)', ' ', clean)
    clean = re.sub(r' +', ' ', clean)
    clean = clean.strip()
    return clean