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

tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
stops = stopwords.words('english')
redis_connection = redis.StrictRedis(host="localhost",
                                     port=int(6379),
                                     decode_responses=True)

#query = "Siddhartha"

obj = {}
arr = []


df = pandas.read_csv('book_data2.csv', header=0, skiprows=range(1, 32400), nrows = 1)
# classes = ['Fiction','Fantasy','Romance',
#             'Paranormal','Mystery','Young Adult',
#             'Classics','Contemporary','Childrens','Cultural','Literature',
#             'Sequential Art','Thriller','European Literature','Religion','History']

classes = ['Fiction','Fantasy','Romance',
             'Paranormal','History','Young Adult','Mystery']


recall = 0
precision = 0


#def classifier(query,maingenre,df,precision):
def classifier(query):
    finalData = collections.defaultdict(dict)
    largest = []
    tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
    tokens = tokenizer.tokenize(query)
    
#tokens = tokenizer.tokenize(query)
    genreSet = set()
    for token in tokens:
        token = token.lower()
        token = token + "CLASS"
        if token not in stops:
            if redis_connection.exists(token):
            #if token in wordGenreObj:
                c = redis_connection.hgetall(token)
                genreSet.update(c.keys())


    # print("-------genreset--------")
    # print(genreSet)
    sumDen =0
    genreProbablity = {}
    count=0
    totalWords = 0
    largest = []
    if len(genreSet)>0:
        #print(genreSet)
        for genre in genreSet:
            finalData[genre] = {}
            finalData[genre]['Query']={}
            genreRedisProb = float(redis_connection.get(genre))
            totalWords = float(redis_connection.get('TOTALWORDS'))
            genreRedisProb = float(genreRedisProb + totalWords)
            probablity = 0

            for word in tokens:
                l=[]
                
                word=word.lower()
                word1 = word
                word = word + "CLASS"
                if word not in stops:
                    if redis_connection.exists(word):
                    #if word in wordGenreObj:
                        c = redis_connection.hgetall(word)
                       
                        
                        #val = wordGenreObj.get(word)
                        if genre in c.keys():
                            l.append(c[genre])
                            l.append(genreRedisProb)
                            l.append(np.log(float(c[genre])/genreRedisProb))
                            probablity = probablity + np.log(float(c[genre])/genreRedisProb)
                        # else:
                        #     probablity = probablity * 0.1
                        
                        
                        # print("-------prob------" )
                        # print(genre + word)
                        # print(str(probablity))
                    else:
                        #count=count+1
                        l.append(1)
                        l.append(genreRedisProb)
                        l.append(1/genreRedisProb)
                        probablity = probablity + (1/genreRedisProb)
                    finalData[genre]['Query'][word1] = l
            
            c1 = redis_connection.get(genre)
            # words = redis_connection.get('TOTALWORDS')

                
            #genreProbablity[genre] = float(probablity) * float(int(c1)/int(words))
            genreProbablity[genre] = float(probablity) + np.log(float(int(c1)/int(totalWords)))
            
        #     sumDen = sumDen + genreProbablity[genre]

        #     # print("--------sumden-----------")
        #     # print(sumDen)

            
        sum =0
        # for genre in genreSet:
        #     val = genreProbablity.get(genre)
        #     genreProbablity[genre] = val/sumDen
        #     #print(genreProbablity)
        #     value = genreProbablity[genre]
        #     sum=sum+value
            # if(value < 0.1):
            #     del genreProbablity[genre]

        #print(genreProbablity)

        for genre in genreSet:
            finalData[genre]['genreProb']= genreProbablity[genre]
        
           
            #print(genreProbablity)
            value = genreProbablity[genre]
            sum=sum+value

        sum = sum * (-1)
        sum_new = 0
        for key in genreProbablity:
            val = genreProbablity[key]
            val = val + sum
            sum_new = sum_new + val
            genreProbablity[key] = val
            
        for key in genreProbablity:  
            val = genreProbablity[key] 
            genreProbablity[key] = round((val/sum_new) * 100,2)
    
        

        heap = [(-value, key) for key, value in genreProbablity.items()]
        largest = heapq.nsmallest(5, heap)  
        largest = [(key, -value) for value, key in largest]
        # print("----------ACTUAL---------")


        
    else:
        genreProbablity = {}

        
        sum=0

        

        for i in classes:
            i=i+"GENRE"
            finalData[i] = {}
            finalData[i]['Query']={}
            probability=0
            for word in tokens:
                if word not in stops:
                    word = word.lower()
                    word1 = word
                    word = word+"CLASS"
                    l=[]
                    l.append(1)
                    c = float(redis_connection.get(i))
                    c1 = float(redis_connection.get('TOTALWORDS'))
                    c2=c+c1
                    l.append(c2)
                    l.append(np.log(1/c2))
                    probability = probability+np.log(1/c2)
                    finalData[i]['Query'][word1] = l
            probability = probability + np.log(c/c1)
            sum = sum + probability
            print(genreProbablity)
            finalData[i]['genreProb'] =  probability
            genreProbablity[i] = probability

        sum_new=0
        sum = sum * (-1)
        for key in genreProbablity:
            val = genreProbablity[key]
            val = val + sum
            sum_new = sum_new + val
            genreProbablity[key] = val
            
        for key in genreProbablity:  
            val = genreProbablity[key] 
            genreProbablity[key] = round((val/sum_new) * 100,2)
        heap = [(-value, key) for key, value in genreProbablity.items()]
        largest = heapq.nsmallest(5, heap)
        largest = [(key, -value) for value, key in largest]

    finalObject= collections.defaultdict(dict)
    for key in largest:

        val = key[0]
        val2 = key[1]


        try:
            finalObject[val]['genrePercent'] = val2
            finalObject[val]['Query'] = collections.defaultdict(dict)
            finalObject[val]['Query'] = finalData[val]['Query']
            finalObject[val]['genreProb'] = finalData[val]['genreProb']

        except:

            continue
  
    #print(finalObject)
    return finalObject
    # arr1=[]
    # for key in largest:
    #     val=key[0].replace('GENRE','')
    #     arr1.append(val)
    
    # intersection = list(set(maingenre) & set(arr1))
    # num = len(intersection)+2
    # finalset = set()
    # finalset.update(arr1)
    # finalset.update(maingenre)
    # den = len(finalset)
    # if (den ==0):
    #     den = 1

    # den1 = len(set(maingenre))+1

    
    # precision = precision + (num/den)

    # #recall = recall +(num/den)


   
    
    # arr.append([df,list(set(maingenre) & set(arr1))])
    # df2 = pandas.DataFrame(arr,
    #                 columns=['Title', 'Intersection'])

    
    # #print(df2)
    # return precision


# for i in range(len(df)):

#     try:
#         # tokens = tokenizer.tokenize(df.book_desc[i])
#         tokens = tokenizer.tokenize(df.book_desc[i])
#         #print("---------EXPECTED---------")
#         #print(tokens)
#         maingenre=[]
#         genretokens = (df.genres[i]).split("|")
     
#         for genre in genretokens:
#             if genre in classes:
               
#                 maingenre.append(genre)
#         #print(df.genres[i])
#         # tokens1 = tokenizer.tokenize(df.book_title[i])
#         # for tok in tokens1:
#         #     tokens.append(tok)

#     except:
#         continue

#     #classifier(df.book_desc[i], maingenre,df.book_title[i],precision)
#     classifier("winning")
  
#print(precision/5)

# val = classifier('abcdefg')
# print(val)








