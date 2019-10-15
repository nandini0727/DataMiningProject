import collections
import math
from nltk.tokenize import RegexpTokenizer
import numpy as np
import pandas
from stop_words import get_stop_words
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import heapq
import json
import redis
import time
import nltk

snow = nltk.stem.SnowballStemmer('english')
start_time = time.time()
redis_connection = redis.StrictRedis(host="localhost",
                                     port=int(6379),
                                     decode_responses=True)

stops = stopwords.words('english')
stemmer = PorterStemmer()
N = 54301


def getMaxFrequency(query_tokens):
    max = 0
    res = query_tokens[0]
    for i in query_tokens:
        freq = query_tokens.count(i)
        if freq > max:
            max = freq
            res = i
    res1 = query_tokens.count(res)
    return res1


l = []


def getList(dict):
    for key in dict.keys():
        l.append(key)
    return l


def getQueryTokens(query):
    tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
    tokens = tokenizer.tokenize(query)

    query_tokens = []
    for token in tokens:
        token = token.lower()
        if token not in stops:
            query_tokens.append(token)
            token = snow.stem(token)
            query_tokens.append(token)
    return query_tokens


def calculateTFIDFSUM(query):
    tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
    tokens = tokenizer.tokenize(query)
    docsval = {}

    query_tokens = []
    for token in tokens:
        token = token.lower()
        if token not in stops:
            #token = stemmer.stem(token)
            token = snow.stem(token)
            query_tokens.append(token)

    if not query_tokens:
        return []

    docs_set = set()

    for token in query_tokens:
        c = redis_connection.hgetall(token)
        docsval[token] = c
        docs_set.update(c.keys())
    finaltfidf = {}

    for docs in docs_set:
        sum = 0
        for val in docsval:

            doctfidf = docsval[val]
            if docs in doctfidf:

                sum = sum + float(doctfidf[docs])

            finaltfidf[docs] = sum

    heap = [(-value, key) for key, value in finaltfidf.items()]
    largest = heapq.nsmallest(20, heap)
    largest = [(key, -value) for value, key in largest]

    finalObject = {}

    for key in largest:

        val = key[0]
        val2 = key[1]

        try:

            if redis_connection.hgetall(val) is not None:
                finalObject[val] = redis_connection.hgetall(val)
                finalObject[val]['tfidf'] = val2

        except:

            continue

    return finalObject
