from __future__ import division
import time
import json
import ngrams


class Results:

    def __init__(self):
        self.accuracy = self.precision = self.correct = self.recall = self.f1 = 0
        self.size = 0
        self.true_positives = []
        self.true_negatives = []
        self.false_positives = []
        self.false_negatives = []

    def add_result(self, res):
        """
        Res is fed from the two subtask methods, with an string indicator for type of result
        :param res:
        :return: None
        """
        if res.type_of_result == 'tp':
            self.true_positives.append(res.__dict__)
        elif res.type_of_result == 'fp':
            self.false_positives.append(res.__dict__)
        elif res.type_of_result == 'tn':
            self.true_negatives.append(res.__dict__)
        elif res.type_of_result == 'fn':
            self.false_negatives.append(res.__dict__)
        self.size += 1

    def calculate_scores(self):
        self.precision = len(self.true_positives) / (len(self.true_positives) + len(self.false_positives))
        self.recall = len(self.true_positives) / (len(self.true_positives) + len(self.false_negatives))
        self.accuracy = (len(self.true_positives) + len(self.true_negatives)) / self.size
        self.f1 = 2 * self.precision * self.recall / (self.precision + self.recall)

    def log(self):
        with open('../log/NGRAMS_SUBTASK1__' + time.strftime('%Y-%m-%d--%H:%M:%S' + '.txt'), 'w') as f:
            json.dump(self.__dict__, f, indent=4)
        with open('../log/subtask1_recent.json', 'w') as f:
            json.dump(self.__dict__, f, indent=4)

    def __repr__(self):
        return 'Correct: ' + str(len(self.true_positives) + len(self.true_negatives)) + \
               '\nTrue positives: ' + str(len(self.true_positives)) + \
               '\nTrue negatives: ' + str(len(self.true_negatives)) + \
               '\nFalse positives: ' + str(len(self.false_positives)) + \
               '\nFalse negatives: ' + str(len(self.false_negatives)) + \
               '\nPrecision: ' + str(self.precision) + \
               '\nRecall: ' + str(self.recall) + \
               '\nAccuracy: ' + str(self.accuracy) + \
               '\nF1: ' + str(self.f1)


class Result:

    def __init__(self, sentence, annotation):

        # self.sentence = sentence.encode('ascii', 'ignore')
        self.sentence = sentence
        self.annotation = annotation
        self.ngram = ngrams.non_three_gram_words(self.sentence, 50)
        if self.annotation == "0":
            if len(self.ngram[1]) <= 1:
                self.type_of_result = 'tn'
            else:
                self.type_of_result = 'fp'
        else:
            if len(self.ngram[0]) > 1:
                self.type_of_result = 'tp'

            else:
                self.type_of_result = 'fn'
