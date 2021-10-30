# Table of contents
* [Introduction](#introduction)
* [Technologies](#technologies)
* [Usage](#usage)
* [Arguments](#arguments)
* [Methods](#methods)
* [Results](#results)

# Introduction
This is a python project that implements various Info Retrieval methods and evaluations on a collection of documents.

# Technologies
This project is created with:
* Python version: 3.7.4
* Vivake Gupta's Python implementation of Porter's Stemming Algorithm.

# Usage
To run this project, install the files locally and run using python command line within the `src` directory:
```
$ cd src
$ python search.py
$ python eval.py
```

# Arguments
All files support the following arguments:
| Argument      | Description                        |
|---------------|------------------------------------|
| -s \| -stop   | Enable stop word removal           |
| -p \| -porter | Enable Porter's Stemming Algorithm |

Example Usage:
```
$ python search.py -s -p
$ python eval.py -stop -porter
```

# Methods
In this project, the postings lists generated is ordered by term, alphabetically. My `search.py` program implements a Heuristic Top-K Retrieval method with `k=10`.

To calculate cosine similarity scores:
* Find all documents containing at least 1 word from query
* Calculate weight of each term for each document using TF-IDF weighting scheme where TF is `1+log(F)` and IDF is `log(N/DF)`
* Finally, take of dot product of document and query divided by the magnitude of document times the magnitude of query.

# Results
By using a list of queries from `query.text` and passing it through `eval.py`, we can assess the average `MAP` and `R-Precision` values

```
$ python eval.py -s -p
Average MAP: 0.1
Average R-Precision: 0.31
```
```
$ python eval.py -p
Average MAP: 0.1
Average R-Precision: 0.31
```
```
$ python eval.py -s
Average MAP: 0.1
Average R-Precision: 0.31
```
```
$ python eval.py
Average MAP: 0.1
Average R-Precision: 0.28
```