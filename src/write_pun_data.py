import json

import multiprocessing
from data_processing import print_progress
from pun_word_4grams import pun_data


def write_data(line):
    line_split = line.split("\t")
    # print line_split
    if len(line_split) != 6:
        return
    try:
        with open("../data/subtask3_pun_data/" + line_split[0] + ".json", 'w') as out:
            json.dump(pun_data(line_split[1], line_split[2]), out, indent=4)
    except Exception as e:
        print e
        print "Failed on", line_split[1]


if __name__ == "__main__":
    with open("../data/subtask3-annotations-full-2.tsv") as f:
        data = f.read().split("\n")

    count = 0
    pool = multiprocessing.Pool(processes=4)
    pun_it = pool.imap_unordered(write_data, data)
    print_progress(count, len(data))

    for res in pun_it:
        count += 1
        print_progress(count, len(data))
