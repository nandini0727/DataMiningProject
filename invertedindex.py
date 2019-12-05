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

redis_connection = redis.StrictRedis(host="localhost",
                                     port=int(6379),
                                     decode_responses=True)

sys.stdout = open('output.txt', 'w')

stops = stopwords.words('english')
stemmer = PorterStemmer()
snow = nltk.stem.SnowballStemmer('english')
df = pandas.read_csv('CSV3.csv')

df['actual_caption'].dropna(inplace=True)
tokenizer = RegexpTokenizer(r'[a-zA-Z]+')

j = 0
documents = {}

inverted_index = collections.defaultdict(dict)
docObj = collections.defaultdict(dict)

for i in range(len(df)):
    objRow = {}
    docmainID = "document" + str(df.ID[i])
    try:
        objRow['imageURL'] = df.URL[i]
        objRow['actual'] = df.actual_caption[i]
        objRow['collab'] = df.google_colab_caption[i]


        docObj[docmainID] = objRow
    except:
        continue
   

    try:
        tokens = tokenizer.tokenize(df.actual_caption[i])
        tokens1 = tokenizer.tokenize(df.google_colab_caption[i])
        for tok in tokens1:
            tokens.append(tok)
        
        tokens_new = []
        pos = 0
       
        for word in tokens:
            word = word.lower()
            if word not in stops:
                #word = stemmer.stem(word)
                word = snow.stem(word)
                word = word + "IMAGE"
                tokens_new.append(word)
                docID = "document" + str(df.ID[i])
                if word in inverted_index:
                    values = inverted_index.get(word)
                    if docID in values.keys():
                        value = inverted_index[word][docID]
                        #value[1].append(pos)
                        value[0] = value[0]+1
                        
                        #inverted_index[word][docID]
                    else:

                        #inverted_index[word][docID] = [1,[pos]]
                        inverted_index[word][docID] = [1]

                else:
                    doc_index = {}
                    #doc_index[docID] = [1,[pos]]
                    doc_index[docID] = [1]
                    inverted_index[word] = doc_index
                #pos = pos+1

        documents[docID] = tokens_new

    except:
        continue



tfidfvec = collections.defaultdict(dict)

for document in documents:
    docID = document
    documentLength = len(documents[document])
    magnitude = 0
   
    for term in documents[document]:
        
        tfidfList = []
        frequency = len(inverted_index[term].keys())
        idf = np.log((len(documents) / (frequency+1)))

        tf = inverted_index[term][docID][0]/documentLength

        if term in tfidfvec:
            value = tfidfvec.get(term)
            
           
            if docID not in value.keys():
                val = []
                val.append(tf*idf)
                val.append(tf)
                # positionList = inverted_index[term][docID][1]
                # val.append(positionList)
                # #val.append(idf)
                # #docvector[docID] = val
                tfidfvec[term][docID] = val
                tfidfvec[term]["IDF"] = idf


        else:
            docvector={}
            val = []
           # val = docvector.get(docID)
            val.append(tf*idf)
            val.append(tf)
            #docvector[docID] = [tf*idf,[]]
            # position = inverted_index[term][docID][1]
            # val.append(position)
            #val.append(idf)
            docvector[docID] = val
            docvector["IDF"] = idf
            

            tfidfvec[term] = docvector

        magnitude = magnitude + ((tf*idf)*(tf*idf))
    magnitude = math.sqrt(magnitude)
    docObj[document]["magnitude"] = magnitude


for key in docObj:
    redis_connection.hmset(key, docObj[key])


for key in tfidfvec:
    val = tfidfvec[key]

    rval = json.dumps(val)
    redis_connection.set(key, rval)



# value = redis_connection.get('masterpiec')
# value = json.loads(value)
# print(value)
# print(value['doc3'])











