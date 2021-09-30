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

import sys


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
        # *S - The stem ends with S
        vowels = "aeiou"

        # m - Measure of the stem
        def calculateM(word):
            # Vowel followed by Consonant
            count = 0
            for i in range(0, len(word) - 1):
                if word[i] in vowels and word[i + 1] not in vowels:
                    count += 1
            return count

        # *v* - the stem contains a vowel
        def conditionV(word):
            for vowel in vowels:
                if vowel in word:
                    return True
            return False

        # *o - The stem ends in CVC (second C not W, X or Y)
        def conditionCVC(word):
            if len(word) < 3:
                return False
            if word[-3] not in vowels and word[-2] in vowels and word[-1] not in vowels + "wxy":
                return True
            return False

        # *d - The stem ends with a double consonant
        def conditionD(word):
            if len(word) >= 2 and word[-2] == word[-1] and word[-1] not in vowels:
                return True
            return False

        def step1A(word):
            # SSES --> SS
            if word[-4:] == "sses":
                return step1B(word[0:-4] + "ss")
            # IES --> I
            if word[-3:] == "ies":
                return step1B(word[0:-3] + "i")
            # SS --> SS
            if word[-2:] == "ss":
                return step1B(word)
            # S --> ""
            if word[-1:] == "s":
                return step1B(word[0:-1])
            return step1B(word)

        def step1B(word):
            # (m>0) EED --> EE
            if word[-3:] == "eed" and calculateM(word[0:-3]) > 0:
                return step1C(word[0:-1])
            # (*v*) ED --> ""
            if word[-2:] == "ed" and conditionV(word[0:-2]):
                return cleanup(word[0:-2])
            # (*v*) ING --> ""
            if word[-3:] == "ing" and conditionV(word[0:-3]):
                return cleanup(word[0:-3])
            return step1C(word)

        def cleanup(word):
            # AT --> ATE
            if word[-2:] == "at":
                return step1C(word + "e")
            # BL --> BLE
            if word[-2:] == "bl":
                return step1C(word + "e")
            # IZ --> IZE
            if word[-2:] == "iz":
                return step1C(word + "e")
            # (*d & !(*L or *S or *Z)) --> single letter
            if word[-1:] not in "lsz" and conditionD(word):
                return step1C(word[0:-1])
            # (m=1 & *o) --> E
            if calculateM(word) == 1 and conditionCVC(word):
                return step1C(word + "e")
            return step1C(word)

        def step1C(word):
            # (*v*) Y --> I
            if word[-1:] == "y" and conditionV(word[0:-1]):
                return step2(word[0:-1] + "i")
            return step2(word)

        def step2(word):
            # (m>0) ATIONAL --> ATE
            if word[-7:] == "ational" and calculateM(word[0:-7]) > 0:
                return step3(word[0:-7] + "ate")
            # (m>0) TIONAL --> TION
            if word[-6:] == "tional" and calculateM(word[0:-6]) > 0:
                return step3(word[0:-2])
            # (m>0) ENCI --> ENCE
            if word[-4:] == "ence" and calculateM(word[0:-4]) > 0:
                return step3(word[0:-1] + "e")
            # (m>0) ANCI --> ANCE
            if word[-4:] == "anci" and calculateM(word[0:-4]) > 0:
                return step3(word[0:-1] + "e")
            # (m>0) IZER --> IZE
            if word[-4:] == "izer" and calculateM(word[0:-4]) > 0:
                return step3(word[0:-1])
            # (m>0) ABLI --> ABLE
            if word[-4:] == "abli" and calculateM(word[0:-4]) > 0:
                return step3(word[0:-1] + "e")
            # (m>0) ALLI --> AL
            if word[-4:] == "alli" and calculateM(word[0:-4]) > 0:
                return step3(word[0:-2])
            # (m>0) ENTLI --> ENT
            if word[-4:] == "entli" and calculateM(word[0:-4]) > 0:
                return step3(word[0:-2])
            # (m>0) ELI --> E
            if word[-3:] == "eli" and calculateM(word[0:-3]) > 0:
                return step3(word[0:-1])
            # (m>0) OUSLI --> OUS
            if word[-5:] == "ousli" and calculateM(word[0:-5]) > 0:
                return step3(word[0:-2])
            # (m>0) IZATION --> IZE
            if word[-7:] == "ization" and calculateM(word[0:-7]) > 0:
                return step3(word[0:-5] + "e")
            # (m>0) ATION --> ATE
            if word[-5:] == "ation" and calculateM(word[0:-5]) > 0:
                return step3(word[0:-3] + "e")
            # (m>0) ATOR --> ATE
            if word[-4:] == "ator" and calculateM(word[0:-4]) > 0:
                return step3(word[0:-2] + "e")
            # (m>0) ALISM --> AL
            if word[-5:] == "alism" and calculateM(word[0:-5]) > 0:
                return step3(word[0:-3])
            # (m>0) IVENESS --> IVE
            if word[-7:] == "iveness" and calculateM(word[0:-7]) > 0:
                return step3(word[0:-4])
            # (m>0) FULNESS --> FUL
            if word[-7:] == "fulness" and calculateM(word[0:-7]) > 0:
                return step3(word[0:-4])
            # (m>0) OUSNESS --> OUS
            if word[-7:] == "ousness" and calculateM(word[0:-7]) > 0:
                return step3(word[0:-4])
            # (m>0) ALITI --> AL
            if word[-5:] == "aliti" and calculateM(word[0:-5]) > 0:
                return step3(word[0:-3])
            # (m>0) IVITI --> IVE
            if word[-5:] == "iviti" and calculateM(word[0:-5]) > 0:
                return step3(word[0:-3] + "e")
            # (m>0) BILITI --> BLE
            if word[-6:] == "biliti" and calculateM(word[0:-6]) > 0:
                return step3(word[0:-6] + "ize")
            return step3(word)

        def step3(word):
            # (m>0) ICATE --> IC
            if word[-5:] == "icate" and calculateM(word[0:-5]) > 0:
                return step4(word[0:-3])
            # (m>0) ATIVE --> ""
            if word[-5:] == "ative" and calculateM(word[0:-5]) > 0:
                return step4(word[0:-5])
            # (m>0) ALIZE --> AL
            if word[-5:] == "alize" and calculateM(word[0:-5]) > 0:
                return step4(word[0:-3])
            # (m>0) ICITI --> IC
            if word[-5:] == "iciti" and calculateM(word[0:-5]) > 0:
                return step4(word[0:-3])
            # (m>0) ICAL --> IC
            if word[-4:] == "ical" and calculateM(word[0:-4]) > 0:
                return step4(word[0:-2])
            # (m>0) FUL --> ""
            if word[-3:] == "ful" and calculateM(word[0:-3]) > 0:
                return step4(word[0:-3])
            # (m>0) NESS --> ""
            if word[-4:] == "ness" and calculateM(word[0:-4]) > 0:
                return step4(word[0:-4])
            return step4(word)

        def step4(word):
            # (m>1) AL --> ""
            if word[-2:] == "al" and calculateM(word[0:-2]) > 1:
                return step5A(word[0:-2])
            # (m>1) ANCE --> ""
            if word[-4:] == "ance" and calculateM(word[0:-4]) > 1:
                return step5A(word[0:-4])
            # (m>1) ENCE --> ""
            if word[-4:] == "ence" and calculateM(word[0:-4]) > 1:
                return step5A(word[0:-4])
            # (m>1) ER --> ""
            if word[-2:] == "er" and calculateM(word[0:-2]) > 1:
                return step5A(word[0:-2])
            # (m>1) IC --> ""
            if word[-2:] == "ic" and calculateM(word[0:-2]) > 1:
                return step5A(word[0:-2])
            # (m>1) ABLE --> ""
            if word[-4:] == "able" and calculateM(word[0:-4]) > 1:
                return step5A(word[0:-4])
            # (m>1) IBLE --> ""
            if word[-4:] == "ible" and calculateM(word[0:-4]) > 1:
                return step5A(word[0:-4])
            # (m>1) ANT --> ""
            if word[-3:] == "ant" and calculateM(word[0:-3]) > 1:
                return step5A(word[0:-3])
            # (m>1) EMENT --> ""
            if word[-5:] == "ement" and calculateM(word[0:-5]) > 1:
                return step5A(word[0:-5])
            # (m>1) MENT --> ""
            if word[-4:] == "ment" and calculateM(word[0:-4]) > 1:
                return step5A(word[0:-4])
            # (m>1) ENT --> ""
            if word[-3:] == "ent" and calculateM(word[0:-3]) > 1:
                return step5A(word[0:-3])
            # (m>1 and (*S or *T)) ION --> ""
            if word[-3:] == "ion" and word[-3:][-1] in "st" and calculateM(word[0:-3]) > 1:
                return step5A(word[0:-3])
            # (m>1) OU --> ""
            if word[-2:] == "ou" and calculateM(word[0:-2]) > 1:
                return step5A(word[0:-2])
            # (m>1) ISM --> ""
            if word[-3:] == "ism" and calculateM(word[0:-3]) > 1:
                return step5A(word[0:-3])
            # (m>1) ATE --> ""
            if word[-3:] == "ate" and calculateM(word[0:-3]) > 1:
                return step5A(word[0:-3])
            # (m>1) ITI --> ""
            if word[-3:] == "iti" and calculateM(word[0:-3]) > 1:
                return step5A(word[0:-3])
            # (m>1) OUS --> ""
            if word[-3:] == "ous" and calculateM(word[0:-3]) > 1:
                return step5A(word[0:-3])
            # (m>1) IVE --> ""
            if word[-3:] == "ive" and calculateM(word[0:-3]) > 1:
                return step5A(word[0:-3])
            # (m>1) IZE --> ""
            if word[-3:] == "ize" and calculateM(word[0:-3]) > 1:
                return step5A(word[0:-3])
            return step5A(word)

        def step5A(word):
            # (m>1) E --> ""
            if word[-1:] == "e" and calculateM(word[0:-1]) > 1:
                return step5B(word[0:-1])
            # (m=1 & !*o) NESS --> ""
            if word[-4:] == "ness" and calculateM(word[0:-4]) == 1 and not conditionCVC(word[0:-4]):
                return step5B(word[0:-4])
            return step5B(word)

        def step5B(word):
            # (m>1 & *d & *L) --> single letter
            if conditionD(word) and calculateM(word) > 1:
                return word[0:-1]
            return word

        for key in self.index:
            for i in range(len(self.index[key]["title"])):
                self.index[key]["title"][i] = step1A(
                    self.index[key]["title"][i])
            for i in range(len(self.index[key]["abstract"])):
                self.index[key]["abstract"][i] = step1A(
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
        dictionaryFile = open("dictionary.txt", "w")
        postingsLists = open("postingsLists.txt", "w")
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
        docCol.readStopWordsFile("./common_words")

    docCol.readDocuments("./cacm.all")

    if "-p" in sys.argv or "-porter" in sys.argv:
        docCol.porterStemmingAlgorithm()

    # for key in docCol.index:
    #     print(key, docCol.index[key])
    #     print()
    # print(docCol.index["3204"]["title"], docCol.index["3204"]["abstract"])
    # print(docCol.index["335"]) # Equation
    docCol.createDictionary()
    # for key in sorted(docCol.dictionary):
    #     print(key)
    #     print(docCol.dictionary[key])
    docCol.createFiles()
    # print(docCol.index["1197"])
    # print(docCol.dictionary["magnitude"]["docID"]["1197"])
    # print(docCol.dictionary["magnitud"])
