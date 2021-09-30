# Jeremy Ng 500882192
# CPS842 Assignment 1

import sys
from porter import PorterStemmer


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

    def readStopWordsFile(self, file):
        # Open and read common_words files
        with open(file, "r") as words:
            for word in words:
                # [0:-1] to remove newline character
                self.stopWords.add(word[0:-1])

    # Function to parse input. **Hard to differentiate "-" between minus or hyphen**
    def parse(self, text):
        chars = ["'s", "'", "-", ".",
                 "(", ")", "{", "}", "[", "]", ":", ";", ",", '"', "*", "/", "?", "!", "$"]
        for char in chars:
            if char in text:
                text = text.replace(char, " ")
        if "<=" in text:
            text = text.replace("<=", " less than or equal to ")
        if ">=" in text:
            text = text.replace("<=", " greater than or equal to ")
        if "=" in text:
            text = text.replace("=", " equal to ")
        if "<" in text:
            text = text.replace("<", " less than ")
        if ">" in text:
            text = text.replace("<", " greater than ")
        if "+" in text:
            text = text.replace("<", " add ")
        if "^" in text:
            text = text.replace("^", " raised to the power of ")
        if "&" in text:
            text = text.replace("&", " and ")
        if "%" in text:
            text = text.replace("%", " percent ")
        if "+" in text:
            text = text.replace("+", " plus ")
        return text.split()

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
            for line in document:
                if line.startswith(".I"):
                    # Store previous index information
                    self.addDocument(index, title, abstract, date, authors)
                    # Clear variables and set new index
                    index = line.split(" ")[-1][0:-1]
                    title = []
                    abstract = []
                    date = ""
                    authors = []
                # Set mode
                elif line.startswith(".T"):
                    mode = ".T"
                elif line.startswith(".W"):
                    mode = ".W"
                elif line.startswith(".B"):
                    mode = ".B"
                elif line.startswith(".A"):
                    mode = ".A"
                elif line.startswith(".X"):
                    mode = ".X"
                elif line.startswith(".N"):
                    mode = ".N"
                # If line is not setting mode then store data. [0:-1] to remove newline character
                else:
                    if mode == ".T":
                        for word in self.parse(line[0:-1].lower()):
                            if "-s" in sys.argv or "-stop" in sys.argv:
                                if word not in self.stopWords:
                                    title += [word]
                            else:
                                title += [word]
                    if mode == ".W":
                        for word in self.parse(line[0:-1].lower()):
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

    def porterStemmingAlgorithm(self):
        porter = PorterStemmer()
        for key in self.index:
            for i in range(len(self.index[key]["title"])):
                self.index[key]["title"][i] = porter.stem(
                    self.index[key]["title"][i], 0, len(self.index[key]["title"][i]) - 1)
            for i in range(len(self.index[key]["abstract"])):
                self.index[key]["abstract"][i] = porter.stem(
                    self.index[key]["abstract"][i], 0, len(self.index[key]["abstract"][i]) - 1)

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
            self.dictionary[word]["df"] += 1
            if index not in self.dictionary[word]["docID"]:
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

    def createFiles(self):
        dictionaryFile = open("./output/dictionary.txt", "w")
        postingsLists = open("./output/postingsLists.txt", "w")
        for key in sorted(self.dictionary):
            dictionaryFile.write(f'{key} {self.dictionary[key]["df"]}\n')
            postingsLists.write(f'.{key}\n')
            for index in self.dictionary[key]["docID"]:
                postingsLists.write(
                    f'{index} {self.dictionary[key]["docID"][index]["tf"]} {self.dictionary[key]["docID"][index]["position"]}\n')
        dictionaryFile.close()
        postingsLists.close()


if __name__ == "__main__":
    docCol = DocumentCollection()

    if "-s" in sys.argv or "-stop" in sys.argv:
        docCol.readStopWordsFile("./data/common_words")

    docCol.readDocuments("./data/cacm.all")

    if "-p" in sys.argv or "-porter" in sys.argv:
        docCol.porterStemmingAlgorithm()

    docCol.createDictionary()

    docCol.createFiles()
