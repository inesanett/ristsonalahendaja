from crossword_solver.candidate_search_helpers import search_candidates
from crossword_solver.crossword_helpers import Crossword, Hint
import pandas as pd
import re
from copy import deepcopy

def find_suitable_candidates(hint, crossword):
    matching = ''.join([crossword.matrix[y][x] for x, y in hint.coordinates]).replace('_', '.')
    suitable_candidates = []
    for c in hint.candidates:
        if re.match(matching, c.text):
            suitable_candidates.append(c)
    return suitable_candidates

def solving_algorithm(crossword):
    if len(crossword.hints)==0:
        return [crossword]
    
    hint = crossword.hints[0]
    suitable_candidates = find_suitable_candidates(hint, crossword)
    if len(suitable_candidates)==0:
        return []
    
    results = []
    for candidate in suitable_candidates:
        new_crossword = deepcopy(crossword)
        for i, (x, y) in enumerate(hint.coordinates):
            new_crossword.matrix[y][x] = candidate.text[i]
        new_crossword.hints.pop(0)
        new_crossword.score += candidate.weight
        result = solving_algorithm(new_crossword)
        results.extend(result)
    return results