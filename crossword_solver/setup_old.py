from setuptools import setup, find_packages

setup(
    name='crossword_solver',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here
        'numpy',
        'pandas',
        'estnltk',
        'wikipedia',
        'unidecode',
        'gensim',
        'scipy==1.12',
        'pytesseract',
        'Levenshtein',
        'pyarrow',
        'pillow',
        'flask',
        'opencv-python'
    ],
    author='Ines Anett Nigol',
    author_email='ines.anett.nigol@ut.ee',
    description='Estonian crossword solver',
    license='MIT',
)