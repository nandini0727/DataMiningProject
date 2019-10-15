# DataMiningProject
Book description Search using TF-IDF.
Motive: What if you had a book search technique based on book description? It provides user the flexibility to search books based on his search query and explore new possibilities.
Goal: To implement a search technique on good reads book data set using TF-IDF and Cosine similarity. We show top 20 documents with highest TF-IDF matching the search query.
Data Set: https://www.kaggle.com/meetnaren/goodreads-best-books
Technology Stack: Apache Flask, Python, Redis.
How this is implemented:
Configure an EC2 instance with ubuntu linux distribution.
Create a docker image with python pre-installed. I chose 'python:3.6.5-slim' from docker hub.
Create a docker redis image.
Connect both the images using docker networking.
Run an independent python script that will read the data from dataset and will store following in Redis Data Store.
When user enters search query, we retrieve set of documents from already built inverted index from redis and for all the documents, we calculate TF-IDF and show top 20 results with highest TF-IDF.

Pre-Processing:
Remove Stop Words: 

Often the document text contains lot of common words like 'the', 'and'.. We don't want to process these words and store any information about these in our database. So, first step would be to remove all stop words like these from the dataset.
2. Perform SnowballStemming: 
Stemming is a process of mapping similar set of words in to single word. Here, we chose Snow ball stemming algorithm because it will map all words originated from same word to its root word.Meaning, 'winning','win','wins' will be the same in the context of query search. So, it will map all those words in to just 'win'. So, by performing stemming, we can vastly reduce the number of words before we can do further processing with the words.
3. Build Inverted Index: 
Inverted Index is built for all the documents where term is a key which contains a value of :
{documentID where term is present: frequency of word in the document}. Inverted Index is used to efficiently calculate TF and IDF of every term in document.
4. TF-IDF:
TF-IDF stands for Term Frequency and Inverse Document frequency. It is a ranking mechanism applied to search engine mostly. It takes each unique words as terms in the document. TF-IDF is a metric that represents how 'important' a word is to a document in the document set. Each TF-IDF vector determines how important a given word is to that document. There are two steps involved here:
a) Calculate Term Frequency(TF): Term frequency is the number of times a given term or query apears within a search index
b) Calculate Inverse Document Frequency(IDF): This will have all the documents and the number of times it appeared in the document for a given term.
IDF = Log((Total number of Documents) / Number of documents the word is present)
5. Store pre-processed data in Redis:
Store the data in Redis in below format:
{term1: {doc1: TF*IDF, doc2: TF*IDF,……}, term2: {doc2:TF*IDF,doc3:TF*IDF}….}
The reason we stored in this format is: when user enters search query, we need to get relevant documents for those terms and storing in this way, the retrieval access is O(1) for each term.
6. Store Document Info to display
Store book_title and book_description for all the documents in Redis. As we are calculating cosine similarity and returning top 20 elements, we need relevant document information like title, description to be stored so we can access quickly and retrieve the results.
{Document1 : {title:"Example Title" , description:"Example Description"} }
Search Query Entered by User:
Divide into query tokens: We need to go through the same process of removing stop words, do snow ball stemming for the query tokens.
Retrieve the values for these tokens from Redis: Since we already stored pre-processed data in Redis as in step 5 above, we retrieve those values.
Form a document set: From the retrieved results, form a unique set of documents in which query tokens are present.
Sum all TF-IDF values: Now, we just sum all the TF-IDF values for these documents and display top 20 with highest TF-IDF values.

References:
https://www.youtube.com/watch?v=3HuYr6G2Z28&t=1146s
https://medium.com/@schogini/two-docker-container-communication-using-python-and-redis-a-tiny-demonstration-b9d7cd35daab
Challenges:
Initially I tried to set up Amazon EC2 instance and Redis instance in AWS. I started working locally in python3 and when I deployed my code in ec2 instance, I am unable to start the apache server in flask because of python version mismatch.

Overcome: Rather than installing everything in EC2 instance, I created two docker images. One with Python3 and other one as Redis Service. By building these docker images, it has greatly reduced all dependency issues.
2. Initially I stored both inverted index and weighted vector in Redis. So, for a given query, retrieving all the documents from Redis is very slow since these terms might associate with 100 or 1000's of documents. 
Overcome: So, changed the data store design to store achieve low latency like below:
{term1: {doc1: TF*IDF, doc2: TF*IDF,……}, term2: {doc2:TF*IDF,doc3:TF*IDF}….}
By using this design, you will retrieve only the query token keys from Redis.
3. Initially I calculated cosine similarity with the above Data store design and it took about 6–10s to retrieve the results. 
Overcome: After using the above data store design, I am able to get results in a second.
Contributions:
I used the reference example(http://www.site.uottawa.ca/~diana/csi4107/cosine_tf_idf_example.pdf) and textbook example and built the code from the scratch.
Since the query results needs to have low latency, I decided to use redis in-memory database for quick key access.
Since, I need to return top 20 results from thousands of documents, I am using a dict with fixed size 20 and doing min heapify while storing the documents.
