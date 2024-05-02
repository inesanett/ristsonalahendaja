from crossword_solver.candidate_search_helpers import search_candidates
from crossword_solver.crossword_helpers import Crossword, Hint
import pandas as pd
import re
from copy import deepcopy

def find_whole_crossword_candidates(crossword):
    for hint in crossword.hints:
        all_candidates = search_candidates(hint)
        # Only save candidates with the right length
        filtered = []
        for c in all_candidates:
            if len(c.text) == hint.length:
                filtered.append(c)
        hint.candidates = filtered

def find_suitable_candidates(hint, crossword):
    matching = ''.join([crossword.matrix[x, y] for x, y in hint.coordinates]).replace('_', '.')
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
    
    results = []
    new_crossword = deepcopy(crossword)
    new_crossword.hints.pop(0)
    result = solving_algorithm(new_crossword)
    results.extend(result)
    for candidate in suitable_candidates:
        new_crossword = deepcopy(crossword)
        for i, (x, y) in enumerate(hint.coordinates):
            new_crossword.matrix[y][x] = candidate.text[i]
        new_crossword.hints.pop(0)
        new_crossword.score += candidate.weight
        result = solving_algorithm(new_crossword)
        results.extend(result)
    return results

def display_results(solving_algorithm_results):
    sorted_results = sorted(solving_algorithm_results, key = lambda x:x.score)[::-1]
    for solution in sorted_results:
        print(solution.score)
        print(solution)
    return