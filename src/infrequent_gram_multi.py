from __future__ import division
import multiprocessing
import os

from data_processing import print_progress
from baselines import is_pun


def classify_pun(context):

    id = context[1]
    if os.path.isfile("../baselines/subtask1/results_" + str(id) + ".txt"):
        return
    try:
        res = "1" if is_pun(context[0]) else "0"
        with open("../baselines/subtask1/results_" + str(id) + ".txt", 'w') as f:
            f.write(id + " " + res)
        return
    except Exception as e:
        return

if __name__ == "__main__":

    # size = 10
    puns = []
    tsv_file = open("../data/hetero_annotations.tsv").read()
    size = len(tsv_file.split("\n"))
    for i, line in enumerate(tsv_file.split("\n")[1:size+1]):
        sent = line.split("\t")[0]
        puns.append((sent, "het_" + str(i)))

    count = 0
    print_progress(count, size)
    pool = multiprocessing.Pool(processes=4)
    pun_it = pool.imap_unordered(classify_pun, puns)
    for res in pun_it:
        count += 1
        print_progress(count, size)



