import multiprocessing
from pun_word_4grams import pun_data, best_word
from data_processing import print_progress
import os


def classify(context):
    try:
        sent = context[0]
        id = context[1]
        if os.path.isfile("../test/subtask2/results_" + str(id) + ".txt"):
            name, score = open("../test/subtask2/results_" + str(id) + ".txt").read().split()
            return score, name
        print sent
        return best_word(pun_data(sent)), id
    except Exception as e:
        return "--blank--", id


if __name__ == "__main__":

    size, count = 1271, 0
    contexts = []
    tsv_file = open("../data/subtask2_annotations.tsv").read()
    for i, line in enumerate(tsv_file.split("\n")):
        if len(line.split("\t")) > 1:
            id = line.split("\t")[0]
            sent = line.split("\t")[1]
            contexts.append((sent, id))

    print len(contexts)
    print_progress(count, size)

    pool = multiprocessing.Pool(processes=4)
    pun_it = pool.imap_unordered(classify, contexts)

    results = {}
    split_val = 0

    for res in pun_it:
        results[res[1]] = res[0]
        with open("../test/subtask2/results_" + res[1] + ".txt", 'w') as f:
            f.write(res[1] + " " + str(res[0]))
        count += 1
        print_progress(count, size)

    print results
    with open("../test/results.txt", 'w') as f:
        for id, res in results.iteritems():
            f.write(id + " " + str(res) + "\n")

