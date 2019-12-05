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

import sys
sys.stdout = open('output.txt', 'w')

# classes = ['Fiction','Fantasy','Romance',
#             'Paranormal','Mystery','Young Adult',
#             'Classics','Contemporary','Childrens','Cultural','Literature',
#             'Sequential Art','Thriller','European Literature','Religion','History']

classes = ['Fiction','Fantasy','Romance',
             'Paranormal','History','Young Adult','Mystery']


redis_connection = redis.StrictRedis(host="localhost",
                                     port=int(6379),
                                     decode_responses=True)
stops = stopwords.words('english')

snow = nltk.stem.SnowballStemmer('english')
df = pandas.read_csv('book_data2.csv',nrows=32400,header=0)

df['book_desc'].dropna(inplace=True)
df['genres'].dropna(inplace=True)
tokenizer = RegexpTokenizer(r'[a-zA-Z]+')

j = 0
documents = {}

wordGenreObj = collections.defaultdict(dict)
docObj = collections.defaultdict(dict)
genreObj = {}
totalWords = set()


for i in range(len(df)):

    try:
        tokens = tokenizer.tokenize(df.book_desc[i])
        #tokens = tokenizer.tokenize(df.book_title[i])
        # tokensset = set()
       
        # tokensset.update(tokens)
        # tokensset.update(tokens1)
        # for tok in tokens1:
        #     tokens.append(tok)
     
        genresvar = (df.genres[i]).split("|")
        genresvar = list(set(genresvar))
        tokens_new =[]

        for word in tokens:
            word = word.lower()
            word = word+"CLASS"
            if word not in stops:
                tokens_new.append(word)
                 #word = snow.stem(word)
                if word not in wordGenreObj:
                    wordGenreObj[word] = {}
                for genre in genresvar:
                    if genre in classes:
                        genre = genre + "GENRE"
                        if word in wordGenreObj:
                            wordValue = wordGenreObj.get(word)
                            if genre in wordValue.keys():
                                genreVal = wordGenreObj[word][genre]
                                wordGenreObj[word][genre] = genreVal + 1
                            else:
                                wordGenreObj[word][genre] = 1
        for genre in genresvar:
            if genre in classes:
                genre = genre + "GENRE"
                if genre in genreObj:
                    value = genreObj.get(genre)
                    genreObj[genre] = value + len(tokens_new)
                    totalWords.update(tokens_new)
                else:
                    genreObj[genre] = len(tokens_new)
                    totalWords.update(tokens_new)
    except:
        continue

for key in genreObj:
    #print(genreObj[key])
    redis_connection.set(key, genreObj[key])


# for wordKey in wordGenreObj:
#     wordValue = wordGenreObj.get(wordKey)
#     for genre in list(wordValue):
#         genreVal = wordGenreObj[wordKey][genre]
#         #wordGenreObj[wordKey][genre] = (genreVal)/(genreObj[genre])

#         wordGenreObj[wordKey][genre] = genreVal
#         val = wordGenreObj[wordKey][genre]
#         dict1 = wordGenreObj[wordKey]
        # if(val < 0.0001):
        #     del dict1[genre]

for key in wordGenreObj:
    if len(wordGenreObj[key]) > 0:
        redis_connection.hmset(key, wordGenreObj[key])

# totalWords=0
# for genre in genreObj:
#     totalWords = totalWords + genreObj[genre]

redis_connection.set("TOTALWORDS", len(totalWords))


    
