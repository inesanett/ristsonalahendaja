from copy import deepcopy
from crossword_solver.solver_utils import reorder_crossword_hints, solving_algorithm

def solve_crossword(crossword, max_empty_words = 6, max_solutions_count = 10):
    results = []
    solving_cw = deepcopy(crossword)
    new_hints = []
    for hint in solving_cw.hints:
        if len(hint.candidates)>0:
            new_hints.append(hint)
    solving_cw.hints = new_hints
    reorder_crossword_hints(solving_cw)

    results = [(0, 0, 0)]*max_solutions_count
    min_intersections = 0  
    min_score = 0  
    for matrix, score, intersections in solving_algorithm(solving_cw, max_empty_words=max_empty_words):
        if intersections > min_intersections or (intersections == min_intersections and score > min_score):
            results.pop(-1)
            results.append((matrix, score, intersections))
            results = sorted(results, key = lambda x: (x[2], x[1]), reverse = True)
            min_intersections = results[-1][2]
            min_score = results[-1][1]
    # Only keep solutions with a least one word filled in
    results = [r for r in results if r[1]>0]
    return results