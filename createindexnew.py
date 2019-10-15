import collections
import math
from nltk.tokenize import RegexpTokenizer
import numpy as np
import pandas
from stop_words import get_stop_words
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import nltk
import heapq
import json
import redis

redis_connection = redis.StrictRedis(host="localhost",
                                     port=int(6379),
                                     decode_responses=True)

stops = stopwords.words('english')
stemmer = PorterStemmer()
snow = nltk.stem.SnowballStemmer('english')
df = pandas.read_csv('book_data.csv')

df['book_desc'].dropna(inplace=True)
tokenizer = RegexpTokenizer(r'[a-zA-Z]+')

j = 0
documents = {}

inverted_index = collections.defaultdict(dict)
docObj = collections.defaultdict(dict)

for i in range(len(df)):
    objRow = {}
    docmainID = "doc" + str(df.id[i])
    try:
        objRow['title'] = df.book_title[i]
        objRow['description'] = df.book_desc[i]


        docObj[docmainID] = objRow
    except:
        continue
   

    try:
        tokens = tokenizer.tokenize(df.book_desc[i])
        tokens1 = tokenizer.tokenize(df.book_title[i])
        for tok in tokens1:
            tokens.append(tok)
        
        print(tokens)
        tokens_new = []
        for word in tokens:
            word = word.lower()
            if word not in stops:
                #word = stemmer.stem(word)
                word = snow.stem(word)
                tokens_new.append(word)
            docID = "doc" + str(df.id[i])
            if word in inverted_index:
                values = inverted_index.get(word)
                if docID in values.keys():
                    value = inverted_index[word][docID]
                    inverted_index[word][docID] = value + 1
                else:

                    inverted_index[word][docID] = 1

            else:
                doc_index = {}
                doc_index[docID] = 1
                inverted_index[word] = doc_index

        documents[docID] = tokens_new

    except:
        continue
for key in docObj:
    redis_connection.hmset(key, docObj[key])

# for key in inverted_index:
#     redis_connection.hmset(key, inverted_index[key])

tfidfvec = collections.defaultdict(dict)

for document in documents:
    docID = document
    documentLength = document.__len__()

    for term in documents[document]:
        tfidfList = []
        frequency = inverted_index[term].keys().__len__()
        idf = math.log((documents.__len__() / frequency), 2)

        tf = inverted_index[term][docID]/documentLength

        # tfidfList = [tf,idf,tf*idf]

        if term in tfidfvec:
            value = tfidfvec.get(term)
           
            if docID not in value:
                tfidfvec[term][docID] = tf*idf
        else:
            docvector={}
            docvector[docID] = tf*idf
            tfidfvec[term] = docvector

for key in tfidfvec:
    redis_connection.hmset(key, tfidfvec[key])











