from crossword_solver.crossword_utils import Direction, Hint, Crossword, save_crossword

hints = []
h = Hint(5, 0, Direction.DOWN, "kahe küüruga loom", 6)
hints.append(h)
h = Hint(0, 2, Direction.RIGHT, "must-valge loom", 5)
hints.append(h)
h = Hint(7, 1, Direction.DOWN, "loom, kellel on sarv ninal", 10)
hints.append(h)
h = Hint(3, 5, Direction.RIGHT, "täpiline kaslane", 6)
hints.append(h)
h = Hint(5, 7, Direction.RIGHT, "mesikäpp", 4)
hints.append(h)

# Animal crossword for children
cw = Crossword(10, 12, hints)
# Left side
cw.set_out_of_range_spaces(0, 5, 0, 2)
cw.set_out_of_range_spaces(0, 5, 3, 5)
cw.set_out_of_range_spaces(0, 1, 2, 3)
cw.set_out_of_range_spaces(0, 4, 5, 12)
cw.set_out_of_range_spaces(4, 7, 8, 12)
cw.set_out_of_range_spaces(4, 5, 6, 8)
cw.set_out_of_range_spaces(5, 6, 7, 8)
# Right side
cw.set_out_of_range_spaces(6, 10, 0, 2)
cw.set_out_of_range_spaces(5, 6, 0, 1)
cw.set_out_of_range_spaces(6, 7, 2, 5)
cw.set_out_of_range_spaces(8, 10, 2, 5)
cw.set_out_of_range_spaces(6, 7, 6, 7)
cw.set_out_of_range_spaces(8, 10, 6, 7)
cw.set_out_of_range_spaces(8, 10, 8, 12)

save_crossword(cw, '../data/crossword1.pickle')