import numpy as np
from sklearn.cluster import AffinityPropagation
import semantic_similarity


def affinity_propagation(words, algo="word2vec", use_model=False):
    """
        Uses wordnet similarity to cluster the words in the sentences
        :param words: input sentence
        :return: two lists which correspond the clusters
        """

    words = semantic_similarity.pos_filter(words, False, strict=False)
    words = np.asarray(words)  # So that indexing with a list will work
    if algo == "word2vec":
        lev_similarity = np.array([[semantic_similarity.word2vec_distance(w1, w2, use_model=use_model)
                                    for w1 in words] for w2 in words])

    if algo == "wordnet":
        lev_similarity = np.array([[semantic_similarity.word2vec_distance(w1, w2) for w1 in words] for w2 in words])

    if len(lev_similarity) < 2:
        return [[], []]
    affprop = AffinityPropagation(affinity="precomputed", damping=0.5)
    affprop.fit(lev_similarity)
    if np.isnan(np.sum(affprop.labels_)):
        print "No labels"
        return [[], []]

    clusters = []
    flattened_cluster = []
    centroids = []
    for cluster_id in np.unique(affprop.labels_):
        exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
        centroids.append(words[affprop.cluster_centers_indices_[cluster_id]])
        cluster = np.unique(words[np.nonzero(affprop.labels_ == cluster_id)])
        clusters.append(list(cluster))
        flattened_cluster.extend(cluster)

    return clusters, centroids


if __name__ == "__main__":

    affinity_propagation("Tom is in the house".split(" "))
