# Jeremy Ng 500882192
# CPS842 Project

import sys
from parse import parse
from search import TopK
from porter import PorterStemmer


class Eval(TopK):
    def __init__(self):
        super().__init__()
        self.queries = {}
        self.qrels = {}
        self.maps = []
        self.rpValues = []

    # Read from query.text and qrels.text
    def loadQueries(self, porter, queryPath, qrelsPath):
        with open(queryPath, "r") as queryFile:
            mode = ""
            for line in queryFile:
                if line.startswith(".I"):
                    index = line.split()[1]
                if line[0:-1] in [".W", ".A", ".N"]:
                    mode = line[0:-1]
                elif mode == ".W":
                    if index not in self.queries:
                        self.queries[index] = ""
                    self.queries[index] += line[0:-1]
        queryFile.close()
        with open(qrelsPath, "r") as qrelsFile:
            for line in qrelsFile:
                data = line.split()
                index = str(int(data[0]))
                if index not in self.qrels:
                    self.qrels[index] = []
                self.qrels[index] += [data[1]]
        qrelsFile.close()
        if "-p" in sys.argv or "-porter" in sys.argv:
            for key, val in self.queries.items():
                self.queries[key] = [porter.stem(x)
                                     for x in parse(val.lower())]
        else:
            for key, val in self.queries.items():
                self.queries[key] = parse(val.lower())

    # Get Top K ranking documents from search and calculate MAP and R-Precision for all queries
    # Then calculate and print the average MAP and R-Precision values
    def compare(self):
        for queryID in self.queries:
            if queryID not in self.qrels:
                self.maps += [0]
                self.rpValues += [0]
                continue
            self.query = self.queries[queryID]
            self.calculateWeight()
            self.calculateCosineSimilarity()
            recalls = []
            precisions = []
            count = 1
            magREL = len(self.qrels[queryID])
            for docID in self.getRank(10, verbose=False):
                if docID in self.qrels[queryID]:
                    recalls += [(len(recalls) + 1) / magREL]
                    precisions += [(len(precisions) + 1) / count]
                count += 1
            self.maps += [sum(precisions) / magREL]
            if not precisions:
                self.rpValues += [0]
            else:
                self.rpValues += [precisions[-1]]
        print(f'Average MAP: {round(sum(self.maps) / len(self.maps), 3)}')
        print(
            f'Average R-Precision: {round(sum(self.rpValues) / len(self.rpValues), 3)}')


def main():
    porter = PorterStemmer()
    eval = Eval()
    eval.loadQueries(porter, "../data/query.text", "../data/qrels.text")

    if "-s" in sys.argv or "-stop" in sys.argv:
        eval.readStopWordsFile("../data/common_words")

    eval.readDocuments("../data/cacm.all")

    if "-p" in sys.argv or "-porter" in sys.argv:
        eval.porterStemmingAlgorithm()

    eval.createDictionary()

    eval.N = len(eval.index)
    eval.calculateIDF()

    eval.compare()


if __name__ == "__main__":
    main()
