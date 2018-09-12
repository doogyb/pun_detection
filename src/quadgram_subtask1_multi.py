from __future__ import division
import json
import multiprocessing
import os
from pun_word_4grams import is_pun, pun_data
from data_processing import print_progress


def classify_pun(context):

    id = context[1]
    if os.path.isfile("../baselines/subtask1_quadgrams/results_" + str(id) + ".txt"):
        return
    try:

        with open("../baselines/subtask1_quadgrams/results_" + str(id) + ".json", 'w') as f:
            json.dump(pun_data(context[0]), f, indent=4)
        return
    except Exception as e:
        print "Caught exception"
        print e
        return

if __name__ == "__main__":

    size = 2
    puns = []
    tsv_file = open("../data/hetero_annotations.tsv").read()
    # size = len(tsv_file.split("\n"))
    for i, line in enumerate(tsv_file.split("\n")[:size]):
        sent = line.split("\t")[0]
        puns.append((sent, "het_" + str(i+1)))

    count = 0
    print_progress(count, size)
    pool = multiprocessing.Pool(processes=2)
    pun_it = pool.imap_unordered(classify_pun, puns)
    for res in pun_it:
        count += 1
        print_progress(count, size)



