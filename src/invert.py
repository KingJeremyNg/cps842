# Jeremy Ng 500882192
# CPS842 Project

import sys
from porter import PorterStemmer
from parse import parse


class DocumentCollection:
    # Constructor
    def __init__(self):
        self.index = {}
        self.stopWords = set()
        self.dictionary = {}

    # Function to add new document
    def addDocument(self, index, title, abstract, date, authors):
        self.index[index] = {
            "title": title,
            "abstract": abstract,
            "date": date,
            "authors": authors
        }

    # Open and read common_words files
    def readStopWordsFile(self, file):
        with open(file, "r") as words:
            for word in words:
                # [0:-1] to remove newline character
                self.stopWords.add(word[0:-1])
        words.close()

    # Function to read and parse files
    def readDocuments(self, collection):
        # Open and read CACM file
        with open(collection, "r") as document:
            index = 0
            title = []
            abstract = []
            date = ""
            authors = []
            mode = ".I"
            modeSet = [".T", ".W", ".B", ".A", ".N", ".K", ".C", ".X"]
            for line in document:
                if line.startswith(".I"):
                    # Store previous index information
                    self.addDocument(index, title, abstract, date, authors)
                    # Clear variables and set new index
                    index = line[3:-1]
                    title = []
                    abstract = []
                    date = ""
                    authors = []
                # Set mode
                for string in modeSet:
                    if line.startswith(string):
                        mode = string
                        break
                # If line is not setting mode then store data. [0:-1] to remove newline character
                else:
                    if mode == ".T":
                        for word in parse(line[0:-1].lower()):
                            if "-s" in sys.argv or "-stop" in sys.argv:
                                if word not in self.stopWords:
                                    title += [word]
                            else:
                                title += [word]
                    if mode == ".W":
                        for word in parse(line[0:-1].lower()):
                            if "-s" in sys.argv or "-stop" in sys.argv:
                                if word not in self.stopWords:
                                    abstract += [word]
                            else:
                                abstract += [word]
                    if mode == ".B":
                        date = line[0:-1]
                    if mode == ".A":
                        authors.append(line[0:-1])
            # Edge case for last index
            self.addDocument(index, title, abstract, date, authors)
            # Delete this record
            del self.index[0]
        document.close()

    # Apply porter's stemming algorithm to every word of our documents
    def porterStemmingAlgorithm(self):
        porter = PorterStemmer()
        for key in self.index:
            for i in range(len(self.index[key]["title"])):
                self.index[key]["title"][i] = porter.stem(
                    self.index[key]["title"][i])
            for i in range(len(self.index[key]["abstract"])):
                self.index[key]["abstract"][i] = porter.stem(
                    self.index[key]["abstract"][i])

    # Add to dictionary
    def addToDictionary(self, index, word, position):
        if word not in self.dictionary:
            self.dictionary[word] = {
                "df": 1,
                "docID": {
                    index: {
                        "tf": 1,
                        "position": [position]
                    }
                }
            }
        else:
            if index not in self.dictionary[word]["docID"]:
                self.dictionary[word]["df"] += 1
                self.dictionary[word]["docID"][index] = {
                    "tf": 1,
                    "position": [position]
                }
            else:
                self.dictionary[word]["docID"][index]["tf"] += 1
                self.dictionary[word]["docID"][index]["position"] += [position]

    # Create word dictionary
    def createDictionary(self):
        for key in self.index:
            position = 1
            for word in self.index[key]["title"]:
                self.addToDictionary(key, word, position)
                position += 1
            for word in self.index[key]["abstract"]:
                self.addToDictionary(key, word, position)
                position += 1

    # Make dictionary and postings lists files
    def createFiles(self):
        dictionaryFile = open("../output/dictionary.txt", "w")
        postingsLists = open("../output/postingsLists.txt", "w")
        if "-p" in sys.argv or "-porter" in sys.argv:
            dictionaryFile.write(".porter yes\n")
        else:
            dictionaryFile.write(".porter no\n")
        for key in sorted(self.dictionary):
            dictionaryFile.write(f'{key} {self.dictionary[key]["df"]}\n')
            postingsLists.write(f'.{key}\n')
            for index in self.dictionary[key]["docID"]:
                postingsLists.write(
                    f'{index} {self.dictionary[key]["docID"][index]["tf"]} {self.dictionary[key]["docID"][index]["position"]}\n')
        dictionaryFile.close()
        postingsLists.close()


def main():
    docCol = DocumentCollection()

    if "-s" in sys.argv or "-stop" in sys.argv:
        docCol.readStopWordsFile("../data/common_words")

    docCol.readDocuments("../data/cacm.all")

    if "-p" in sys.argv or "-porter" in sys.argv:
        docCol.porterStemmingAlgorithm()

    docCol.createDictionary()

    docCol.createFiles()


if __name__ == "__main__":
    main()
