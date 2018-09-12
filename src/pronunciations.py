import subprocess
from src.data_processing import load_cmu
import src.string_similarity as sm
from src.ipatoarpabet import translate as ph_translate
word_frequencies = None
MAX_FREQUENCY = 100000
model = None

cmu = load_cmu()

def get_closest_sounding_words(in_word, cthreshold=0, share_first_letter=False, use_dictionary=False):
    """
    :param in_word: word to be processed
    :param use_dictionary: include words that are similar and have same first letter
    :param cthreshold: threshold to use in levenshtein distance when searching corpus
    :return: returns a set of similar sounding words based on CMU dict phonemes
    """
    in_word = in_word.lower()
    global cmu
    if not cmu:
        cmu = load_cmu()

    def phonetic_translation(pun_word):
        phonemes = []
        for word in pun_word.split():
            if word in cmu:
                pun_phone = cmu[word][0]
            else:
                pun_phone = ph_translate(word)[0].split()
            phonemes.extend(pun_phone)
        return phonemes

    # if in_word not in cmu:
    #     return []


    ph = '/'.join(phonetic_translation(in_word))

    print(ph)

    pros = set(subprocess.check_output(["src/c/closest_sounding_words", in_word, ph, str(cthreshold)]).split())
    pros = set([p.decode('utf-8') for p in pros])
    if use_dictionary:
        dictionary = open("/usr/share/dict/american-english").read().lower().split()
        for word in dictionary:
            if in_word[0] == word[0] and sm.levenshtein(in_word, word) <= 2 and in_word != word:
                pros.add(word)
    if share_first_letter:
        print(pros)
        pros = set([p for p in pros if p[0] == in_word[0]])
    return pros


def same_sounding_words(in_word):

    if in_word not in cmu and in_word.lower() not in cmu:
        return []
    pronounce_word = cmu[in_word] if in_word in cmu else cmu[in_word.lower()]
    ret = []
    for key, val in cmu.iteritems():
        if key == in_word:
            continue
        if any(i in val for i in pronounce_word):
            ret.append(key)

    return ret

def phonetic_translation(pun_word):
    phonemes = []
    for word in pun_word.split():
        if word in cmu:
            pun_phone = cmu[word][0]
        else:
            pun_phone = ph_translate(word)[0].split()
        phonemes.extend(pun_phone)
    return phonemes


def phonetic_distance(word1, word2):
    ph1 = phonetic_translation(word1)
    ph2 = phonetic_translation(word2)

    # levenshtein of phonemes as atomic units
    phoneme_l = levenshtein(ph1, ph2)
    len_l = max(len(ph1), len(ph2))

    # treat phonemes as strings
    phoneme_s = levenshtein(''.join(ph1), ''.join(ph2))
    len_s = max(''.join(ph1), ''.join(ph2))

    return max(phoneme_l/len_l, phoneme_s/len_s)






if __name__ == "__main__":
    # print((same_sounding_words("orifice", threshold=4)))
    print(get_closest_sounding_words("orifice",  cthreshold=2))
