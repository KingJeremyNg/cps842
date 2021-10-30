# Jeremy Ng 500882192
# CPS842 Project

import sys
import math
from parse import parse
from invert import DocumentCollection
from porter import PorterStemmer


class TopK(DocumentCollection):
    def __init__(self):
        super().__init__()
        self.N = 0
        self.query = []
        self.weights = {}
        self.queryVector = {}
        self.similarity = {}

    # Calculate IDF for each word in the dictionary
    def calculateIDF(self):
        for word in self.dictionary:
            self.dictionary[word]["idf"] = math.log(
                self.N / self.dictionary[word]["df"], 10)

    # Calculate weight for documents that contain at least 1 word from query
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

    # Calculate magnitude of weights in a given index
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

    # Calculate cosine similarity of documents containing at least 1 word from query
    def calculateCosineSimilarity(self):
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
            for word in self.query:
                if word in seen:
                    continue
                if word in self.similarity[docID] and word in self.queryVector:
                    arr += [self.similarity[docID]
                            [word] * self.queryVector[word]]
                seen.add(word)
            docMag = self.getMag(docID)
            queryMag = (
                sum([x ** 2 for x in [val for key, val in self.queryVector.items()]])) ** 0.5
            self.similarity[docID] = sum(arr) / (docMag * queryMag)

    # Get information relating to index ID from collection file
    def getDocument(self, index, filePath="../data/cacm.all"):
        with open(filePath, "r") as collection:
            file = collection.read()
        collection.close()
        if f'.I {index}' in file:
            start = file.index(f'.I {index}')
            if f'.I {int(index) + 1}' in file:
                end = file.index(f'.I {int(index) + 1}')
                return file[start:end]
            else:
                return file[start:-1]
        else:
            return "No Document"

    # Get title information from document
    def getTitle(self, document):
        if ".T" not in document:
            return "No Title"
        start = document.index(".T") + 3
        for search in [".W", ".B", ".A", ".N", ".X"]:
            if search in document:
                end = document.index(search)
                break
        return document[start:end].replace("\n", " ")

    # Get top K documents
    def getRank(self, k, verbose=False):
        if not self.similarity:
            print("No documents")
            return
        result = []
        count = 1
        for docID in sorted(self.similarity, key=self.similarity.get, reverse=True):
            if count > k:
                break
            if verbose:
                print(f'\n{count})')
                print(f'Index: {docID}')
                print(f'Title: {self.getTitle(self.getDocument(docID))}')
                print(f'Author(s): {" | ".join(self.index[docID]["authors"])}')
            result += [docID]
            count += 1
        return result


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
        docCol.calculateCosineSimilarity()
        docCol.getRank(10, True)
        query = parse(input("\nEnter Query: ").lower())


if __name__ == "__main__":
    main()
