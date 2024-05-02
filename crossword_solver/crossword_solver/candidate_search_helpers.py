import re
import unidecode
from dataclasses import dataclass
from gensim.models import KeyedVectors
import pandas as pd

# Wikipedia search
import wikipedia as wp
wp.set_lang('et')
MAX_WIKIPEDIA_RESULTS = 50
WIKI_TAG = 'viki'
WIKI_WEIGHT = 0.6

# WordNet search
from estnltk import download
download('wordnet')
from estnltk.wordnet import Wordnet
from estnltk import Text
WORDNET_TAG = 'wordnet'
WORDNET_LEMMAS_WEIGHT = 0.9
WORDNET_HYPONYMS_WEIGHT = 0.8
WORDNET_SIMILAR_WEIGHT = 0.8
WORDNET_VOCAB = 'wordnet vocab'
WORDNET_VOCAB_WEIGHT = 0.8
wn_voc = pd.read_parquet('../data/wordnet_contents.parquet')

# Abbreviation
ABBREVIATION_TAG = 'abbreviation'
ABBREVIATION_WEIGHT = 0.9

# Word2Vec
word2vec_model = KeyedVectors.load_word2vec_format('../data/lemmas.cbow.s100.w2v.bin', binary=True)
WORD2VEC_TAG = 'word2vec'
WORD2VEC_WEIGHT = 0.7
MAX_WORD2VEC_RESULTS = 20

@dataclass
class Candidate():
    text: str
    source: str
    weight: float = 1.0
        
    def length(self):
        return len(self.text)
    
    def __hash__(self):
        return hash(self.text)
    
    def __eq__(self, other):
        return self.text == other.text
        
# Text cleaning functions
def lemmatise_text(original):
    text = Text(original)
    text.tag_layer(['morph_analysis'])
    return ' '.join((t[0] for t in text.lemma))

def replace_accented_characters(text):
    # Replace accented characters keeping "õ", "ä", "ö", "ü"
    text = text.replace('õ', '_').replace('ä', '=').replace('ö', '>').replace('ü', '<')
    text = unidecode.unidecode(text)
    return text.replace('_', 'õ').replace('=', 'ä').replace('>', 'ö').replace('<', 'ü')

def remove_numbers(text):
    return re.sub(r'\d+', '', text)

def remove_punctuation(text):
    return re.sub(r'[^\w\s]', '', text)

def replace_multiple_spaces(text):
    return re.sub(r' +', ' ', text)

def clean_text(text):
    # Lowercase
    text = text.lower()
    # Remove bracketed parts
    text = re.sub(r'\([^)]*\)', '', text).strip()
    # Remove numbers
    text = remove_numbers(text)
    # Remove punctuation
    text = remove_punctuation(text)
    # Replace letters that do not exist in Estonian language
    text = replace_accented_characters(text)     
    # Remove unnecessary spaces
    text = replace_multiple_spaces(text)
    return text.strip()

# Create candidates
## Make new forms from text
def expand_candidate_text(text_list):
    # Add lemmas
    expanded_list = text_list + [lemmatise_text(text) for text in text_list]
    word_list = []
    for text in expanded_list:
        clean = clean_text(text)
        if ' ' in clean:
            # Separated form
            word_list.extend(clean.split())
            # Joint form
            word_list.append(clean.replace(' ', ''))
        else:
            word_list.append(clean)
    # Remove duplicates
    word_list = list(set(word_list))
    return word_list

## Create candidates from text
def create_candidates(word_list, tag, weight):
    return [Candidate(candidate, tag, weight) for candidate in word_list]

## Take in a list of words and return expanded candidates list
def convert_results_to_candidates(text_list, tag, weight):
    word_list = expand_candidate_text(text_list)
    return create_candidates(word_list, tag, weight)
    
# Wikipedia search
def wikipedia_search(text, max_wikipedia_results = MAX_WIKIPEDIA_RESULTS):
    query = lemmatise_text(text)
    if len(query) > 0:
        wiki_results = wp.search(query, results = max_wikipedia_results)
        return convert_results_to_candidates(wiki_results, WIKI_TAG, WIKI_WEIGHT)
    return []

# Wordnet search
def wordnet_search(text):
    wn = Wordnet()
    synsets = wn[text]
    lemmas = []
    hyponyms = []
    similar = []
    wordnet_candidates = []
    for synset in synsets:
        lemmas.extend(synset.lemmas)
        new_hyponyms = synset.get_related_synset("hyponym")
        new_similar = synset.get_related_synset("similar")
        for h in new_hyponyms:
            hyponyms.extend(h.lemmas)
        for s in new_similar:
            similar.extend(s.lemmas)
    wordnet_candidates.extend(convert_results_to_candidates(lemmas, WORDNET_TAG, WORDNET_LEMMAS_WEIGHT))
    wordnet_candidates.extend(convert_results_to_candidates(hyponyms, WORDNET_TAG, WORDNET_HYPONYMS_WEIGHT))
    wordnet_candidates.extend(convert_results_to_candidates(similar, WORDNET_TAG, WORDNET_SIMILAR_WEIGHT))
    return wordnet_candidates

# Wordnet vocabulary list search
def find_regex_match(hint_text, length, wn_list):
    if "..." not in hint_text:
        return []
    matching_group = f"(.{{{length}}})"
    pattern ="^"+ hint_text.replace("...", matching_group)+ "$"
    matches = []
    for w in wn_list:
        match = re.search(pattern, w)
        if match is not None:
            matches.append(match.group(1))
    if len(matches) > 0:
        return convert_results_to_candidates(matches, tag = WORDNET_VOCAB, weight = WORDNET_VOCAB_WEIGHT)
    return []

# Create abbreviation
def create_abbreviated_candidate(text, length):
    # Check if the number of words in the clue is equal to the length of the expected answer
    # If True, add abbrevated form of hint as a possible candidate
    splitted = text.split(" ")
    if len(splitted) == length:
        print(text, splitted, length )
        abbreviation = ''.join([word[0] for word in splitted]).lower()
        return convert_results_to_candidates([abbreviation], ABBREVIATION_TAG, ABBREVIATION_WEIGHT)
    return []

# Word2Vec search
def create_word2vec_candidates(text, max_results = MAX_WORD2VEC_RESULTS):
    lemmatised_text = lemmatise_text(text).lower()
    lemma_list = lemmatised_text.split(" ")
    # Filter out lemmas that exist in vocabulary
    filtered = [lemma for lemma in lemma_list if lemma in word2vec_model.key_to_index.keys()]
    if len(filtered) > 0:
        neighbours_info = word2vec_model.most_similar(positive = filtered, topn = max_results)
        neighbours = [neighbour[0] for neighbour in neighbours_info]
        return convert_results_to_candidates(neighbours, tag = WORD2VEC_TAG, weight = WORD2VEC_WEIGHT)
    return []

## Candidate cleaning
def remove_duplicates(candidate_list):
    return list(set(candidate_list))

def search_candidates(hint):
    hint_text = hint.hint
    length = hint.length
    candidate_list = []
    lemmatised_text = lemmatise_text(hint_text)
    if "vastus" in lemmatised_text:
        return candidate_list
    candidate_list.extend(wikipedia_search(lemmatised_text))
    candidate_list.extend(wordnet_search(lemmatised_text))
    candidate_list.extend(create_abbreviated_candidate(hint_text, length))
    candidate_list.extend(create_word2vec_candidates(lemmatised_text))
    candidate_list.extend(find_regex_match(hint_text, length, wn_voc['word']))
    candidate_list = remove_duplicates(candidate_list)
    sorted_candidates = sorted(candidate_list, key = lambda x: x.weight, reverse = True)
    return sorted_candidates