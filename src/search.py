# Jeremy Ng 500882192
# CPS842 Project

import sys
import math
from parse import parse
from invert import DocumentCollection
from porter import PorterStemmer
from test import Dictionary


class TopK(DocumentCollection):
    def __init__(self):
        super().__init__()
        self.N = 0
        self.query = []
        self.weights = {}
        self.queryVector = {}
        self.similarity = {}

    def calculateIDF(self):
        for word in self.dictionary:
            self.dictionary[word]["idf"] = math.log(
                self.N / self.dictionary[word]["df"], 10)

    def calculateWeight(self):
        self.weights = {}
        self.queryVector = {}
        seen = set()
        for word in self.query:
            if word in seen:
                continue
            self.weights[word] = {}
            if word in self.dictionary:
                for docID in self.dictionary[word]["docID"]:
                    self.weights[word][docID] = (
                        1 + math.log(self.dictionary[word]["docID"][docID]["tf"], 10)) * self.dictionary[word]["idf"]
                    self.queryVector[word] = (
                        1 + math.log(self.query.count(word), 10)) * self.dictionary[word]["idf"]
            seen.add(word)

    def getMag(self, index):
        seen = set()
        weights = []
        for word in self.index[index]["title"] + self.index[index]["abstract"]:
            if word in seen:
                continue
            weights += [((1 + math.log(self.dictionary[word]["docID"]
                                      [index]["tf"], 10)) * self.dictionary[word]["idf"]) ** 2]
            seen.add(word)
        return sum(weights) ** 0.5

    def calculateCosineSimularity(self):
        self.similarity = {}
        for word in self.weights:
            for docID in self.weights[word]:
                if docID not in self.similarity:
                    self.similarity[docID] = {}
                if word not in self.similarity[docID]:
                    self.similarity[docID][word] = self.weights[word][docID]
        for docID in self.similarity:
            seen = set()
            arr = []
            queryMag = []
            for word in self.query:
                if word in seen:
                    continue
                if word in self.similarity[docID] and word in self.queryVector:
                    arr += [self.similarity[docID]
                            [word] * self.queryVector[word]]
                if word in self.queryVector:
                    queryMag += [self.queryVector[word]]
                seen.add(word)
            docMag = self.getMag(docID)
            queryMag = (sum([x ** 2 for x in queryMag])) ** 0.5
            self.similarity[docID] = sum(arr) / (docMag * queryMag)

    def printRank(self, k):
        if not self.similarity:
            print("No documents")
            return
        count = 0
        for key in sorted(self.similarity, key=self.similarity.get, reverse=True):
            if count == k:
                break
            print(key, round(self.similarity[key], 2))
            count += 1


def main():
    docCol = TopK()
    porter = PorterStemmer()

    if "-s" in sys.argv or "-stop" in sys.argv:
        docCol.readStopWordsFile("../data/common_words")

    docCol.readDocuments("../data/cacm.all")

    if "-p" in sys.argv or "-porter" in sys.argv:
        docCol.porterStemmingAlgorithm()

    docCol.createDictionary()

    docCol.N = len(docCol.index)
    docCol.calculateIDF()

    query = parse(input("\nEnter Query: ").lower())
    while(query != "zzend"):
        if "-p" in sys.argv or "-porter" in sys.argv:
            docCol.query = [porter.stem(x) for x in query]
        else:
            docCol.query = query
        docCol.calculateWeight()
        docCol.calculateCosineSimularity()
        docCol.printRank(10)
        query = parse(input("\nEnter Query: ").lower())


if __name__ == "__main__":
    main()
