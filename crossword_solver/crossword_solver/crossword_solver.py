from crossword_solver.crossword_detection import detect_crossword_from_file
from crossword_solver.solver_helpers import reorder_crossword_hints, find_whole_crossword_candidates, solving_algorithm

def solve_crossword(path):
    crossword = detect_crossword_from_file(path)
    reorder_crossword_hints(crossword)
    find_whole_crossword_candidates(crossword)
    solutions = solving_algorithm(crossword)
    return solutions