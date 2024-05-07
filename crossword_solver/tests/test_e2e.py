from crossword_solver.solver_helpers import find_whole_crossword_candidates
from crossword_solver.crossword_solver import solve_crossword
from crossword_solver.crossword_detection import detect_crossword_from_file
from copy import deepcopy

path = '../data/pictures/ristsona_2.png'
crossword = detect_crossword_from_file(path)
find_whole_crossword_candidates(crossword)
results = solve_crossword(crossword)
printing_crossword = deepcopy(crossword)
for matrix, score, intersections in sorted(results, key=lambda x: x[2], reverse = True)[:5]:
    printing_crossword.matrix = matrix
    print(printing_crossword, round(score, 1), intersections)