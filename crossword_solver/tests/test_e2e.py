from crossword_solver.common_helpers import load_image
from crossword_solver.crossword_solver import solve_crossword

image = load_image('ristsona.png')

solution = solve_crossword(image)
print(solution)