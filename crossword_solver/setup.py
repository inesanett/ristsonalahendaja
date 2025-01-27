from setuptools import setup, find_packages

setup(
    name='crossword_solver',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here
        'numpy==1.26.4',
        'pandas==2.2.2',
        'wikipedia==1.4.0',
        'unidecode',
        'gensim==4.3.2',
        'scipy==1.12',
        'pytesseract==0.3.10',
        'Levenshtein==0.25.1',
        'pyarrow==16.0.0',
        'pillow==10.3.0',
        'Flask==3.0.3',
        'opencv-python==4.9.0.80',
    ],
    author='Ines Anett Nigol',
    author_email='ines.anett.nigol@ut.ee',
    description='Estonian crossword solver',
    license='MIT',
)