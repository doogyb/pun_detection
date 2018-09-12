import nltk
import xml.etree.ElementTree as ET
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from gensim.models import Word2Vec
from collections import defaultdict
import operator


def generate_ngrams(input, n):
    output = []
    for i in range(len(input) - n + 1):
        output.append(input[i:i + n])
    if (len(input) < n):
        output.append(input + [' '] * (3 - len(input)))
    return output


word2vecmodel = Word2Vec.load_word2vec_format('/home/word2vec/GoogleNews-vectors-negative300.bin', binary=True)
tree = ET.parse('/home/PycharmProjects/Projects/pun_detection/data/trial/subtask2-homographic-test.xml')
root = tree.getroot()
st_words = stopwords.words('english')
word_freq = defaultdict()

st_words.append('anymore')
st_words.append('become')
st_words.append('yet')
st_words.append('ago')
st_words.append('earlier')
st_words.append('back')
st_words.append('soon')



for i, sent in enumerate(root):
    for word in sent:
        if (word.text not in word_freq):
            word_freq[word.text] = 0
        word_freq[word.text] = word_freq.get(word.text) + 1
sorted_word_freq = sorted(word_freq.items(), key=operator.itemgetter(1), reverse=True)
for x in sorted_word_freq:
    print('freq::',x)


def get_word2vec_score(w1, w2):
    if w1 not in word2vecmodel.vocab:
        print(w1 + 'not in vocab')
    if w2 not in word2vecmodel.vocab:
        print(w2 + 'not in vocab')
    if (w1 in word2vecmodel.vocab and w2 in word2vecmodel.vocab):
        print('score', word2vecmodel.similarity(w1, w2))


def detect_pun_sentence(text):
    raw_text = text
    print(text)

    text = text.split(' ')
    text_pos = nltk.pos_tag(text)

    first_highest_pairs = defaultdict()
    last_highest_pairs = defaultdict()

    for i, w in enumerate(text_pos):
        if w[0].lower() in word2vecmodel.vocab and w[0].lower() not in st_words:
            for j, x in enumerate(text_pos):
                if x[0].lower() in word2vecmodel.vocab and x[0].lower() not in st_words:
                    if (w[0] != x[0]):
                        score = word2vecmodel.similarity(w[0].lower(), x[0].lower())
                        print('w2v score :', w, x, score)
                        if (score > 0.01):
                            if (i < j):
                                first_highest_pairs[(w, i, x, j)] = score
                                # print('forward selected :: ', w, x, score)
                            if (i > j):
                                last_highest_pairs[(w, i, x, j)] = score
                                # print('backward selected :: ', w, x, score)

    sorted_first_highest_pair = sorted(first_highest_pairs.items(), key=operator.itemgetter(1), reverse=True)
    sorted_last_highest_pair = sorted(last_highest_pairs.items(), key=operator.itemgetter(1), reverse=True)

    first_word_pair = defaultdict()
    last_word_pair = defaultdict()

    for x in sorted_first_highest_pair:

        # forwards
        if (x[0][0] not in first_word_pair):
            first_word_pair[x[0][0]] = ([], 0, 0.)

        rel = first_word_pair.get(x[0][0])[0]
        freq = first_word_pair.get(x[0][0])[1]
        score = first_word_pair.get(x[0][0])[2]

        damp_factor = 1.
        if (x[0][0][1][0] == x[0][2][1][0]):
            damp_factor = 0.9


        rel.append(x[0][2])
        freq += 1
        score += (0.9 - x[1]) * damp_factor

        first_word_pair[x[0][0]] = (rel, freq, score)

    for x in sorted_last_highest_pair:
        # backwards
        if (x[0][0] not in last_word_pair):
            last_word_pair[x[0][0]] = ([], 0, 0.)

        rel = last_word_pair.get(x[0][0])[0]
        freq = last_word_pair.get(x[0][0])[1]
        score = last_word_pair.get(x[0][0])[2]

        damp_factor = 1.
        if (x[0][0][1][0] == x[0][2][1][0]):
            damp_factor = 0.9


        rel.append(x[0][2])
        freq += 1
        score += (0.9 - x[1]) * damp_factor

        last_word_pair[x[0][0]] = (rel, freq, score)

    # print('first')
    best_first = 'NA'
    best_first_score = 0.
    best_first_candidates = defaultdict()
    for k, v in first_word_pair.items():
        # print('FKV::',k,v)
        total_score = 0.
        if (v[1] >= 1):
            # print('tuple::', k, v[0], v[1], v[2], v[2] / v[1])
            # total_score += v[2]
            for r in v[0]:
                max_sim = 0.
                for s in wn.synsets(k[0]):
                    d = s.definition()

                    token = [w for w in nltk.word_tokenize(d.lower()) if
                             w.lower() in word2vecmodel.vocab and w not in st_words]
                    sim = 0.
                    try:
                        if (len(token) > 0):
                            sim = word2vecmodel.n_similarity([r[0].lower()], token)
                    except:
                        print('error:', token)
                    if (sim > max_sim):
                        max_sim = sim

                total_score += max_sim
                # print('w2vf::', r, max_sim)

        total_score += v[2]
        if(word_freq.get(k[0])>25):
            total_score*=0.25
        if (total_score != 0):
            best_first_candidates[k] = total_score
            # print('tsf::', k, total_score)
            if (total_score > best_first_score):
                best_first_score = total_score
                best_first = k

    # print('last')
    best_last = 'NA'
    best_last_score = 0.
    best_last_candidates = defaultdict()
    for k, v in last_word_pair.items():
        print('LKV::', k, v)
        total_score = 0.
        likelihood = 5.
        if(k[1][0]=='N'):
            likelihood=.7
        if(k[1][0]=='R'):
            likelihood=1.
        if(k[1][0]=='V'):
            likelihood=.9
        if(k[1][0]=='J'):
            likelihood=1.

        if (v[1] >= 1):
            # print('tuple::', k, v[0], v[1], v[2], v[2] / v[1])
            # total_score += v[2]
            for r in v[0]:
                max_sim = 0.
                wn_damp_factor = 1.
                if (r[1][0] == k[1][0]):
                    wn_damp_factor = 0.85

                for i,s in enumerate(wn.synsets(k[0])):
                    d = s.definition()
                    token = [w for w in nltk.word_tokenize(d.lower()) if
                             w.lower() in word2vecmodel.vocab and w not in st_words]
                    sim = 0.
                    try:
                        if (len(token) > 0):
                            sim = word2vecmodel.n_similarity([r[0].lower()], token) * wn_damp_factor
                    except:
                        print('error:', token)

                    if (sim > max_sim):
                        max_sim = sim

                total_score += max_sim
                print('w2vl::', r, max_sim)

        total_score += v[2]
        if(word_freq.get(k[0])>25):
            total_score*=0.25
        total_score*=likelihood
        if (total_score != 0):
            best_last_candidates[k] = total_score
            print('tsl::', k, total_score, '\n')
            if (total_score > best_last_score):
                best_last_score = total_score
                best_last = k

    # sorted_last_best_candidate = sorted(best_last_candidates.items(), key=operator.itemgetter(1), reverse=True)
    # print(sorted_last_best_candidate)
    # print(' '.join(text))

    print('best_candidate::', str(best_first) + '\t' + str(best_last) + '\n')

    best_candidate = best_last

    if (raw_text.lower().startswith('my name is')):
        best_candidate = best_first

    # best_candidate = 'NA'
    # best_candidate_score = 0.
    # for k, v in best_last_candidates.items():
    #     score = v
    #     if (k in best_first_candidates):
    #         score += best_first_candidates.get(k) * .5
    #     print('best::', k, best_first_candidates.get(k), v, score)
    #
    #
    #     if (score > best_candidate_score):
    #         best_candidate_score = score
    #         best_candidate = k
    # for k, v in best_first_candidates.items():
    #     if (k not in best_last_candidates):
    #         score = v * .5
    #         print('best::', k, v, best_last_candidates.get(k), score)
    #         if (score > best_candidate_score):
    #             best_candidate_score = score
    #             best_candidate = k
    #
    # print('best_selected::', str(best_candidate))
    if (best_candidate == 'NA'):
        return 'NA'


    return str(best_candidate[0])
    # print('\n')


def run():
    with open('log_update.txt', 'w') as fw:
        with open('output.txt', 'w') as fo:
            # for l in sorted_word_freq:
            #     print('freq::',l)
            for i, sent in enumerate(root):
                # print(sent)
                words = [word.text for word in sent]
                text = ' '.join(words)
                output = detect_pun_sentence(text)
                if (output.strip() != 'NA'):
                    fo.write(str(sent.attrib['id']) + ' ' + str(sent.attrib['id']) + '_' + str(
                        words.index(output.strip())+1) + '\n')
                fw.write(output.strip() + '\t' + text + '\n')


def calculate_P_R_F1():
    p = 0.
    r = 0.
    f1_250 = 0.
    total_lines = 0.
    with open('log_update.txt', 'r') as f:
        with open('gold_set.txt', 'r') as g:
            gold_lines = g.readlines()
            total_lines = len(gold_lines)
            predicted_lines = f.readlines()
            for i, g_line in enumerate(gold_lines):
                gold_label, gtext = g_line.split('\t')
                pred_label, ptext = predicted_lines[i].split('\t')
                if (pred_label != 'NP'):
                    if (gold_label.lower() == pred_label.lower()):
                        p += 1;
                    else:
                        print('Error', pred_label, ':', gold_label, ':', gtext)
                else:
                    r += 1
                if (i == 250):
                    f1_250 = p / 250
    print('correct', p)
    print('not predicted', r)
    print('f1_250', f1_250)
    print('total lines', total_lines)
    print('f1', p / total_lines)


# print(detect_pun_sentence('My name is Mike . I \' m an announcer'))
run()
calculate_P_R_F1()
