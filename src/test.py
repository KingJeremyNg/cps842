# Jeremy Ng 500882192
# CPS842 Project

import time
from porter import PorterStemmer
from parse import parse


class Dictionary:
    # Constructor
    def __init__(self):
        self.dictionary = {}
        self.porter = False

    # Read output files from invert.py
    def readFiles(self, dictionaryPath, postingsListsPath):
        with open(dictionaryPath, "r") as dictionary:
            if dictionary.readline()[0:-1].split()[1] == "yes":
                self.porter = True
            for line in dictionary:
                term, df = line[0:-1].split()
                self.dictionary[term] = {
                    "df": df,
                    "docID": {}
                }
        dictionary.close()
        with open(postingsListsPath, "r") as postingsLists:
            term = ""
            for line in postingsLists:
                if line.startswith("."):
                    term = line[1:-1]
                else:
                    separator = line.index("[")
                    index, tf = line[0:separator - 1].split()
                    position = line[separator + 1:-2].split(", ")
                    self.dictionary[term]["docID"][index] = {
                        "tf": tf,
                        "position": position
                    }
        postingsLists.close()

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

    # Get abstract information from document
    def getAbstract(self, document, stem, porter):
        if ".W" not in document:
            return "No Abstract"
        start = document.index(".W") + 3
        for search in [".B", ".A", ".N", ".X"]:
            if search in document:
                end = document.index(search)
                break
        document = parse(document[start:end].replace("\n", " "))
        for i in range(len(document)):
            if self.porter:
                if stem == porter.stem(document[i].lower()):
                    middle = i
                    break
            elif not self.porter:
                if stem == document[i].lower():
                    middle = i
                    break
        else:
            return "No Context"
        return " ".join(document[max(0, middle - 10): middle + 11])


if __name__ == "__main__":
    data = Dictionary()
    data.readFiles("../output/dictionary.txt",
                   "../output/postingsLists.txt")
    porter = PorterStemmer()
    times = []
    search = input("Enter Search: ").lower()
    start = time.time()
    while(search != "zzend"):
        start = time.time()
        if data.porter:
            word = porter.stem(search)
        else:
            word = search
        if word in data.dictionary:
            print(
                f'\nThe word "{search}" has been found in {data.dictionary[word]["df"]} document(s)!\n')
            for index in data.dictionary[word]["docID"]:
                tf = data.dictionary[word]["docID"][index]["tf"]
                position = data.dictionary[word]["docID"][index]["position"]
                document = data.getDocument(index)
                print("Index: " + index)
                print("Term Frequency: " + str(tf))
                print("Position: " + ", ".join(position))
                print("Title: " + data.getTitle(document))
                print("Context: " + data.getAbstract(document, word, porter))
                print()
            end = time.time()
            times += [end - start]
            print(f'Search took {round(times[-1], 2)} seconds.')
        else:
            print(f'\nThe word "{search}" does not exist!')
        search = input("\nEnter Search: ").lower()
        start = time.time()
    if times:
        print(f'Average Time: {round(sum(times) / len(times), 2)} seconds.')
    print("Program stopping...")
