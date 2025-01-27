from crossword_solver.candidate_search import search_candidates
import numpy as np
import re

def reorder_crossword_hints(crossword):
    hints = sorted([hint for hint in crossword.hints if "vastus" not in hint.hint], key=lambda x: x.length, reverse = True)
    ordered_hints = [hints.pop(0)]
    used_squares = set(ordered_hints[0].coordinates)
    while hints:
        for hint in hints:
            hint.overlap = len(set(hint.coordinates) & used_squares)
        hints = sorted(hints, key = lambda x:x.overlap, reverse = True)
        used_hint = hints.pop(0)
        ordered_hints.append(used_hint)
        used_squares = used_squares | set(used_hint.coordinates)
    crossword.hints = ordered_hints

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
    matching = ''.join(crossword.matrix[hint.x_min:hint.x_max+1, hint.y_min:hint.y_max+1].flatten()).replace('_', '.')
    suitable_candidates = []
    for c in hint.candidates:
        if re.match(matching, c.text):
            suitable_candidates.append(c)
    return suitable_candidates

def solving_algorithm(crossword, max_empty_words = 5):
    if len(crossword.hints)==0:
        yield np.copy(crossword.matrix), crossword.score, crossword.intersections
        return
    
    hint = crossword.hints.pop(0)
    suitable_candidates = find_suitable_candidates(hint, crossword)

    if len(suitable_candidates)==0 and max_empty_words==0:
        yield np.copy(crossword.matrix), crossword.score, crossword.intersections
    if max_empty_words>0:
        yield from solving_algorithm(crossword, max_empty_words-1)
    
    prev_text = np.copy(crossword.matrix[hint.x_min:hint.x_max+1, hint.y_min:hint.y_max+1])
    intersection_count = np.count_nonzero(prev_text != crossword.unfilled_character)
    crossword.intersections += intersection_count
    for candidate in suitable_candidates:
        crossword.matrix[hint.x_min:hint.x_max+1, hint.y_min:hint.y_max+1] = np.array(list(candidate.text)
                                                                                          ).reshape(prev_text.shape)
        crossword.score += candidate.weight
        yield from solving_algorithm(crossword, max_empty_words)
        crossword.score -= candidate.weight
        crossword.matrix[hint.x_min:hint.x_max+1, hint.y_min:hint.y_max+1] = prev_text
    crossword.intersections -= intersection_count
    crossword.hints.insert(0, hint)