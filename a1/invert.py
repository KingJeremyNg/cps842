# Jeremy Ng 500882192
# CPS842 Assignment 1

# You need to write a program invert to do the index construction.
# The input to the program is the document collection.
# The output includes two files - a dictionary file and a postings lists file.

# Each entry in the dictionary should include a term and its document frequency.
# You should use a proper data structure to build the dictionary (e.g. hashmap or search tree or others).
# The structure should be easy for random lookup and insertion of new terms.
# All the terms should be sorted in alphabetical order.

# Postings list for each term should include postings for all documents the term occurs in (in the order of document ID),
# and the information saved in a posting includes document ID,
# term frequency in the document,
# and positions of all occurrences of the term in the document.

# There is a one-to-one correspondence between the term in the dictionary file and its postings list in the postings lists file.


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

    # Function to parse input. **Hard to differentiate "-" between minus or hyphen**
    def parse(self, text):
        chars = ["'s", "'", "-", ".",
                 "(", ")", "{", "}", "[", "]", ":", ";", ",", '"', "*", "/", "?"]
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
        return text.split()

    # Function to read and parse files
    def readFiles(self, collection, stopWordsFile):
        # Open and read common_words files
        with open(stopWordsFile, "r") as words:
            for word in words:
                # [0:-1] to remove newline character
                self.stopWords.add(word[0:-1])

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
                            if word not in self.stopWords:
                                title += [word]
                    if mode == ".W":
                        for word in self.parse(line[0:-1].lower()):
                            if word not in self.stopWords:
                                abstract += [word]
                    if mode == ".B":
                        date = line[0:-1]
                    if mode == ".A":
                        authors.append(line[0:-1])
            # Edge case for last index
            self.addDocument(index, title, abstract, date, authors)

    # Add to dictionary
    def addToDictionary(self, index, word):
        if word not in self.dictionary:
            self.dictionary[word] = {
                "df": 1,
                "docID": {
                    index: 1
                },
            }
        else:
            self.dictionary[word]["df"] += 1
            if index not in self.dictionary[word]["docID"]:
                self.dictionary[word]["docID"][index] = 1
            else:
                self.dictionary[word]["docID"][index] += 1

    # Create word dictionary
    def createDictionary(self):
        for key in self.index:
            for word in self.index[key]["title"]:
                self.addToDictionary(key, word)
            for word in self.index[key]["abstract"]:
                self.addToDictionary(key, word)


if __name__ == "__main__":
    docCol = DocumentCollection()
    docCol.readFiles("./cacm.all", "./common_words")
    # for key in docCol.index:
    #     print(key, docCol.index[key])
    #     print()
    # print(docCol.index["3204"]["title"], docCol.index["3204"]["abstract"])
    # print(docCol.index["335"]) # Equation
    docCol.createDictionary()
    # for key in sorted(docCol.dictionary):
    #     print(key, docCol.dictionary[key])
