import os

# Change this to your data folder path
DATA_FOLDER_PATH = '/app/crossword_solver/data'
#DATA_FOLDER_PATH = 'C:/Users/ianigol/Documents/MAGISTER/ristsonalahendaja/crossword_solver/data'

WORDNET_VOCAB_PATH = os.path.join(DATA_FOLDER_PATH, 'wordnet_contents.parquet')
WORD2VEC_PATH = os.path.join(DATA_FOLDER_PATH, 'lemmas.cbow.s100.w2v.bin')
FONT_PATH = os.path.join(DATA_FOLDER_PATH, 'Roboto-Regular.ttf')