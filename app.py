import io
from flaskext.markdown import Markdown
from flask import Flask, url_for, render_template, flash, request, redirect, session, send_file, send_from_directory
import re
import os
import uuid
import spacy
from spacy import displacy
import json
import glob
import datetime
import sqlite3
from spacy.pipeline import EntityRuler
from spacy.language import Language
import PyPDF2
import docx2txt
from spacy.pipeline import EntityRecognizer
from shutil import copyfile



HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem">{}</div>"""

app = Flask(__name__)
Markdown(app)
app.secret_key = os.urandom(24)
UPLOAD_FOLDER = 'Uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


nlp = spacy.load("model-best-medicalner")
nlp_class = spacy.load("model-best-class")
# nlp.max_length = 4000000
upload_file = ""


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/textpage')
def textpage():
    return render_template('text_page.html')

@app.route('/extract', methods=["GET", "POST"])
def extract():
    if request.method == 'POST':
        raw_text = request.form['rawtext']

        if raw_text != "":
            raw_text = raw_text.capitalize()
            raw_text = cleanChars(raw_text)
            class_text = raw_text.lower()

            colors = {"drug": "#0C95F7", "disease": "#D2EB50", "actual_disease": "#AEFF8A", "dosage": "#C0C3B1", "symptom": "#FC8F7D", "treatment": "#2EEAFE",
                      "diagnostic_test": "#CCE9AD", "medical_test": "#4D86E9", "sex": "#8DC382", "habit": "#FEA5D7", "medical_disorder": "#AEFF9B"}
            options = {"colors": colors}

            docx = nlp(raw_text)
            html = displacy.render(docx, style="ent", options=options)
            html = html.replace("\n\n", "\n")
            result = HTML_WRAPPER.format(html)
            custom_namedentities = [(entity.text, entity.label_)
                                    for entity in docx.ents]
            uniqueres = list(set((entity.label_)for entity in docx.ents))
            uniqueent = list(set((entity.text, entity.label_)
                             for entity in docx.ents))

            label = classification_model(class_text)
        else:
            raw_text = "There is no text to analyze"

    return render_template('predict.html', rawtext=raw_text, result=result, uniqueent=uniqueent, custom_namedentities=custom_namedentities, uniqueres=uniqueres, classes=label)


def classification_model(raw_text):
    process_text = raw_text.lower()
    class_model = nlp_class(process_text)
    results = class_model.cats
    Keymax = max(zip(results.values(), results.keys()))[1]
    label = Keymax
    return label

def capitalize_text(text):
    txt = re.sub(r'ADTX', '', text)
    txt = re.sub(r'DISC', '', text)
    return '. '.join(i.capitalize() for i in txt.split('.'))


def cleanChars(txt):
    txt = re.sub(r'#', '', txt)
    txt = re.sub(r'"', '', txt)
    txt = re.sub(r'\t', '', txt)
    txt = re.sub(r':', '', txt)
    txt = re.sub(r'\n', '', txt)
    txt = re.sub(r'//', ' ', txt)
    txt = re.sub("[+]", "", txt)

    return txt


# Function to convert
def listToString(s):

    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        str1 += ele

    # return string
    return str1

if __name__ == "__main__":
   # create_tables()
    app.run(debug=True, host="localhost", port=8080)
