
# coding: utf-8

# In[20]:


from src.data_processing import load_data
import itertools
import string

from src.ngrams import *
from src.string_similarity import levenshtein
import operator
from src.data_processing import print_progress
from nltk import word_tokenize, pos_tag
from src.data_processing import load_cmu
from src.ipatoarpabet import translate
from string import punctuation
from src.pronunciations import phonetic_distance
import os, sys
from pattern.en import lexeme
from src.pronunciations import get_closest_sounding_words as csw
# from src.pun_algorithms import *
from collections import defaultdict

with open("data/ngram_searchspace/ngram_totals.json") as f:
    search_space = json.load(f)

task1, task2, task3, min_pairs, strings, pun_strings = load_data()
cmu = load_cmu()

def score(original_frequency, new_frequency, original_word, new_word, position):
    return ( (new_frequency - original_frequency)
           * ((phonetic_distance(original_word, new_word, translated=True)**2)
           * position)) # pos is normalised

def sort_answers(unsorted_dict):
    sd = {}
    for k, d in unsorted_dict.items():
        sd[k] = sorted(d.items(), key=lambda x: x[1], reverse=True)
    return sd

accepted_pos = {'ADV', 'ADJ', 'VERB', 'NOUN'}

def rank_substitutions(index):

    full_path = "results/{}/{}".format(path, index)
#     print(full_path)

#     if os.path.exists(full_path):
#         print(index)
#         with open(full_path) as f:
#             res = json.load(f)
#         return res

    space = search_space[index]
    context = task1[index]['words']

    # takes in list of subs, context is list of words
    res = defaultdict(dict)
    context_length = len(context)

    for trigram, candidate in space.items():

        # No Pos experiment, set to 1
        position = context.index(trigram.split()[1])
        end_position = context_length - position

        # take position and normalise it wrt length of context
        if use_position:
            normal_position = position / context_length
        else:
            normal_position = 1

        original_freq = candidate['original_frequency']
        original_word = trigram.split()[1]

        if original_word in cmu:
            original_ph = cmu[original_word][0]
        else:
            # skip words not in new cmu
            continue

        if use_filter:
            phoneme_filter = set(csw(original_word))

        try:
            lexemes = lexeme(original_word)
        except:
            lexemes = []
        for sub, new_freq in candidate['substitutions'].items():

            new_word = sub.split()[1]


            if use_filter:
                if new_word not in phoneme_filter:
                    continue

            # ignore lexical derivatives
            if new_word in lexemes:
                continue

            new_context = [w for w in context]
            new_context[position-1:position+2] = sub.split()


            if new_word in cmu:
                new_ph = cmu[new_word][0]
            else:
                # skip words not in new cmu
                continue

            if any([w in string.punctuation for w in new_word]):
                continue

            tags = ([w[1] for w in
                     pos_tag(new_context, tagset='universal')])

            if tags[position] not in accepted_pos:
                continue

            s = score(original_freq,
                      new_freq,
                      original_ph,
                      new_ph,
                      normal_position)

            res[trigram][sub] = s



    with open(full_path, 'w') as f:
        json.dump(sort_answers(res), f, indent=4)

    return sort_answers(res)

path = sys.argv[1]
use_filter, use_position = [s.lower() == 'true' for s in sys.argv[2:]]

import time
before = time.time()
from multiprocessing import Pool
p = Pool(4)
ngram_search_space = p.map(rank_substitutions, range(len(task1)))
length = time.time() - before
print("Total time taken in seconds: {}".format(length))
