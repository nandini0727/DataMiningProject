from flask import Flask, request, render_template
import TFTDF
import json
import re
from collections import OrderedDict
import ImageTFIDF
import os
import subprocess
import json
import naivebayeslog




app = Flask(__name__)
UPLOAD_FOLDER = '/Users/nandinikorrapolu/Desktop/DataMiningProject/FinalDataMiningProject/Imagesearch'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def my_form():
    return render_template('index1.html')

@app.route('/', methods=['POST'])
def my_form_post():
    # text = request.form['text']
    # text1 = request.form['text1']
    # text2 = request.form['text2']
   
    sim = OrderedDict()

    if 'text' in request.form:
        text = request.form['text']
        sim = TFTDF.calculateTFIDFSUM(text)

        if len(sim) == 0:
            noval = "OOPS!!! no results found for your search query"
            return noval

    

        for key in sim:
            finalstr=""
            strng=""
            strng = '''<p><strong>{}</strong></p><p>{}</p><br>'''.format(sim[key]['title'],sim[key]['description'])
            finalstr = " ".join((finalstr, strng))

        
            l = TFTDF.getQueryTokens(text)

            word = ' '.join(l)
            terms = re.sub('\s+', '|', word)


            regex = re.compile(r'(\s*)((?:\b\s*(?:%s)\b)+)' % terms, re.I)

        
            
            
            sim[key]['description']= regex.sub("<mark>\g<0></mark>", finalstr)
        
        return render_template('searchresult.html', name=sim)

    if 'text2' in request.form:
        text = request.form['text2']
        sim = ImageTFIDF.calculateTFIDFSUM(text)

        if len(sim) == 0:
            noval = "OOPS!!! no results found for your search query"
            return noval

        

    

        for key in sim:
            finalstr=""
            strng=""
            strng = '''<p><strong>Actual Caption:{}</strong></p><p>Google Collab Caption:{}</p><br>'''.format(sim[key]['actual'],sim[key]['collab'])
            finalstr = " ".join((finalstr, strng))

        
            l = ImageTFIDF.getQueryTokens(text)

            word = ' '.join(l)
            terms = re.sub('\s+', '|', word)


            regex = re.compile(r'(\s*)((?:\b\s*(?:%s)\b)+)' % terms, re.I)

        
            
            
            sim[key]['actual']= regex.sub("<mark>\g<0></mark>", finalstr)
        sim['Que'] = text
        return render_template('imagesearch.html', name=sim)


    if 'text1' in request.form:  
        text = request.form['text1'] 
        sim = naivebayeslog.classifier(text)

        finalstr=""
   
        return render_template('classifierresult.html', name=sim)




    
    if 'sub3' in request.form:
        # check if the post request has the file part
        
        file = request.files['pimage']
       
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        url = UPLOAD_FOLDER + "/" + file.filename
        
 
        bash_com = 'curl -F "image=@' + url + '"' + ' -X POST http://127.0.0.1:5000/model/predict'
        subprocess.Popen(bash_com, shell=True)
        output = subprocess.check_output(['bash','-c', bash_com])
        data = json.loads(output)
       

        sim = ImageTFIDF.calculateTFIDFSUM(data['predictions'][0]['caption'])

        if len(sim) == 0:
            noval = "OOPS!!! no results found for your search query"
            return noval

        

        for key in sim:
            finalstr=""
            strng=""
            strng = '''<p><strong>Actual Caption:{}</strong></p><p>Google Collab Caption:{}</p><br>'''.format(sim[key]['actual'],sim[key]['collab'])
            finalstr = " ".join((finalstr, strng))

        
            l = ImageTFIDF.getQueryTokens(data['predictions'][0]['caption'])

            word = ' '.join(l)
            terms = re.sub('\s+', '|', word)


            regex = re.compile(r'(\s*)((?:\b\s*(?:%s)\b)+)' % terms, re.I)

        
            
            
            sim[key]['actual']= regex.sub("<mark>\g<0></mark>", finalstr)
        sim['Que'] = data['predictions'][0]['caption']
        return render_template('imagesearch.html', name=sim)

   
   
    
if __name__ == '__main__': 
   app.run(host='0.0.0.0',port='80')