# -*- coding: utf-8 -*-
import json
import xml.etree.ElementTree as ET
import sys
import numpy as np
import itertools
import xmltodict
from nltk import word_tokenize
from nltk.corpus import wordnet as wn, cmudict
from sklearn.preprocessing import normalize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk import pos_tag
import os

lm = WordNetLemmatizer()
stemmer = PorterStemmer()

def scores_as_matrix(path):

    def ranked_vectors(path, is_file=True):
        subs = []
        for index in range(1780):
            print_progress(index, 1780)
            full_path = "results/{}/{}".format(path, index)
            f = open(full_path)
            subs.append(json.load(f))
            f.close()
        return subs

    def number_of_substitutions(index, subs):
        tot_sum = 0
        for k, v in subs[index].items():
            tot_sum += len(v)
        return tot_sum

    def generate_ranked_vector(index, mvl, subs):
        vec = [0] * mvl
        scores = []
        for k, v in subs[index].items():
            scores.extend([score[1] for score in v])

        scores = list(sorted(scores, reverse=True))
        for i, j in zip(range(mvl), range(len(scores))):
            vec[i] = scores[i]
        return vec

    subs = ranked_vectors(path)
    max_columns = 10000

    max_vector_length = (min(max(number_of_substitutions(i, subs)
                             for i in range(1780)),
                             max_columns))

    vectors = ([generate_ranked_vector(i, max_vector_length, subs)
                for i in range(1780)])

    X = np.array(vectors)
    X = normalize(X)

    return X

def scores_as_list(path):

    import os
    if os.path.isfile("results/" + path + ".json"):
        print("returning from json")
        f = open("results/" + path + ".json")
        subs = json.load(f)
        f.close()
        return subs
    subs = []
    for index in range(1780):
        print_progress(index, 1780)
        full_path = "results/{}/{}".format(path, index)
        f = open(full_path)
        subs.append(json.load(f))
        f.close()
    return subs

def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def annotate_subtask3():
    tree = ET.parse("../data/subtask3-homographic-test.xml")
    root = tree.getroot()
    count = 0
    skip = 400
    pun_word = ""
    with open("../data/subtask3-annotations-full.tsv") as in_file:
        lines = in_file.read().split("\n")

    with(open("../data/subtask3-annotations-full-2.tsv")) as f:
        already_written = len(f.read().split("\n"))

    with open("../data/subtask3-annotations-full-2.tsv") as out_file:
        for count, line in enumerate(lines):
            if count <= already_written:
                continue
            print("\n\n\n\t\t\t\t", count, "\n\n\n")
            print(line)
            original_word = line.split("\t")[2]
            print(original_word)
            senses = wn.synsets(original_word)
            if len(senses) == 0:
                continue
            if len(senses) == 1:
                out_file.write(line + "\t" + senses[0].lemmas()[0].key() + "\t")

            else:
                for i, s in enumerate(senses):
                    print(i, s.definition())
                syn = senses[int(input())]
                out_file.write(line + "\t" + syn.lemmas()[0].key() + "\t")

            other_word = line.split("\t")[3]
            print(other_word)
            senses = wn.synsets(other_word)
            if len(senses) == 0:
                continue
            if len(senses) == 1:
                out_file.write(senses[0].lemmas()[0].key() + "\n")

            else:
                for i, s in enumerate(senses):
                    print(i, s.definition())
                syn = senses[int(input())]
                out_file.write(syn.lemmas()[0].key() + "\n")


if __name__ == '__main__':
    annotate_subtask3()


def load_cmu():

    with open("corpus/combined_cmu.json") as f:
        cmu = json.load(f)

    return cmu


def load_data():
    cmu = load_cmu()
    task1 = []
    task2 = []
    strings = []
    #
    # with open("data/contractions.json") as f:
    #     contractions = set(json.load(f))

    # with open("/home/doogy/Data/semeval2017_task7/data/test/subtask1-heterographic-test.xml") as f:
    #     xmldict = xmltodict.parse(f.read())
    #     for sent in xmldict['corpus']['text']:
    #         task1.append({"words": [w['#text'] for w in sent['word'] if '#text' in w]})

    with open("data/task1-no-contractions.txt") as f:
        for line in f:
            task1.append({"words": [w for w in line.split()]})

    strings = [' '.join(p['words']) for p in task1]

    with open("/home/doogy/Data/semeval2017_task7/data/test/subtask1-heterographic-test.gold") as f:
        for i, line in enumerate(f.readlines()):
            task1[i]['pun'] = bool(int(line.split()[1]))

    with open("/home/doogy/Data/semeval2017_task7/data/test/subtask2-heterographic-test.xml") as f:
        xmldict = xmltodict.parse(f.read())
    #     for sent in xmldict['corpus']['text']:
    #         task2.append({"words": [w['#text'] for w in sent['word'] if '#text' in w]})

    with open("data/task2-no-contractions.txt") as f:
        for line in f:
            task2.append({"words": [w for w in line.split()]})

    pun_strings = [' '.join(p['words']) for p in task2]

    with open("/home/doogy/Data/semeval2017_task7/data/test/subtask2-heterographic-test.gold") as f:
        for i, line in enumerate(f.readlines()):
            word_array = xmldict['corpus']['text'][i]['word']

            task2[i]['target'] = word_array[[w['@id'] for w in word_array].index(line.split()[1])]['#text']
            task2[i]['t1_index'] = int(line.split()[0].split('_')[1]) - 1

    task3 = []
    with open("/home/doogy/Data/semeval2017_task7/data/test/subtask3-heterographic-test.gold") as f:
        for line in f.readlines():
            lsplit = line.split()
            task1_ind = int(lsplit[0].split('_')[1]) - 1
            c = {}
            c['words'] = task1[task1_ind]['words']
            c['t1_index'] = task1_ind

            left = list(set([w[:w.index('%')] for w in lsplit[1].split(';')]))
            right = list(set([w[:w.index('%')] for w in lsplit[2].split(';')]))

            c['sense_tags'] = ((left, right))
            task3.append(c)

    min_pairs = []
    from src.string_similarity import levenshtein

    for targets, recoveries in [t['sense_tags'] for t in task3]:
        if len(targets) == 1 and len(recoveries) == 1:
            min_pairs.append((targets[0], recoveries[0]))
        else:

            min_distance = 1e10
            check = False
            for word1, word2 in itertools.product(targets, recoveries):
                if word1 in cmu and word2 in cmu:
                    check = True
                    distance = levenshtein(cmu[word1], cmu[word2])
                    if distance < min_distance:
                        min_distance = distance
                        min_pair = (word1, word2)
                    break
            if check:
                min_pairs.append(min_pair)
            else:
                min_pairs.append((targets[0], recoveries[0]))

    return task1, task2, task3, min_pairs, strings, pun_strings

def load_task3_data(path, task1, task2, task3):

    full_path = "results/" + path
    condensed_path = full_path + "_condensed.json"

    pun_words = [None] * len(task1)
    for c in task2:
        pun_words[c['t1_index']] = c['target']
    pun_words = [pun_words[c['t1_index']] for c in task3]

    def get_rankings():

        if os.path.isfile(condensed_path):
            f = open(condensed_path)
            t3_subs = json.load(f)
            f.close()
            t3_subs = [t3_subs[c['t1_index']] for c in task3]

        else:
            substitutions = scores_as_list(path)
            t3_subs = []
            for i in [c['t1_index'] for c in task3]:
                t3_subs.append((list(sorted(substitutions[i].items(),
                                key=lambda x: x[1][0][1], reverse=True))))

            for i in range(len(t3_subs)):
                for j in range(len(t3_subs[i])):

                    t3_subs[i][j] = list(t3_subs[i][j])
                    t3_subs[i][j][1] = t3_subs[i][j][1][:25]

        sub_rankings = []
        for i, subs in enumerate(t3_subs):
            print_progress(i, len(t3_subs))

            pun_word = pun_words[i]
            sentence = task3[i]['words']
            replace_index = sentence.index(pun_word)
            ranked_subs = {}

            for sub in subs:
                derivations = []
                for w in [s[0].split()[1] for s in sub[1]]:

                    temp_sent = list(sentence)
                    temp_sent[replace_index] = w

                    derivations.append({'original_word': w,
                                        'derivations': morphs(w, temp_sent)})

                ranked_subs[sub[0].split()[1]] = derivations

            sub_rankings.append(ranked_subs)
        return sub_rankings

    def toms():
        with open("results/tom_swifties.json") as f:
            tsa = json.load(f)

        temp_toms = [False] * len(task1)

        for context, tom in zip(task2, tsa):
            temp_toms[context['t1_index']] = tom

        tom_swifty_annotations = [temp_toms[c['t1_index']] for c in task3]

        tom_rankings = []
        for i, ts in enumerate(tom_swifty_annotations):
            if not ts:
                tom_rankings.append(False)
                continue

            pun_word = pun_words[i]
            sentence = task3[i]['words']
            replace_index = sentence.index(pun_word)

            derivatives = []
            for w in [t[0][0] for t in ts[0][1]]:
                s = set([w])
                temp_sent = list(sentence)
                temp_sent[replace_index] = w
                derivatives.append({'derivations': morphs(w, temp_sent),
                                    'original_word': w})

            tom_rankings.append({ts[0][0]: derivatives})
        return tom_rankings

    sub_rankings = get_rankings()
    tom_rankings = toms()

    for i in range(len(tom_rankings)):
        if tom_rankings[i]:
            sub_rankings[i] = tom_rankings[i]

    return sub_rankings




def lemma(word, sentence):
    tags = [t[1] for t in pos_tag(sentence)]
    tag = tags[sentence.index(word)]

    if tag.startswith('V'):
        return lm.lemmatize(word, wordnet.VERB)
    elif tag.startswith('J'):
        return lm.lemmatize(word, wordnet.ADJ)
    elif tag.startswith('N'):
        return lm.lemmatize(word, wordnet.NOUN)
    elif tag.startswith('R'):
        return lm.lemmatize(word, wordnet.ADV)
    else:
        return ''

def morphs(word, sentence):
    lemmas = [lemma(word, sentence)]
    lemmas.append(stemmer.stem(word))
    return list(set(lemmas))
