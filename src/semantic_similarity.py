import codecs
import json
import itertools
from gensim.models import Word2Vec
import nltk
import numpy
from nltk.stem.porter import PorterStemmer
from nltk.corpus import wordnet as wn
from nltk import word_tokenize
from numpy.ma import dot
from data_processing import load_cmu
from collections import defaultdict
import pygtrie as trie

parser = None
model = None
grammar_tool = None
word_frequencies = None
cmu = None


def wordnet(word1, word2):
    original_word1 = word1
    original_word2 = word2
    word1 = wn.synsets(word1.strip().lower())
    word2 = wn.synsets(word2.strip().lower())
    if len(word1) == 0 or len(word2) == 0:
        print("Array is empty")
        print("Could not for words: ", original_word1, original_word2)
        return 0
    word1 = wn.synset(word1[0].name)
    word2 = wn.synset(word2[0].name)
    if not word1 or not word2:
        print("word is empty")
        print("Could not for words: ", original_word1, original_word2)
        return 0
    similarity = word1.wup_similarity(word2)

    print(similarity)
    if not similarity:
        print("Could not for words: ", original_word1, original_word2)
        return 0
    return similarity


def word2vec_distance(word1, word2, use_model=False, path="~/Data/googlenews-vectors.bin"):
    global model
    if not model:
        if use_model:
            print("Loading google news vectors")
            model = Word2Vec.load_word2vec_format(path, binary=True)
            print("Model loaded")
        else:
            model = json.load(open("../data/word_vectors.json"))

    if word1 not in model:
        # print word1, "not in model"
        return 0
    if word2 not in model:
        # print word2, "not in model"
        return 0
    vec1 = numpy.array(model[word1])
    vec2 = numpy.array(model[word2])
    return dot(gensim.matutils.unitvec(vec1), gensim.matutils.unitvec(vec2)).data


def word_pair_distances(sent, nbest=3):
    sent = word_tokenize(sent)
    sent = pos_filter(sent, tokenize=False)
    res = []
    word_pairs = set(itertools.combinations(sent, 2))
    for word in word_pairs:
        res.append([word[0], word[1], float(word2vec_distance(word[0], word[1], use_model=True))])

    return sorted(res, reverse=True, key=lambda x: x[2])[:nbest]


def pos_filter(sentence, tokenize=True, strict=True):
    filter_list = ['ADV', 'NOUN', 'VERB', 'ADJ']
    if tokenize:
        tokens = nltk.word_tokenize(sentence.lower().replace("\'",""))
    else:
        tokens = sentence

    tagged = nltk.pos_tag(tokens, tagset='universal')
    filtered_words = [word[0] for word in tagged if word[1] in filter_list]
    if len(filtered_words) == 0:
        return []

    if strict:
        filtered_words = [word for word in filtered_words if len(word) > 3]

    return filtered_words


def contract_words(words):
    contracted_words = [words[0]]
    i = 1
    while i < len(words):
        if '\'' in words[i]:
            contracted_words.remove(words[i-1])
            contracted_words.append(words[i-1] + words[i])
            i += 1
        else:
            contracted_words.append(words[i])
            i += 1
    return contracted_words


# TODO Implement a POS grammatical sentence checker
def is_grammatical(sentence, tool='grammar_check'):
    if tool == "parser":
        global parser
        if not parser:
            p = Parser(allow_null=False)
        if isinstance(sentence, str):
            sentence = sentence.encode('ascii', 'ignore')
        linkages = p.parse_sent(sentence)
        return len(linkages) != 0
    if tool == "grammar_check":
        global grammar_tool
        if not grammar_tool:
            grammar_tool = grammar_check.LanguageTool('en-GB')
        # Sentence is grammatical if no matches are found
        return len(grammar_tool.check(sentence)) == 0


def most_frequent_word(words):
    global word_frequencies
    if not word_frequencies:
        word_frequencies = open(json.load(open("../local_files.json"))['word-frequencies']).read().split("\n")
    for word in word_frequencies[:-1]:
        if word.split()[0] in words:
            return word.split()[0]

    return words[0]


def get_prefixes(word):
    def load_dict(path):
        ret = set()
        with codecs.open(path, "r", "utf8") as r:
            for line in r:
                ret.add(line[:-1])
        return ret
    am = load_dict("/usr/share/dict/american-english")
    br = load_dict("/usr/share/dict/british-english")
    ret = []
    x = word
    for x in iter(lambda: x[:-1], ''):
        if (x in am or x in br) and len(x) > 2:
            ret.append(x)
    return ret


def get_cmu_tree(word, threshold):
    global cmu
    if not cmu:
        cmu = load_cmu()

    def get_phoenetic_trie():
        dd = defaultdict(list)
        tree = trie.Trie()
        for k, vs in cmu.items():
            for v in vs:
                dd[','.join(v)].append(k)
        for k, v in dd.items():
            tree[k.split(',')] = v
        return tree, cmu

    stemmer = PorterStemmer()
    cmu_trie, cmu = get_phoenetic_trie()
    if stemmer.stem(word) in cmu:
        new_word = stemmer.stem(word)
    elif word in cmu:
        new_word = word
    else:
        return get_prefixes(word)
    tmp_ret = []

    for phoneme in cmu[new_word]:
        p = phoneme
        sub_ret = []
        while len(p) > threshold:
            sub_sub_ret = []
            if p in cmu_trie:
                sub_sub_ret.extend([i for i in cmu_trie[p] if i != word])
            else:
                sub_sub_ret.extend([])
            sub_sub_ret.extend(list(itertools.chain(*[v for k, v in cmu_trie.iteritems(p, shallow=True)
                                                      if len(k) == len(p)+1 and word not in v])))
            p = p[:-1]
            sub_ret.append(sub_sub_ret)
        tmp_ret.append(sub_ret)
    # print(tmp_ret)
    ret = []
    for items in itertools.izip_longest(*tmp_ret):
        ret.append(list(itertools.chain(*items)))

    # ret = list(itertools.chain(*ret[:threshold]))
    ret = list(itertools.chain(*ret))

    ret.extend(get_prefixes(word))
    return list(set(ret))


def load_model():
    print("loading model...")
    global model
    model = Word2Vec.load_word2vec_format(json.load(open("../local_files.json"))["google-vectors"], binary=True)
    print("finished loading model")
    return model


def best_word_from_context(words, context):
    max = -10000000
    ret_word = ""
    global model
    if not model:
        model = load_model()
    context = [word for word in context.split() if word in model.vocab]
    for word in words:
        if word not in model.vocab:
            continue
        score = model.n_similarity(context, [word])
        if score >= max:
            ret_word = word
            max = score

    return ret_word


if __name__ == "__main__":
    pass
