from crossword_solver.crossword_detection import detect_crossword
from crossword_solver.solver_helpers import solving_algorithm

def solve_crossword(image):
    crossword = detect_crossword(image)
    solutions = solving_algorithm(crossword)
    raise NotImplementedError