from __future__ import division
import json
import multiprocessing
import os
from nltk.corpus import wordnet as wn
from data_processing import print_progress
from baselines import synset_baseline


def classify_pun(line):
    line_split = line.split("\t")
    id = line_split[0]
    sent = line_split[1]
    word = line_split[2]

    if os.path.isfile("../baselines/subtask3/results_" + str(id) + ".txt"):
        return

    try:
        with open("../baselines/subtask3/results_" + str(id) + ".txt", 'w') as out:
            original_sense, other_sense = synset_baseline(sent, word)
            original_sense = wn.synsets(original_sense)[0].lemmas()[0].key()
            other_sense = wn.synsets(other_sense)[0]
            other_sense = other_sense.lemmas()[0].key()
            out.write(str(id) + " " + original_sense + " " + other_sense)
    except Exception as e:
        pass

if __name__ == "__main__":

    lines = open("../data/subtask3-test.tsv").read().split("\n")
    size = len(lines)

    count = 0
    print_progress(count, size)
    pool = multiprocessing.Pool(processes=4)
    pun_it = pool.imap_unordered(classify_pun, lines)
    for res in pun_it:
        count += 1
        print_progress(count, size)



