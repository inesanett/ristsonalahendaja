import re
import unidecode
from dataclasses import dataclass
from gensim.models import KeyedVectors

# Wikipedia search
import wikipedia as wp
wp.set_lang('et')
MAX_WIKIPEDIA_RESULTS = 50
WIKI_TAG = 'viki'
WIKI_WEIGHT = 0.7

# WordNet search
from estnltk import download
download('wordnet')
from estnltk.wordnet import Wordnet
from estnltk import Text
WORDNET_TAG = 'wordnet'
WORDNET_LEMMAS_WEIGHT = 0.9
WORDNET_HYPONYMS_WEIGHT = 0.8
WORDNET_SIMILAR_WEIGHT = 0.8

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
    
    
## Candidate search
def convert_results_to_candidates(results_list, tag, weight):
    return [Candidate(candidate, tag, weight) for candidate in results_list]
    
def wikipedia_search(query, max_wikipedia_results):
    wiki_results = wp.search(query, results = max_wikipedia_results)
    return convert_results_to_candidates(wiki_results, WIKI_TAG, WIKI_WEIGHT)

def lemmatise_text(original):
    text = Text(original)
    text.tag_layer(['morph_analysis'])
    return ' '.join((t[0] for t in text.lemma))

def wordnet_search(query):
    wn = Wordnet()
    synsets = wn[lemmatise_text(query)]
    lemmas = []
    hyponyms = []
    similar = []
    for synset in synsets:
        lemmas.extend(synset.lemmas)
        new_hyponyms = synset.get_related_synset("hyponym")
        new_similar = synset.get_related_synset("similar")
        for h in new_hyponyms:
            hyponyms.extend(h.lemmas)
        for s in new_similar:
            similar.extend(s.lemmas)
    wordnet_candidates = []
    wordnet_candidates.extend(convert_results_to_candidates(lemmas, WORDNET_TAG, WORDNET_LEMMAS_WEIGHT))
    wordnet_candidates.extend(convert_results_to_candidates(hyponyms, WORDNET_TAG, WORDNET_HYPONYMS_WEIGHT))
    wordnet_candidates.extend(convert_results_to_candidates(similar, WORDNET_TAG, WORDNET_SIMILAR_WEIGHT))
    return wordnet_candidates


## Candidate cleaning
def remove_duplicates(candidate_list):
    return list(set(candidate_list))

def replace_accented_characters(candidate):
    # Replace accented characters keeping "õ", "ä", "ö", "ü"
    candidate = candidate.replace('õ', '_').replace('ä', '=').replace('ö', '>').replace('ü', '<')
    candidate = unidecode.unidecode(candidate)
    candidate = candidate.replace('_', 'õ').replace('=', 'ä').replace('>', 'ö').replace('<', 'ü')
    return candidate

def remove_numbers(candidate):
    return re.sub(r'\d+', '', candidate)

def remove_punctuation(candidate):
    return re.sub(r'[^\w\s]', '', candidate)

def replace_multiple_spaces(candidate):
    return re.sub(r' +', ' ', candidate)

def clean_candidates(candidate_list):
    for candidate in candidate_list:
        # Lowercase
        c = candidate.text.lower()
        # Remove bracketed parts
        c = re.sub(r'\([^)]*\)', '', c).strip()
        # Remove numbers
        c = remove_numbers(c)
        # Remove punctuation
        c = remove_punctuation(c)
        # Replace letters that do not exist in Estonian language
        c = replace_accented_characters(c)     
        # Remove unnecessary spaces
        c = replace_multiple_spaces(c)
        candidate.text = c.strip()

        
## Expanding candidates
def create_joint_form(candidate_text, source, weight):
    new_form = candidate_text.replace(' ', '')
    new_source = source + ' joint'
    return Candidate(new_form, source = new_source, weight = weight)

def create_separated_forms(candidate_text, source, weight):
    new_candidates = []
    new_parts = candidate_text.split()
    new_source = source + ' separated'
    for part in new_parts:
        new_candidates.append(Candidate(part, source = new_source, weight = weight))
    return new_candidates

def create_new_forms_from_candidate_text(candidate_text, source, weight):
    new_candidates = []
    new_candidates.append(create_joint_form(candidate_text, source, weight))
    new_candidates.extend(create_separated_forms(candidate_text, source, weight))
    return new_candidates

def expand_candidate(candidate):
    text = candidate.text
    source = candidate.source
    weight = candidate.weight
    new_candidates = []
    if ' ' in text:
        new_candidates.extend(create_new_forms_from_candidate_text(text, source, weight))
    lemmatised_text = lemmatise_text(text)
    if ' ' in lemmatised_text:
        new_candidates.extend(create_new_forms_from_candidate_text(lemmatised_text, source, weight))
    return remove_duplicates(new_candidates)

def expand_candidates(candidate_list):
    new_candidates = candidate_list.copy()
    for candidate in candidate_list:
        new_candidates.extend(expand_candidate(candidate))
    return remove_duplicates(new_candidates)

def create_abbreviated_candidates(hint):
    # Check if the number of words in the clue is equal to the length of the expected answer
    # If True, add abbrevated form of hint as a possible candidate
    splitted = hint.hint.split(" ")
    if len(splitted) == hint.length:
        abbreviation = ''.join([word[0] for word in splitted]).upper()
        return convert_results_to_candidates([abbreviation], ABBREVIATION_TAG, ABBREVIATION_WEIGHT)
    return []

def create_word2vec_candidates(hint, max_results = MAX_WORD2VEC_RESULTS):
    splitted = hint.hint.split(" ")
    lemmas = [lemmatise_text(word).lower() for word in splitted]
    neighbours_info = word2vec_model.most_similar(positive=lemmas, topn = max_results)
    neighbours = [neighbour[0] for neighbour in neighbours_info]
    return convert_results_to_candidates(neighbours, tag = WORD2VEC_TAG, weight = WORD2VEC_WEIGHT)

## Find candidates from different sources
def search_candidates(query, max_wikipedia_results = MAX_WIKIPEDIA_RESULTS):
    wiki_candidates = wikipedia_search(query, max_wikipedia_results)
    wordnet_candidates = wordnet_search(query)
    candidate_list = wiki_candidates + wordnet_candidates
    clean_candidates(candidate_list)
    candidate_list = remove_duplicates(candidate_list)
    candidate_list = expand_candidates(candidate_list)
    return remove_duplicates(candidate_list)
    