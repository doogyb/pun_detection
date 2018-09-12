# -*- coding: utf-8 -*-
import json
import xml.etree.ElementTree as ET
import sys

import itertools
import xmltodict
from nltk import word_tokenize
from nltk.corpus import wordnet as wn, cmudict


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

    with open("../data/subtask3-annotations-full-2.tsv", 'a') as out_file:
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
    global cmu
    cmu = cmudict.dict()
    for key, val in cmu.items():
        for i, phoneme in enumerate(val):
            cmu[key][i] = [ph[:2] for ph in phoneme]
    return cmu


def load_data():

    cmu = load_cmu()
    task1 = []
    task2 = []
    strings = []

    with open("data/contractions.json") as f:
        contractions = set(json.load(f))

    with open("/home/doogy/Data/semeval2017_task7/data/test/subtask1-heterographic-test.xml") as f:
        xmldict = xmltodict.parse(f.read())
        for sent in xmldict['corpus']['text']:
            task1.append({"words": [w['#text'] for w in sent['word'] if '#text' in w]})

    strings = [' '.join(p['words']) for p in task1]

    with open("/home/doogy/Data/semeval2017_task7/data/test/subtask1-heterographic-test.gold") as f:
        for i, line in enumerate(f.readlines()):
            task1[i]['pun'] = bool(int(line.split()[1]))

    with open("/home/doogy/Data/semeval2017_task7/data/test/subtask2-heterographic-test.xml") as f:
        xmldict = xmltodict.parse(f.read())
        for sent in xmldict['corpus']['text']:
            task2.append({"words": [w['#text'] for w in sent['word'] if '#text' in w]})

    pun_strings = [' '.join(p['words']) for p in task2]

    with open("/home/doogy/Data/semeval2017_task7/data/test/subtask2-heterographic-test.gold") as f:
        for i, line in enumerate(f.readlines()):
            word_array = xmldict['corpus']['text'][i]['word']

            task2[i]['target'] = word_array[[w['@id'] for w in word_array].index(line.split()[1])]['#text']

    task3 = []
    with open("/home/doogy/Data/semeval2017_task7/data/test/subtask3-heterographic-test.gold") as f:
        for line in f.readlines():
            lsplit = line.split()
            left = list(set([w[:w.index('%')] for w in lsplit[1].split(';')]))
            right = list(set([w[:w.index('%')] for w in lsplit[2].split(';')]))
            task3.append((left, right))

    min_pairs = []
    from src.string_similarity import levenshtein

    for targets, recoveries in task3:
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


def convert(context, contractions):
    res = []
    i = 0
    while i < len(context):
        # if i len(context) - 2:
        contract = ''.join(context[i:i+3])
        if ''.join(context[i:i+2]) == "''":
            res.append('"')
            i += 2
        elif contract in contractions:
            res.append(contract)
            i += 3
        else:
            res.append(context[i])
            i += 1

    res = word_tokenize(' '.join(res))
    res = list(map(lambda x: '"' if x == '``' else x, res))
    return res
