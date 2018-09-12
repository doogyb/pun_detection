import os
import nltk
import xml.etree.ElementTree as ET
from nltk.tag import StanfordPOSTagger
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
st = StanfordPOSTagger('/root/Downloads/stanford-postagger-full-2016-10-31/models/english-bidirectional-distsim.tagger',
                       '/root/Downloads/stanford-postagger-full-2016-10-31/stanford-postagger.jar')

tree = ET.parse('/home/PycharmProjects/Projects/pun_detection/data/trial/subtask3-homographic-test.xml')
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
    if (x[1] >= 25):
        st_words.append(x[0].lower())
        # print('freq::', x[0],x[1])


def find_pun_senses(words, anchor):
    line_output = defaultdict()
    print(words)
    anchor_index = words.index(anchor[0])
    # print(anchor_index + 1)
    text_pos = st.tag(words)
    # print(text_pos)
    try:
        if (text_pos[anchor_index][1][0] == 'N'
            or text_pos[anchor_index][1][0] == 'V'
            or text_pos[anchor_index][1][0] == 'R'
            or text_pos[anchor_index][1][0] == 'J'):

            anchor_synsets = wn.synsets(text_pos[anchor_index][0])
            # anchor_synsets.remove(original)
            # print(anchor_synsets)

            for asyn in anchor_synsets:
                score = 0.
                asyn_words = [w for w in asyn.definition().split(' ') if
                              w in word2vecmodel.vocab and w.lower() not in st_words]
                syn_score = 0.
                for t in text_pos:
                    print('word:', t)
                    if (t[0] in word2vecmodel.vocab and t[0].lower() not in st_words and t[0] != anchor[0]):
                        damp = 0.5
                        if (t[1][0].lower() == asyn.pos()
                            or (t[1][0].lower() == 'j' and asyn.pos() == 's')
                            or (t[1][0].lower() == 'j' and asyn.pos() == 'a')):
                            damp = 1.0

                        if (len(asyn_words) > 0 and len(t) > 0):
                            sim = word2vecmodel.n_similarity(asyn_words, [t[0]])
                            score += (sim * damp)
                            # print((t[0], asyn.definition(), sim, sim * damp))

                        t_synsets = wn.synsets(t[0])

                        for ts in t_synsets:
                            tsw = [w for w in ts.definition().split(' ') if
                                   w in word2vecmodel.vocab and w.lower() not in st_words]
                            if (len(asyn_words) > 0 and len(tsw) > 0):
                                syn_sim = word2vecmodel.n_similarity(asyn_words, tsw)
                                if (syn_sim > syn_score):
                                    print(asyn_words, tsw, syn_score, syn_sim)
                                    syn_score = syn_sim

                # print((asyn.definition(), score, syn_score))
                line_output[str(asyn.lemmas()[0].key()) + '\t' +
                            str(asyn.definition())] = score + syn_score
    except:
        print('error::', words)
    return line_output


def run():
    with open('log_update_3.txt', 'w') as fw:
        with open('output_3.txt', 'w') as fo:
            for i, sent in enumerate(root):
                words = [word.text for word in sent]
                anchor = [word.text for word in sent if word.attrib['senses'] == '2']
                anchor_id = [word.attrib['id'] for word in sent if word.attrib['senses'] == '2']
                output = find_pun_senses(words, anchor)
                # print(i)
                fw.write(str(words) + '\n')
                sorted_out = sorted(output.items(), key=operator.itemgetter(1), reverse=True)
                result = []
                result.append(anchor_id[0])
                for o in sorted_out:
                    key_token = o[0].split('\t')
                    result.append(key_token[0])
                    fw.write(str(key_token[1]) + '\t' + str(o[1]) + '\n')
                fw.write(' '.join(result) + '\n')
                fw.write('\n')


                # for wp in text_pos:
                #     if(wp[1][0]=='N' or wp[1][0]=='V'):
                #
                #     for i,s in enumerate(wn.synsets(anchor[0])):
                #         print(s.definition(), )


                #     text = ' '.join(words)
                #     output = detect_pun_sentence(text)
                #     if (output.strip() != 'NA'):
                #         fo.write(str(sent.attrib['id']) + ' ' + str(sent.attrib['id']) + '_' + str(
                #             words.index(output.strip())+1) + '\n')
                #     fw.write(output.strip() + '\t' + text + '\n')


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

def print_pun_senses(text,pun_word):
    output = find_pun_senses(text,[pun_word])
    sorted_out = sorted(output.items(), key=operator.itemgetter(1), reverse=True)
    for o in sorted_out:
        key_token = o[0].split('\t')
        print(str(key_token[1]) + '\t' + str(o[1]) + '\n')

# print_pun_senses('OLD BUNGEE JUMPERS sometimes die but they can still bounce back'.split(' '), 'bounce')
print_pun_senses('The gunman took a shot a new oppotunities'.split(' '), 'shot')
# print_pun_senses('Getting rid of your boat OLD BUNGEE JUMPERS sometimes die but they can still bounce back'.split(' '), 'raft')

run()