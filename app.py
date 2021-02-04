from flask import Flask, render_template, request, redirect, flash, send_from_directory
from flask_bootstrap import Bootstrap
import os
from werkzeug.utils import secure_filename
import pandas as pd
from collections import defaultdict
from nl4dv import NL4DV
import json
from os.path import join, dirname, realpath
from pathlib import Path
import subprocess
import en_core_web_sm

MAX_FILE_SIZE_MB = 1000
ALLOWED_EXTENSIONS = set(['txt', 'csv', 'xlsx'])

app = Flask(__name__)

UPLOAD_FOLDER = Path("static/uploads/")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024

nl4dv_instance = None
query = None

def allowed_file(filename):

	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def trainModel():
    global nl4dv_instance
    global query    


    if request.method == 'POST' and 'file' in request.files and request.files['file']:
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_filename)
            print('File upload success!')
            dependency_parser_config = {"name": "spacy", "model": "en_core_web_sm", "parser": None}
            nl4dv_instance = NL4DV(dependency_parser_config=dependency_parser_config, verbose=True)
            nl4dv_instance = NL4DV(data_url=os.path.join(app.config['UPLOAD_FOLDER'], filename))
            query = request.form.get("query")
            
    return render_template('main_page.html') 
    
    

@app.route('/analyze_query', methods=['GET', 'POST'])
def analyze_query():
    global nl4dv_instance
    global query
    print(query)
    return json.dumps(nl4dv_instance.analyze_query(query, debug=True))





if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8088, debug=True)
    subprocess.call("python -m spacy download en_core_web_sm",shell=True)
