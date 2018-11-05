from src.data_processing import load_cmu
from src.ngrams import ngram_frequency
from src.pronunciations import get_closest_sounding_words
from src.ipatoarpabet import translate as ph_translate
import operator
from src.data_processing import print_progress
from nltk import pos_tag
from src.string_similarity import levenshtein
from nltk.tokenize import wordpunct_tokenize
from nltk.tokenize import word_tokenize
from collections import defaultdict
from nltk.corpus import stopwords
from src.pronunciations import phonetic_translation, phonetic_distance
from gensim import models


cmu = load_cmu()

reverse_cmu = defaultdict(list)
for k, v in cmu.items():
    reverse_cmu[' '.join(v[0])].append(k)

def load_reverse_cmu():
    for k, v in cmu.items():
        print(k, v)
        break

def translate(context, pun_word, ngram_length=3):

    def switch_score(distance, frequency_difference):
        if frequency_difference == 0:
            return 0
        return frequency_difference / ((distance + 1) ** 2)

    pun_phone = phonetic_translation(pun_word)

    def phonetic_distance(cand_phone, switch_phone):

        try:
            if switch_word in cmu:
                switch_phone = cmu[switch_word][0]
            else:
                switch_phone = ph_translate(switch_word)[0].split()
        except:
            pass
        return levenshtein(cand_phone, switch_phone)

    words = context.split(" ")
    window = len(pun_word.split())
    pun_index = None
    try:
        for i in range(len(context.split())):
            if all(context.split()[i + w] == pun_word.split()[w] for w in range(window)):
                pun_index = i
                break
    except ValueError as e:
        return []

    print(pun_word)
    print(context)

    original_frequency = ngram_frequency(words[pun_index - 1:pun_index + (ngram_length - 1)])
    #     substituions = get_three_gram_wildcard(words[pun_index-1], words[pun_index+1])
    similar_words = get_closest_sounding_words(pun_word)
    grams = [[words[pun_index - 1], sim_word, words[pun_index + window]] for sim_word in similar_words]
    # print("Generating substitutions")
    substituions = {}
    for i, gram in enumerate(grams):
        substituions[' '.join(gram)] = ngram_frequency(gram)
        # print_progress(i+1, len(grams))
    ranked_candidates = []

    # print("Generating scores")
    for i, (sub, freq) in zip(range(len(substituions)), substituions.items()):

        switch_word = sub.split()[1]
        ph_d = phonetic_distance(pun_phone, pun_word)

        if ph_d <= 2:
            freq_d = freq - original_frequency
            # ranked_candidates.append((switch_word, switch_score(ph_d, freq_d)))
            ranked_candidates.append((switch_word, ph_d, freq_d))
    return list(sorted(ranked_candidates, key=operator.itemgetter(1), reverse=True))

def detect(sentence, max_window_size=1, threshold=1000):
    # split context into unigrams and bigrams
    normal_pos = {'ADJ', 'ADV', 'NOUN', 'VERB'}
    possible_indices = {}
    context = wordpunct_tokenize(sentence)
    print(context)
    pos = pos_tag(context, tagset='universal')
    for window_size in range(1, max_window_size+1):
        possible_indices[window_size] = []
        for i in range(1, len(context)-window_size):
            if all(pos[i][1] not in normal_pos for i in range(i,i+window_size)):
                continue
            freq = ngram_frequency(context[i-1:i+2])
            if freq < threshold:
                possible_indices[window_size].append(i)

    scores = {}
    for window_size, possible_i in possible_indices.items():
        for i in possible_i:
            if i > 0 and i < len(context) - window_size:

                translation_scores = translate(sentence, ' '.join(context[i:i+window_size]))
                if len(translation_scores) > 0:
                    scores[' '.join(context[i:i+window_size])] = translation_scores
            #
            # if i > 0 and i < len(context) - 2:
            #     translation_scores = translate(sentence, ' '.join(context[i:i+2]))
            #     if len(translation_scores) > 0:
            #         scores[' '.join(context[i:i+2])] = translation_scores[:3]
    # return scores
    return sorted(scores.items(), key=lambda x: x[1][1], reverse = True)

def is_Tom_Swifty(sentence, model):
    # do all the adverb stuff...
    # tom swifty has format [PROPER NOUN said ADVERB .]
    sentence = word_tokenize(sentence)
    pos = pos_tag(sentence)
    words = [p[0].lower() for p in pos]
    tags = [p[1] for p in pos]

    if 'NNP' not in tags[-4:]:
        return False

    noun_position = -1
    for i in range(len(tags)-1, 0, -1):
        if tags[i] == 'NNP':
            noun_position = i
            break

    candidates = []
    for i in range(noun_position+1, len(tags)):
        if tags[i] in {'VBD', 'RB'} and words[i] != 'said':
            candidates.append(words[i])

    # If the word is neither an adverb or verb, return false
    if len(candidates) == 0:
        return False

    prefs = defaultdict(list)
    for candidate in candidates:
        a, b = prefixes(candidate, 3)
        prefs[candidate].extend(b)

    for w in candidates:
        if w not in cmu:
            continue
        og_ph = cmu[w][0]
        for i in range(len(og_ph)):
            for j in range(i, len(og_ph)):
                if ' '.join(og_ph[i: j]) in reverse_cmu and j - i > 2:
                    prefs[w].extend(reverse_cmu[' '.join(og_ph[i: j])])

    search_sentence = ([w for w in sentence
                        if w.lower() not in stopwords.words('english')
                        and w not in candidates])

    max_score = -1
    best_pair = None

    scores = defaultdict(list)

    for candidate, words in prefs.items():
        for word in words:
            pair, score = word_sentence_similarity(word, search_sentence, model)
            if not pair:
                continue

            # print("Comparing", candidate, pair[0])
            # print("Phonetic distance: ", phonetic_distance(candidate, pair[0]) ** 3)
            score *= phonetic_distance(candidate, pair[0])
            scores[candidate].append((pair, score))
            if score > max_score:
                max_score = score
                best_pair = pair

    for k in scores:
        scores[k] = list(sorted(scores[k], key=lambda x: x[1], reverse=True))
    return list(sorted(scores.items(), key=lambda x: x[1][0][1], reverse=True))
    # return list(sorted(ret, key=lambda x: x[1], reverse=True))

def prefixes(word, threshold=None):

    if not threshold:
        stem = stemmer.stem(word)
        translation = phonetic_translation(stem)
        if stem in cmu:
            threshold = len(translation)
        else:
            threshold = len(translation) - 1

    ret = defaultdict(list)
    phonetics = phonetic_translation(word)
    seen = {word}

    for i in range(1, len(phonetics)):
        for k, v in cmu.items():
            if phonetics[:i] == v[0][:i] and k not in seen:
                if i >= threshold:
                    ret[i].append(k)
                    seen.add(k)
                # case for when perfect prefixes

                elif len(v[0]) == i and k not in seen:
                    ret[i].append(k)
                    seen.add(k)
    seen.remove(word)


    return ret, seen


def word_sentence_similarity(word, sentence, model, tokenize=False):
    if word not in model.vocab:
        return None, -1

    if tokenize:
        sentence = word_tokenize(sentence)
    max_score = -1
    max_pair = None
    for w in sentence:
        if w in model.vocab:
            score = model.similarity(word, w)
            if score > max_score:
                max_score = score
                max_pair = (word, w)
    return max_pair, max_score
