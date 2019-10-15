from flask import Flask, request, render_template
import TFTDF
import json
import re



app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('index1.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    sim = TFTDF.calculateTFIDFSUM(text)

    if len(sim) == 0:
        noval = "OOPS!!! no results found for your search query"
        return noval

    print(sim)

    finalstr=""
    for key in sim:
        strng=""
        strng = '''<p><strong>{}</strong></p><p>{}</p><p>TF-IDF score:{}</p><br><br>'''.format(sim[key]['title'],sim[key]['description'],sim[key]['tfidf'])
        finalstr = " ".join((finalstr, strng))
    
    l = TFTDF.getQueryTokens(text)
   
    print(l)
    
    
    word = ' '.join(l)
    terms = re.sub('\s+', '|', word)
    regex = re.compile(r'(\s*)((?:\b\s*(?:%s)\b)+)' % terms, re.I)
    
    
    return regex.sub("<mark>\g<0></mark>", finalstr)
   
   
    
if __name__ == '__main__': 
   app.run()