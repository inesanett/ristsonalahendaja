from copy import deepcopy
from crossword_solver.solver_helpers import reorder_crossword_hints, solving_algorithm

def solve_crossword(crossword, max_empty_words = 8, min_score = 10, min_intersections = 10):
    results = []
    solving_cw = deepcopy(crossword)
    new_hints = []
    for hint in solving_cw.hints:
        if len(hint.candidates)>0:
            new_hints.append(hint)
    solving_cw.hints = new_hints
    reorder_crossword_hints(solving_cw)
    for matrix, score, intersections in solving_algorithm(solving_cw, max_empty_words=max_empty_words):
        if score > min_score and intersections>min_intersections:
            results.append((matrix, score, intersections))
    return results