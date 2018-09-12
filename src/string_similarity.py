
import json
import string
import nltk

dictionary = set(w for w in
                 open("/usr/share/dict/american-english").read().lower().split()
                 if len(w) > 1)

full_dictionary = open("/usr/share/dict/american-english").read().lower().split()
max_len = 23


def levenshtein(word1, word2):
    if len(word1) < len(word2):
        return levenshtein(word2, word1)

    if len(word2) == 0:
        return len(word1)

    previous_row = list(range(len(word2) + 1))
    for i, c1 in enumerate(word1):
        current_row = [i + 1]
        for j, c2 in enumerate(word2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def longest_common_subsequence(word1, word2):

    m = len(word1)
    n = len(word2)
    # An (m+1) times (n+1) matrix
    c = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            result = word1[i - 1] == word2[j - 1]
            if result:
                c[i][j] = c[i - 1][j - 1] + 1
            else:
                c[i][j] = max(c[i][j - 1], c[i - 1][j])

    return c[m][n]


def longest_common_substring(word1, word2):

    m = len(word1)
    n = len(word2)
    c = [[0] * (n + 1) for _ in range(m + 1)]

    max_subtring_length = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                c[i][j] = c[i - 1][j - 1] + 1
                if max_subtring_length < c[i][j]:
                    max_subtring_length = c[i][j]
    return max_subtring_length


def jaccard_similarity(word1, word2):
    intersection_cardinality = len(set.intersection(*[set(word1), set(word2)]))
    union_cardinality = len(set.union(*[set(word1), set(word2)]))
    return intersection_cardinality / float(union_cardinality)


def linear_similarity(word1, word2):
    yloc = 0
    l_intersection = 0
    for i in range(0, len(word1)):
        for j in range(yloc, len(word2)):
            if word1[i] == word2[j]:
                l_intersection += 1
                yloc = j
                break

    union_cardinality = max(len(word1), len(word2))
    return l_intersection / float(union_cardinality)


def find_subwords(word):

    if '-' in word:
        return word.split("-")

    global dictionary, max_len

    words_found = []
    for i in range(len(word)):
        chunk = word[i:i + max_len + 1]
        for j in range(1, len(chunk) + 1):
            sub_word = chunk[:j]
            if sub_word in dictionary:
                # words_found.append(sub_word)
                words_found.append(sub_word)

    return words_found


def find_combination_of_words(word):

    global dictionary, max_len
    words_found = []

    for i in range(len(word)):
        sub_word = word[:i]
        if sub_word in dictionary:
            words_found.append((sub_word, find_subwords(word[i:])))
    return words_found


def return_split_word(word):
    """
    Returns the best match for the find_combination_of_words
    method. It returns two words if there exists an exact
    split. Other wise it returns the two longest sub words
    which form linearly.
    :param word: the word to be split
    :return: a pair of words which where split
    """

    res = []
    words = find_combination_of_words(word)
    for word in words:
        if len(word[1]) > 0:
            res.append((word[0], max(word[1], key=lambda w: len(w))))

    return res


def does_sentence_contain_word_combo(sentence):
    sentence = sentence.encode('ascii', 'ignore').translate(None, string.punctuation)
    split_words = []
    for word in nltk.word_tokenize(sentence.lower()):
        if word not in full_dictionary:
            res = return_split_word(word)
            if len(res) > 0:
                for possible in res:
                    if len(possible[0]+possible[1]) / len(word) > .5:
                        split_words.append(res)
    return split_words


if __name__ == '__main__':
    puns = json.load(open("../data/puns/heterographic_puns.json"))
    for pun in puns:
        if does_sentence_contain_word_combo(pun):
            print(pun)
    print(levenshtein("poplar", "popular"))
