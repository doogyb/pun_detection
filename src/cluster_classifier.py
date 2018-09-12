from __future__ import division
import string_similarity as sm
import semantic_similarity as ss
import clustering
import pronunciations
import json
import operator
from nltk.corpus import cmudict

model = None


def classify_with_clustering(sentence, use_model=False):
    """
    sentence is filtered for useless words (such as prepositions)
    then clustered (multiple algorithms available)
    then a set of words which sound similar to the words in the sentence is produced
    these words are then clustered.
    If one of the words changes cluster when changed to a similar sounding word,
    there is a possibility that the sentence contains a pun at that word.
    :param sentence: string or list of words
    :param use_model: Whether to use the google vector model in memory or not
    :return: True or False for result of classification, along with pun word if classified as pun
    """

    count = 0
    sentence = ss.pos_filter(sentence, True)
    clusters, centroids = clustering.affinity_propagation(sentence, use_model=use_model)
    cmu = cmudict.dict()

    # for cluster, centroid in zip(clusters, centroids):
    #     print cluster, centroid

    possible_puns = []
    # average distance from cluster
    for cluster, cluster_centroid in zip(clusters, centroids):
        for word in cluster:
            # print "Getting word: ", word
            # if the word is contained in cmu:
            if word in cmu:
                res = pronunciations.get_closest_sounding_words(word)
            else:
                continue
            # else, we might have to use g2p (depending on speed...)
            for similar_word in res:

                local_min = -float("Inf")
                closest_centroid = ""
                for cluster_2, centroid in zip(clusters, centroids):

                    distances = map(lambda w: ss.word2vec_distance(similar_word, w, use_model=use_model), cluster_2)
                    average_distance = reduce(lambda x, y: x + y, distances) / len(distances)

                    if abs(average_distance) > local_min:
                        local_min = average_distance
                        closest_centroid = centroid

                if closest_centroid != cluster_centroid:
                    if local_min >= 0.15:
                        count += 1
                        possible_puns.append((word, similar_word, local_min, cluster_centroid, closest_centroid))

    # print count, "words were clustered"
    return sorted(possible_puns, key=operator.itemgetter(2), reverse=True)


def idiom_score(sentence, threshold=0.7):
    """
    Uses longest common subsequence of words to check for possibility
    that idiom is used.
    :param sentence: The sentence to check
    :return: the ratio of the longest common subsequence of the maximium
    found idiom to its length.
    """

    if not isinstance(sentence, list):
        sentence = sentence.lower().split(" ")

    idioms = json.load(open("../data/idioms.json"))
    idioms = [idiom[0].strip().lower().split(" ") for idiom in idioms]

    def common_length(idiom):
        if len(idiom) <= 4:
            return sm.longest_common_substring(idiom, sentence)
        else:
            return sm.longest_common_subsequence(idiom, sentence)

    length_ratios = map(lambda idiom: common_length(idiom) / len(idiom), idioms)
    res = max(length_ratios)
    return res, idioms[length_ratios.index(res)]


if __name__ == "__main__":
    pass
