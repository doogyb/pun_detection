from __future__ import division
import gzip
import json
import os
import string
import nltk
import subprocess
from math import ceil

# word_frequencies = {ln.split()[0]: int(ln.split()[1]) for ln in open("data/most_frequent_words.txt").read().split("\n")[:-1]}
whole_three_grams = None
four_grams = None


def load_all_three_grams():
    global whole_three_grams
    with open("/home/doogy/Data/ngrams/condensed.tsv") as f:
        # print f.read()
        for line in f:
            if line != "\n":
                # print line.split()
                try:
                    # print "succeeded"
                    whole_three_grams[" ".join(line.split()[:3])] = line.split()[3]
                except:
                    pass
                    # print "failed at", line


def load_four_grams():
    global four_grams
    four_grams = {}
    with open("data/4gram_total.tsv") as f:
        for gram in f.read().split("\n")[:-1]:
            four_grams[" ".join(gram.split()[:4])] = int(gram.split()[4])
    return four_grams

#
# def four_gram_frequency(in_gram):
#     return 0


def get_three_gram_wildcard(first_word, last_word):
    three_gram_frequencies = {}
    three_gram_file = get_gram_file(first_word, "3grams")
    # print(three_gram_file)
    search_start = False
    if not os.path.isfile(three_gram_file):
        print(three_gram_file)
        return {}
    with gzip.open(three_gram_file, 'rt', encoding="ISO-8859-1") as f:

        frequencies = f.read().split("\n")

        start_index = int(len(frequencies) / 2)
        upper_limit = len(frequencies)
        jump = start_index

        while (frequencies[start_index].split()[0] == first_word or frequencies[start_index+1].split()[0] != first_word) and jump > 0:
            # print(jump)
            # print(frequencies[start_index-1].split()[0], frequencies[start_index].split()[0])
            jump = (int(jump/2)) if jump != 0 else 1
            if frequencies[start_index].split()[0] < first_word:
                start_index += jump
            else:
                start_index -= jump + 1
            if start_index < 0 or start_index > upper_limit-1:
                start_index = 0
                break

        for freq in frequencies[start_index:-1]:
            line_sep = freq.split()
            # if line_sep[0] == first_word and not search_start:
            #     search_start = True
            # if not search_start:
            #     continue
            if search_start and line_sep[0] != first_word:
                break
            if line_sep[0] == first_word and line_sep[2] == last_word:
                try:
                    three_gram_frequencies[" ".join(line_sep[:3])] = int(line_sep[3])
                except:
                    pass

    return three_gram_frequencies


def get_four_gram_wildcard(words):
    frequencies = {}
    gram_file = get_gram_file(words[0], "4grams")
    search_term = ' '.join(words[:3])

    if not os.path.isfile(gram_file):
        print(gram_file)
        return {}

    with gzip.open(gram_file, 'rt', encoding='ISO-8859-4') as f:
        grams = []
        freqs = []
        whole_grams = []
        for line in f.readlines():
            lsplit = line.split()
            if len(lsplit) < 5:
                print(lsplit)
            try:
                grams.append(' '.join(lsplit[:3]))
                whole_grams.append(' '.join(lsplit[:4]))
                freqs.append(int(lsplit[4]))
            except Exception as e:
                print(line)
                print(lsplit)


        current_index = int(len(freqs) / 2)
        jump = current_index


        while (grams[current_index] == search_term or grams[current_index+1] != search_term) and jump != 0:
            jump = int(jump/2)
            if grams[current_index] < search_term:
                current_index += jump
            else:
                current_index -= jump

        current_index += 1
        while grams[current_index] == search_term:
            frequencies[whole_grams[current_index]] = freqs[current_index]
            current_index += 1

        return frequencies


def get_three_gram_wildcard2(first_word, last_word):
    three_gram_frequencies = {}
    three_gram_file = get_gram_file(first_word)
    search_start = False
    if not os.path.isfile(three_gram_file):
        return {}
    with gzip.open(three_gram_file, 'rb') as f:

        frequencies = f.read()
        for freq in frequencies.split("\n")[:-1]:
            if freq.split()[0] == first_word and not search_start:
                search_start = True
            if search_start and freq.split()[0] != first_word:
                break
            if freq.split()[0] == first_word and freq.split()[2] == last_word:
                try:
                    three_gram_frequencies[" ".join([w.encode('ascii', 'ignore') for w in freq.split()[:3]])] = int(freq.split()[3])
                except:
                    pass

                # print "3gram not found: ", in_words
    return three_gram_frequencies


def four_gram_frequency(words):
    gram_file = four_gram_file(words)
    for search_file in gram_file:
        if not os.path.isfile(search_file):
            continue
        with open(search_file) as f:
            lines = f.read().split("\n")

        index = int(len(lines) / 2)
        jump = index
        max_jumps = 0
        while lines[index].split()[:4] != words:
            jump = int(ceil(jump / 2))
            if lines[index].split() < words:
                index += jump
            else:
                index -= jump
            if jump == 1:
                break
            if index <= 0 or index >= len(lines) - 1 or max_jumps >= 23:
                index = 0
                break
            max_jumps += 1
            # print index, jump

        if lines[index].split("\t")[0] == " ".join(words):
            return int(lines[index].split()[-1])
    return False


def four_gram_wildcard(words):
    ret = {}

    wildcard_position = words.index("***")
    gram_file = four_gram_file(words)
    for search_file in gram_file:
        if not os.path.isfile(search_file):
            continue
        with open(search_file) as f:
            lines = f.read().split("\n")

        index = int(len(lines) / 2)
        jump = index
        max_jumps = 0
        while lines[index].split()[0] == words[0] or lines[index+1].split()[0] != words[0]:
            jump = int(ceil(jump/2))
            if lines[index].split()[:wildcard_position] < words[:wildcard_position]:
                index += jump
            else:
                index -= jump
            if jump == 1:
                break
            if index <= 0 or index >= len(lines)-1 or max_jumps >= 23:
                index = 0
                break
            max_jumps += 1
            # print index, jump

        for line in lines[index+1:]:

            try:
                split_line = [w.encode('ascii', 'ignore') for w in line.split()]
                # split_line = line.split()
                if len(split_line) > 0:
                    if words[0] != split_line[0]:
                        break
                add = True
                if len(split_line) == 5:

                    for index, word in enumerate(words):
                        if index != wildcard_position and word != split_line[index]:
                            # print
                            add = False
                            break
                    if add:
                        ret[" ".join(split_line[:4])] = int(split_line[4])

            except UnicodeDecodeError as e:
                pass
                # print "Could not encode line", line
                # print e

    return ret


def four_gram_file(words):
    first_word = ""
    for w in words:
        if w == "***":
            break
        first_word += w + " "

    four_gram_dir = json.load(open("local/local_files.json"))['4grams']
    index = []
    with open(four_gram_dir + "4gm.idx") as f:
        for line in f.read().split("\n")[:-1]:
            index.append((" ".join(line.split("\t")[1].split()[0:3]), line.split("\t")[0]))
#
    if first_word == "***":
        return [four_gram_dir + index[i][1][:-3] for i in range(len(index))]
    search_files = []
    for i in range(len(index) - 1):
        if index[i][0] <= first_word <= index[i+1][0]:
            search_files.append(four_gram_dir + index[i][1][:-3])
            # last_index = i

    # search_files.append(four_gram_dir + index[last_index+1][1][:-3])
    return search_files


def non_three_gram_words(pun, threshold=0):
    """
    Finds frequencies for all possible 3grams contained in candidate sentence.
    If a 3gram is not found or has a frequency of 0, then a word contained
    in this 3gram could possibly be a pun.
    :param pun:
    :param threshold: The frequency for a 3gram to be deemed valid
    :return:
    """
    found, not_found = [], []
    three_grams_not_found = []
    sentences = nltk.sent_tokenize(pun)

    for sent in sentences:
        words = ng_word_tokenize(sent)

        # words = [w for w in words if w not in string.punctuation]
        for i in range(len(words)-2):
            if ngram_frequency(words[i:i+3]) > threshold:
                if words[i:i+3] not in found:
                    found.append(words[i:i+3])
                # print "Found: ", words[i:i+3]
            else:
                # print("not found: ", words[i:i+3])
                if words[i:i + 3] not in not_found:
                    not_found.append(words[i:i + 3])
                three_grams_not_found.append(words[i:i+3])

    print(not_found)
    result = list(set([w for nf in not_found for w in nf]))
    return result, list(not_found)


def missing_three_grams(sentence, threshold=0):

    not_found = []
    sentences = nltk.sent_tokenize(sentence)

    for sent in sentences:
        words = ng_word_tokenize(sent)

        # words = [w for w in words if w not in string.punctuation]
        for i in range(len(words) - 2):
            if ngram_frequency(words[i:i+3]) <= threshold:
                not_found.append(words[i:i + 3])
    return not_found


def ngram_frequency(in_words):

    # in_words being a list of words

    gram_file = get_gram_file(in_words[0], str(len(in_words)) + "grams")
    arguments = ["src/c/ngram_frequency", gram_file]
    arguments.extend(in_words)
    return int(subprocess.check_output(arguments))


def get_gram_file(first_word, n):

    # data_folder = json.load(open("local/local_files.json"))[n]
    data_folder = '/home/doogy/data'

    if first_word[0] in string.punctuation:
        if first_word[0] == '`' or first_word[0] == "\"":
            return data_folder + "symbols/quotes.gz"
        return data_folder + "symbols/" + first_word[0] + ".gz"

    if first_word[0].isupper():
        char_dir = "upper/"
    else:
        char_dir = "lower/"

    first_dir = first_word[0].lower() + "/"

    if first_word.lower() == "the":
        second_dir = 'h/'
        third_dir = 'the'

    elif len(first_word) == 1:
        second_dir = ""
        third_dir = "_only"
    elif len(first_word) == 2:
        if first_word[1] in string.punctuation:
            second_dir = ""
            third_dir = "symb"
        else:
            second_dir = first_word[1].lower() + "/"
            third_dir = "_only"
    else:

        if first_word[1] in string.punctuation:
            second_dir = ""
            third_dir = "symb"

        else:

            second_dir = first_word[1].lower() + "/"
            if first_word[2] in string.punctuation:
                third_dir = "symb"
            else:
                third_dir = first_word[2].lower()
    return data_folder + char_dir + first_dir + second_dir + third_dir + ".gz"


def ng_word_tokenize(sentence):
    """
    Method for tokenizing sentences to get best results from ngrams.
    :param sentence:
    :return:
    """

    sentence = nltk.word_tokenize(sentence)
    punctuation_to_remove = ["?", "!", "...", "*"]

    sentence = translate_to_google_tokens(sentence)
    sentence = [w for w in sentence if w not in punctuation_to_remove]
    # In case the sentence was purely punctuation.
    if not sentence:
        return []
    sentence = [w for w in sentence if w not in string.punctuation]
    sentence.append(".")
    return sentence


def ng_word_tokenize2(sentence):
    """
    Method for tokenizing sentences to get best results from ngrams.
    :param sentence:
    :return:
    """

    sentence = nltk.word_tokenize(sentence)
    punctuation_to_remove = ["?", "!", "...", "*"]
    sentence = translate_to_google_tokens(sentence)
    sentence = [w for w in sentence if w not in punctuation_to_remove]
    # In case the sentence was purely punctuation.
    if not sentence:
        return []
    return sentence


def translate_to_google_tokens(sentence):
    for i in range(len(sentence)):
        # Convert do n't into do not for google's way of dealing with contractions
        if i < len(sentence) - 1:
            if sentence[i] == "do" and sentence[i+1] == "n't":
                sentence[i+1] = "not"
            if sentence[i] == "ai" and sentence[i+1] == "n't":
                sentence[i] = "is"
                sentence[i+1] = "not"
            if sentence[i] == "was" and sentence[i+1] == "n't":
                sentence[i+1] = "not"
            if sentence[i] == "wo" and sentence[i+1] == "n't":
                sentence[i+1] = "not"
            if sentence[i] == "were" and sentence[i+1] == "n't":
                sentence[i+1] = "not"
            if sentence[i] == "could" and sentence[i+1] == "n't":
                sentence[i+1] = "not"
            if sentence[i] == "ca" and sentence[i+1] == "n't":
                sentence[i] = "can"
                sentence[i+1] = "not"

        # Convert `` to ''
        if sentence[i] == "``":
            sentence[i] = "\""
        if sentence[i] == "''":
            sentence[i] = "\""
        # if sentence[i] == "Tom":
        #     sentence[i] = "*"
        if sentence[i] == "'m":
            sentence[i] = "am"

    return sentence

if __name__ == "__main__":
    # print(get_three_gram_wildcard2("his", "was"))
    # print(three_gram_frequency("I am a".split()))
    four_gram_wildcard("I am a wolf".split())
