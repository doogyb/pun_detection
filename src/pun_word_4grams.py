from __future__ import division
import json

import operator
import string

import pattern.en
from pprint import pprint
from data_processing import load_cmu
from ngrams import ng_word_tokenize, four_gram_wildcard, ng_word_tokenize2
from string_similarity import levenshtein
import nltk
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()
cmu = None


def pun_data(context, revolve_word=None):
    global cmu
    if not cmu:
        cmu = load_cmu()

    results = {}
    relevant_grams = relevant_grams_revolve(context, revolve_word) if revolve_word else relevant_four_grams(context)

    for gram, selected_word in relevant_grams:
        search_gram = ["***" if g == selected_word else g for g in gram]

        selected_index = gram.index(selected_word)
        four_grams = four_gram_wildcard(search_gram)
        words = " ".join(g for g in search_gram)

        results[words] = {}
        results[words]['frequency'] = four_grams[words] if words in four_grams else 0
        results[words]['selected_word'] = selected_word
        selected_word_ph = get_phoneme_case_insensitive(selected_word)
        results[words]['miss'] = selected_word_ph is None
        results[words]['index'] = context.index(selected_word)

        if selected_word:
            results[words]['selected_word_ph'] = selected_word_ph

        for other_gram, freq in four_grams.iteritems():
            if other_gram == words:
                continue

            sub_gram = {}
            sub_word = other_gram.split()[selected_index]
            replaced_word_ph = get_phoneme_case_insensitive(sub_word)

            if selected_word_ph and replaced_word_ph:
                sub_gram['phoneme_distance'] = levenshtein(replaced_word_ph, selected_word_ph)
                sub_gram['phoneme_as_character_distance'] = \
                    levenshtein("".join(replaced_word_ph), "".join(selected_word_ph))
                sub_gram['replaced_word_ph'] = replaced_word_ph

            else:
                sub_gram['phoneme_distance'] = 'miss'

            sub_gram['character_distance'] = levenshtein(sub_word, selected_word)
            sub_gram["gram"] = other_gram
            sub_gram['frequency'] = freq
            sub_gram['replaced_word'] = sub_word

            results[words][other_gram] = sub_gram

    return results


def get_phoneme_case_insensitive(word):
    if word in cmu:
        return cmu[word][0]
    if word.lower() in cmu:
        return cmu[word.lower()][0]
    return None


def best_word(data):

    # TODO preference for second last quadgram (quadgram without full stop)

    local_max = -10000000
    scores = {}
    for gram, sub_gram in data.iteritems():
        gram_score = -1000000
        selected_word = data[gram]['selected_word']

        for values in sub_gram.values():
            if isinstance(values, dict):
                # check if word is plural form
                replaced_word = values['replaced_word']

                if check_inflections(selected_word, replaced_word):
                    continue
                if 'selected_word_ph' in data:
                    score = calculate_score(values, selected_word, data['selected_word_ph'])
                else:
                    score = calculate_score(values, selected_word, False)
                if score == "skip":
                    continue
                score -= (data[gram]['frequency'])

                if replaced_word in scores:
                    if score > scores[replaced_word]:
                        scores[replaced_word] = score
                else:
                    scores[replaced_word] = score

                # score += data[gram]['index'] * 2

                if score > local_max:
                    best_gram = values
                    best_original_gram = gram
                    # print gram
                    local_max = score
                    best_word = data[gram]['selected_word']
                    # print best_gram
                    # print score
                    # print best_original_gram
                    # print local_max

                if gram_score < score:
                    best_local_gram = values
                    gram_score = score

        # print "Best local gram for ", gram, ": ", best_local_gram
        # print "with score: ", gram_score

    # print best_gram['replaced_word'], local_max
    # print best_original_gram
    # if best_gram:
    #     return best_gram['replaced_word']
    # else:
    #     return "--blank--"
    # print scores
    if len(scores.keys()) >= 1:
        return sorted(scores.items(), key=operator.itemgetter(1), reverse=True)[0][0]
    # return [["--blank--", 0]]
    return "--blank--"


def is_pun(data):
    # TODO preference for second last quadgram (quadgram without full stop)
    local_max = -10000000
    best_score = -1000000
    scores = {}
    for gram, sub_gram in data.iteritems():
        selected_word = data[gram]['selected_word']

        for values in sub_gram.values():
            if isinstance(values, dict):
                # check if word is plural form
                replaced_word = values['replaced_word']

                if check_inflections(selected_word, replaced_word):
                    continue
                if 'selected_word_ph' in data:
                    score = calculate_score(values, selected_word, data['selected_word_ph'])
                else:
                    score = calculate_score(values, selected_word, False)
                if score == "skip":
                    continue
                score -= (data[gram]['frequency'])

                if replaced_word in scores:
                    if score > scores[replaced_word]:
                        scores[replaced_word] = score
                else:
                    scores[replaced_word] = score

                if score > local_max:
                    local_max = score
                    best_score = score

    return best_score


def relevant_four_grams(context):

    exclude_list_pos = ['CC', 'RB', 'WRB' 'CD', 'DT', 'IN', 'NNP',
                        'NNPS', 'PRP', 'PRP$', 'TO', ",", ".", ":", "'", '"']
    exclude_list_words = ['was', "'", "'ve", 'a', "I", "in"]
    grams = []
    # sent = nltk.sent_tokenize(context)[-1]
    tokens = ng_word_tokenize(context)
    tagged = nltk.pos_tag(tokens)
    for i in xrange(len(tagged) - 3):
        # must have at least two content words
        if len([tg for tg in tagged[i:i+4] if tg[1] not in exclude_list_pos]) >= 2:
            for tg in tagged[i+1:i+4]:
                if tg[0] not in exclude_list_words and tg[1] not in exclude_list_pos:
                    grams.append(([w[0] for w in tagged[i:i+4]], tg[0]))

    if len(tokens[-4:]) != 4:
        return []

    return grams


def split_four_grams(context):

    grams = []
    sent = nltk.sent_tokenize(context)[-1]
    tokens = ng_word_tokenize2(sent)
    for gram in [tokens[i:i+4] for i in xrange(len(tokens)-3)]:
        if gram[0] not in string.punctuation:
            grams.append(gram)
    return grams


def relevant_grams_revolve(context, word):
    tokens = ng_word_tokenize(context)
    grams = []
    for i in xrange(len(tokens) - 3):
        if word in tokens[i:i+4] and word != tokens[i]:
            grams.append((tokens[i:i+4], word))
    return grams


def check_inflections(original_word, other_word):
    try:
        if pattern.en.pluralize(original_word) == other_word:
            return True
        if original_word == other_word.lower():
            return True
        if stemmer.stem(original_word) == stemmer.stem(other_word):
            return True
        return False
    except:
        return False


def calculate_score(data, selected_word, selected_word_ph):

    word = data['replaced_word']
    distance_ratio_ph = 0
    distance_ratio_phch = 0

    if data['phoneme_distance'] != 'miss':
        phoneme = data['replaced_word_ph']
        distance_ratio_ph = (len(phoneme) - data['phoneme_distance']) / len(phoneme)
        distance_ratio_phch = (len("".join(phoneme)) - data['phoneme_as_character_distance']) / len("".join(phoneme))

    distance_ratio_ch = (len(word) - data['character_distance']) / len(word)
    distance_ratio = max(distance_ratio_ph, distance_ratio_phch, distance_ratio_ch)

    if distance_ratio <= 0:
        return "skip"

    # temper scores based on first phoneme
    if data['phoneme_distance'] != 'miss' and selected_word_ph:
        # print phoneme, cmu[selected_word]
        if phoneme[0] == selected_word_ph[0]:
            return data['frequency'] - (1 / distance_ratio ** 10)
    else:
        if word[0] == selected_word[0]:
            return data['frequency'] - (1 / distance_ratio ** 15)

    return data['frequency'] - (1 / distance_ratio ** 20)
    # return data['frequency'] - (1 / distance_ratio ** 10)


if __name__ == "__main__":
    # print best_word(pun_data("Two snakes parted , and one said , ' fangs for the memories ' .", 'fangs'))
    # print pun_data("\"I'm halfway up a mountain,\" Tom alleged.")
    # print best_word(pun_data("Two snakes parted , and one said , ' fangs for the memories ' .", 'fangs'))
    pass