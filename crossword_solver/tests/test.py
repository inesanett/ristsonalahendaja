from crossword_solver.candidate_search_helpers import Candidate
from crossword_solver.crossword_helpers import Crossword, load_crossword
from crossword_solver.solver_helpers import solving_algorithm
import pandas as pd

# Read in WordNet contents
wn_voc = pd.read_parquet('../data/wordnet_contents.parquet')

# Read in crossword
cw = load_crossword('../data/crossword1.pickle')

cw.hints[0].candidates.append(Candidate("kaamel", "mina", 1))
cw.hints[1].candidates.append(Candidate("sebra", "mina", 1))
cw.hints[2].candidates.append(Candidate("ninasarvik", "mina", 1))
cw.hints[3].candidates.append(Candidate("gepard", "mina", 1))

t = solving_algorithm(cw)
t = sorted(t, key = lambda x:x.score)[::-1]
for solution in t:
    print(solution)
    print(solution.score)