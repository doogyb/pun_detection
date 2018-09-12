import multiprocessing
from data_processing import print_progress
from subtask3 import produce_synset, load_model, synset_baseline
from pprint import pprint
import os


def classify(context):
    count = 0
    try:
        m = load_model()
        for cont in context:
            print_progress(count, len(context))
            count += 1
            try:
                line_split = cont.split("\t")
                id = line_split[0]
                sent = line_split[1]
                word = line_split[2]
                if os.path.isfile("../test/subtask3/results_" + str(id) + ".txt"):
                    continue
                original_sense, other_sense = produce_synset(sent, word, m)
                # print original_sense, other_sense
                original_sense_key = original_sense[0][1].lemmas()[0].key()
                other_sense_key = other_sense[0][1].lemmas()[0].key()
                with open("../test/subtask3/results_" + str(id) + ".txt", 'w') as out:
                    out.write(str(id) + " " + original_sense_key + " " + other_sense_key + " " + original_sense[0][2] +
                              " " + other_sense[0][2])

            except Exception as e:
                pass

    except Exception as e:
        print e


def classify_linear():

    size, count = 10, 0
    lines = open("../data/subtask3-test.tsv").read().split("\n")
    size = len(lines)
    # m = load_model()
    for line in lines:
        count += 1
        # try:
        line_split = line.split("\t")
        id = line_split[0]
        sent = line_split[1]
        word = line_split[2]
        if os.path.isfile("../baselines/subtask3/results_" + str(id) + ".txt"):
            continue

        with open("../baselines/subtask3/results_" + str(id) + ".txt", 'w') as out:
            original_sense, other_sense = synset_baseline(sent, word)
            # print original_sense, other_sense
            original_sense_key = original_sense[0][1].lemmas()[0].key()
            other_sense_key = other_sense[0][1].lemmas()[0].key()
            out.write(str(id) + " " + original_sense_key + " " + other_sense_key + " " + original_sense[0][2] +
                      " " + other_sense[0][2])
        # except Exception as e:
        #     print e
        #     pass
        print_progress(count, size)


if __name__ == "__main__":
    classify_linear()
    # classify_linear()
