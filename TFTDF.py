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
import sys
from ast import literal_eval
from collections import OrderedDict

snow = nltk.stem.SnowballStemmer('english')
start_time = time.time()
redis_connection = redis.StrictRedis(host="localhost",
                                     port=int(6379),
                                     decode_responses=True)

stops = stopwords.words('english')
stemmer = PorterStemmer()
N = 54301

sys.stdout = open('output.txt', 'w')


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

def getPhraseQueryTokens(query):
    tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
    tokens = tokenizer.tokenize(query)

    query_tokens = []
    for token in tokens:
        if redis_connection.exists(token):
            token = token.lower()
            
            query_tokens.append(token)
       
    return query_tokens





def calculateTFIDFSUM(query):
    type=0
    if '"' in query:
        type=1
    tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
    tokens = tokenizer.tokenize(query)
    docsval = {}
    query_tokens = []
    for token in tokens:
        
        token = token.lower()
        if token not in stops:
            #token = stemmer.stem(token)
            token = snow.stem(token)
            if redis_connection.exists(token):
                query_tokens.append(token)

    if not query_tokens:
        return []

    
          

    docs_set = set()


   
    finaltfidf = {}

    postingList = []
  
    if(type == 1):
        dset=set()
        for token in query_tokens:
            c = redis_connection.get(token)
            c = json.loads(c)
            docsval[token] = c
            l= []
            l = c.keys()
            postingList.append(l)
        
       

        dset = set(postingList[0]).intersection(*postingList) 
        dset.remove("IDF")

        for doc in dset:
            positionList = []
            for val in docsval:
                positionList.append(docsval[val][doc][1])

    
            for i in range(len(positionList)):
                for j in range(len(positionList[i])):
                    
                    positionList[i][j] = positionList[i][j] - i

            hasVal = set(positionList[0]).intersection(*positionList)

            if(len(hasVal) != 0):

                c = redis_connection.hgetall(doc)
                desc = c['description'].lower()
                query = query.replace('"','').lower()
                
                if query in desc:
                    docs_set.add(doc)

  

    else:

        for token in query_tokens:
            if redis_connection.exists(token):
                c1 = redis_connection.get(token)
            
                c = json.loads(c1)
            
                docsval[token] = c
                
                docs_set.update(c.keys())
                docs_set.remove('IDF')
              
        
    #     QueryVec = {}
    #     Qmagnitude = 0
    #     for token in query_tokens:
    #         if token in QueryVec:
    #             val = QueryVec.get(token)
    #             QueryVec[token] = val[0]+1
    #         else:
    #             l=[]
    #             l.append(1)
    #             l.append(docsval[token]["IDF"])
    #             QueryVec[token] = l  

    #     for token in query_tokens:
    #         val = QueryVec[token][0]
    #         QueryVec[token][0] =  val/len(query_tokens)
        
    #     for token in query_tokens:
    #         QueryTFIDF = QueryVec[token][0] * QueryVec[token][1]
    #         Qmagnitude = Qmagnitude + ((QueryTFIDF)*(QueryTFIDF))
    #     Qmagnitude = math.sqrt(Qmagnitude)



    # for docs in docs_set:
    #     numerator=0
    #     denominator=0
    #     denDoc=0
    #     denQuery=0

    #     for val in query_tokens:

    #         # print(val)
    #         # print(docs)

    #         # print("queryvec")
    #         # print(QueryVec)
        
    #         docsData = docsval[val]

    #         # print("docsdata")
    #         # print(docsData)
           
    #         if docs in docsData:
             
    #             queryvecval = QueryVec[val]
              
    #             docvecval = docsData[docs]

    #             QueryTFIDF = queryvecval[0] * queryvecval[1]

    #             # print("QueryTFIDF")
    #             # print(QueryTFIDF)

    #             denDoc = denDoc + ((docvecval[0]) * (docvecval[0]))

    #             # print("denominatordoc")
    #             # print(denDoc)

    #             # denQuery = denQuery + (QueryTFIDF * QueryTFIDF)
                
    #             # print("denquery")
    #             # print(denQuery)
            
    #             numerator = numerator + (QueryTFIDF * docvecval[0])
    #             # print("numerator")
    #             # print(numerator)

    #     denDoc = math.sqrt(denDoc)
    #     #denQuery = math.sqrt(denQuery)        
    #     # c = redis_connection.hgetall(docs)
    #     # denominator = float(Qmagnitude) * float(c["magnitude"])
    #     denominator = denDoc * Qmagnitude
    #     # print("denominator")
    #     # print(denominator)
    #     finaltfidf[docs] = float(numerator) / float(denominator)

    #     # print("finaltfiddfdocs")
    #     # print(finaltfidf)


  
    finalObject1 = OrderedDict()
    finalObject= collections.defaultdict(dict)
    for docs in docs_set:
        sum = 0 
        finalObject1[docs] = OrderedDict()
        finalObject1[docs]['Query'] = {}
        for val in docsval:
            l=[]
           
            doctfidf = docsval[val]
            if docs in doctfidf:
                l.append(doctfidf[docs][2])
                l.append(doctfidf["IDF"])
                l.append(doctfidf[docs][0])
                sum = sum + float(doctfidf[docs][0])
            else:
                l.append(0.00)
                l.append(doctfidf["IDF"])
                l.append(0.00)
            finaltfidf[docs] = sum
            finalObject1[docs]['Query'][val] = l

    heap = [(-value, key) for key, value in finaltfidf.items()]
    largest = heapq.nsmallest(20, heap)
    largest = [(key, -value) for value, key in largest]

    

  
  
    for key in largest:

        val = key[0]
        val2 = key[1]


        try:

            if redis_connection.hgetall(val) is not None:
                c = redis_connection.hgetall(val)
                finalObject[val]['title'] = c['title']
                finalObject[val]['description'] = c['description']
                finalObject[val]['tfidf'] = val2
                finalObject[val]['Query'] = OrderedDict()
                finalObject[val]['Query'] = finalObject1[val]['Query']
                finalObject[val]['url'] = c['url']

        except:

            continue
   
  
    return finalObject


# val = calculateTFIDFSUM('german girl')
# print(val)