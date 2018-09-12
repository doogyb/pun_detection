from .results import Result, Results
import multiprocessing
from .data_processing import print_progress


def classify_pun(context):

    return Result(context[0], context[1])

def run():

    size = 1000
    puns = []
    tsv_file = open("../data/hetero_annotations.tsv").read()
    for line in tsv_file.split("\n")[1:size+1]:
        sent, annot = line.split("\t")[:2]
        puns.append((sent, annot))

    false_negatives, false_positives = [], []
    count = 0
    jobs = []
    tp = tn = fp = fn = 0

    print_progress(count, size)

    pool = multiprocessing.Pool(processes=64)
    pun_it = pool.imap_unordered(classify_pun, puns)
    out = ""
    results = Results()
    for res in pun_it:
        results.add_result(res)
        count += 1
        print_progress(count, size)

    results.calculate_scores()
    results.log()
    print(results)



