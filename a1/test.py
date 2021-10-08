# Jeremy Ng 500882192
# CPS842 Assignment 1

from porter import PorterStemmer
import time


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
    def getDocument(self, index, filePath="./data/cacm.all"):
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


    # Simple parser
    def parse(self, text):
        chars = ["'s", "'", "-", ".",
                "(", ")", "{", "}", "[", "]", ":", ";", ",", '"', "*", "/", "?", "!", "$", "`"]
        for char in chars:
            if char in text:
                text = text.replace(char, " ")
        operators = {
            "<=": " less than or equal to ",
            ">=": " greater than or equal to ",
            "=": " equal to ",
            "<": " less than ",
            ">": " greater than ",
            "+": " add ",
            "^": " raised to the power of ",
            "&": " and ",
            "%": " percent ",
            "+": " plus "
        }
        for key, val in operators.items():
            if key in text:
                text = text.replace(key, val)
        return text.split()


    def getAbstract(self, document, stem, porter):
        if ".W" not in document:
            return "No Abstract"
        start = document.index(".W") + 3
        for search in [".B", ".A", ".N", ".X"]:
            if search in document:
                end = document.index(search)
                break
        document = self.parse(document[start:end].replace("\n", " "))
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
    data.readFiles("./output/dictionary.txt",
                   "./output/postingsLists.txt")
    porter = PorterStemmer()
    times = []
    search = input("Enter Search: ").lower()
    start = time.time()
    while(search != "zzend"):
        start = time.time()
        if data.porter:
            stem = porter.stem(search)
        else:
            stem = search
        if stem in data.dictionary:
            print(
                f'\nThe word "{search}" has been found in {data.dictionary[stem]["df"]} document(s)!\n')
            for index in data.dictionary[stem]["docID"]:
                tf = data.dictionary[stem]["docID"][index]["tf"]
                position = data.dictionary[stem]["docID"][index]["position"]
                document = data.getDocument(index)
                print("Index: " + index)
                print("Term Frequency: " + str(tf))
                print("Position: " + ", ".join(position))
                print("Title: " + data.getTitle(document))
                print("Context: " + data.getAbstract(document, stem, porter))
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
