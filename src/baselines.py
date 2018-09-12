from __future__ import division

import os

from pun_word_4grams import relevant_four_grams, split_four_grams
from nltk.corpus import wordnet as wn
from ngrams import four_gram_frequency
from data_processing import print_progress
from subtask3 import synset_baseline


def is_pun(context, threshold=150):
    """
    If the context contains no infrequent quadgrams, then it is not a pun
    :param context: The context to be dealt with
    :return: Boolean value for classification
    """

    relevant_grams = split_four_grams(context)
    # print relevant_grams
    for gram in relevant_grams:
        freq = four_gram_frequency(gram)

        # print gram
        # print freq
        if freq < threshold:
            return True
    return False


def check_results(gold, system):
    gold_annot = {}
    system_annot = {}
    with open(gold) as f:
        for line in f.read().split("\n")[:-1]:
            gold_annot[line.split()[0]] = int(line.split()[1])
    with open(system) as f:
        for line in f.read().split("\n")[:-1]:
            system_annot[line.split()[0]] = int(line.split()[1])

    tp, fp, tn, fn = 0, 0, 0, 0
    for key, val in gold_annot.iteritems():
        if key in system_annot:
            if val == system_annot[key]:
                if val == 0:
                    tn += 1
                else:
                    tp += 1
            else:
                if val == 0:
                    fn += 1
                else:
                    fp += 1

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = (2 * precision * recall) / (precision + recall)
    print "Accuracy:", (tp + tn) / (tp + tn + fn + fp)
    print "Precision:", precision
    print "Recall:", recall
    print "F1:", f1


def subtask3_topkeys():

    size, count = 10, 0
    lines = open("../data/subtask3-test.tsv").read().split("\n")
    size = len(lines)
    # m = load_model()
    for line in lines[2:3]:
        count += 1
        # try:
        line_split = line.split("\t")
        id = line_split[0]
        print id
        sent = line_split[1]
        word = line_split[2]
        # if os.path.isfile("../baselines/subtask3/results_" + str(id) + ".txt"):
        #     continue

        try:
            with open("../baselines/subtask3/results_" + str(id) + ".txt", 'w') as out:
                original_sense, other_sense = synset_baseline(sent, word)
                original_sense = wn.synsets(original_sense)[0].lemmas()[0].key()
                other_sense = wn.synsets(other_sense)[0]
                other_sense = other_sense.lemmas()[0].key()
                out.write(str(id) + " " + original_sense + " " + other_sense)
        except Exception as e:
            raise
        print_progress(count, size)



if __name__ == "__main__":
    subtask3_topkeys()
    # check_results("../gold/subtask1-heterographic-test.gold", "../baselines/subtask1/total.txt")
