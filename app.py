from typing import List, Any

from flask import Flask, jsonify, request
from flasgger import Swagger
from flasgger.utils import swag_from
from flask_cors import CORS
from Time_Matters_MultipleDocs import Time_Matters_MultipleDocs
from Time_Matters_SingleDoc import Time_Matters_SingleDoc
from zipfile import ZipFile
import os
import glob

def main():
    """The main function for this script."""
    app.run(host='127.0.0.1',port=443, debug=True)
    CORS(app)


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

app.config['SWAGGER'] = {
  "title": "Time-Matters-API",
  "headers": [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS"),
        ('Access-Control-Allow-Credentials', "false"),
  ],
  "info": {
    "title": "Time-Matters",
    "description": "Date extractor that scores the relevance of temporal expressions found within a text (single document) or a set of texts (multiple documents).",
    "contact": {
      "responsibleOrganization": "ME",
      "responsibleDeveloper": "Me",
      "email": "me@me.com",
      "url": "www.me.com",
    },
    "termsOfService": "http://me.com/terms",
    "version": "0.0.1"
  },
  "schemes": [
    "https",
    "http"
  ]
}


Swagger(app)
@app.route('/SingleDoc/api/v1.0/BySentence', methods=['GET'])
@swag_from('single_doc.yml')
def single_doc_bySentence():
    text = str(request.args.get('text'))
    temporal_tagger_name = str(request.args.get('temporal_tagger_name')).lower()
    date_granularity = str(request.args.get('date_granularity')).lower()
    language = str(request.args.get('language')).lower()
    document_type = str(request.args.get('document_type')).lower()
    document_creation_time = str(request.args.get('document_creation_time')).lower()
    ngram = request.args.get('ngram')
    num_of_keywords = request.args.get('num_of_keywords')
    n_contextual_window = request.args.get('n_contextual_window')
    N = request.args.get('N')
    TH = request.args.get('TH')

    list_field_default = [(date_granularity, 'full'), (language, 'English'), (document_type, 'news'),
                          (document_creation_time, 'yyyy-mm-dd'), (ngram, 1), (num_of_keywords, 10),
                          (n_contextual_window, 'full_sentence'), (N, 'max'), (TH, 0.05)]

    date_granularity, language, document_type, document_creation_time, \
    ngram, num_of_keywords, \
    n_contextual_window, N, TH = get_default(list_field_default)

    heroku_set_permissions()
    if temporal_tagger_name == 'py_heideltime':
        result = Time_Matters_SingleDoc(text, time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH], temporal_tagger=[temporal_tagger_name, language, date_granularity, document_type, document_creation_time], debug_mode=False, score_type='ByDoc')
    else:
        result = Time_Matters_SingleDoc(text, time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH], temporal_tagger=[temporal_tagger_name, date_granularity], debug_mode=False, score_type='BySentence')
    return jsonify({'Score': result[0], 'TempExpressions': result[1], 'RelevantKWs': result[2], 'TextNormalized': result[3], 'TextTokens': result[4], 'SentencesNormalized': result[5], 'SentencesTokens': result[6]})


@app.route('/SingleDoc/api/v1.0/ByDoc', methods=['GET'])
@swag_from('single_doc.yml')
def single_doc_bydoc():
    text = str(request.args.get('text'))
    temporal_tagger_name = str(request.args.get('temporal_tagger_name')).lower()
    date_granularity = str(request.args.get('date_granularity')).lower()
    language = str(request.args.get('language')).lower()
    document_type = str(request.args.get('document_type')).lower()
    document_creation_time = str(request.args.get('document_creation_time')).lower()
    ngram = request.args.get('ngram')
    num_of_keywords = request.args.get('num_of_keywords')
    n_contextual_window = request.args.get('n_contextual_window')
    N = request.args.get('N')
    TH = request.args.get('TH')


    list_field_default = [(date_granularity, 'full'), (language, 'English'), (document_type, 'news'),
                          (document_creation_time, 'yyyy-mm-dd'), (ngram, 1), (num_of_keywords, 10),
                          (n_contextual_window, 'full_sentence'), (N, 'max'), (TH, 0.05)]

    date_granularity, language, document_type, document_creation_time, \
    ngram, num_of_keywords, \
    n_contextual_window, N, TH = get_default(list_field_default)
    heroku_set_permissions()
    if temporal_tagger_name == 'py_heideltime':
        result = Time_Matters_SingleDoc(text, time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH],
                                        temporal_tagger=[temporal_tagger_name, language, date_granularity, document_type, document_creation_time], debug_mode=False, score_type='ByDoc')
    else:
        result = Time_Matters_SingleDoc(text, time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH], temporal_tagger=[temporal_tagger_name, date_granularity], debug_mode=False, score_type='ByDoc')
    return jsonify({'Score': result[0], 'TempExpressions': result[1], 'RelevantKWs': result[2], 'TextNormalized': result[3], 'TextTokens': result[4], 'SentencesNormalized': result[5], 'SentencesTokens': result[6]})


# ============================================================
# multidoc
@app.route('/MultipleDocs/api/v1.0/ByCorpus', methods=['POST'])
@swag_from('ByCorpus_MD.yml')
def multidoc_bycorpus():
    iFile = request.files.getlist('zip_file')[0]
    docs = get_docs(iFile)

    temporal_tagger_name = str(request.args.get('temporal_tagger_name')).lower()
    date_granularity = str(request.args.get('date_granularity')).lower()
    language = str(request.args.get('language')).lower()
    document_type = str(request.args.get('document_type')).lower()
    document_creation_time = str(request.args.get('document_creation_time')).lower()
    ngram = request.args.get('ngram')
    num_of_keywords = request.args.get('num_of_keywords')
    N = request.args.get('N')
    TH = request.args.get('TH')

    list_field_default = [(date_granularity, 'full'), (language, 'English'), (document_type, 'news'),
                          (document_creation_time, 'yyyy-mm-dd'), (ngram, 1), (num_of_keywords, 10),
                          ('full_document', 'full_document'), (N, 'max'), (TH, 0.05)]

    date_granularity, language, document_type, document_creation_time, \
    ngram, num_of_keywords, \
    n_contextual_window, N, TH = get_default(list_field_default)
    heroku_set_permissions()
    if temporal_tagger_name == 'py_heideltime':
        result = Time_Matters_MultipleDocs(docs, time_matters=[ngram, num_of_keywords, 'full_document', N, TH],
                                        temporal_tagger=[temporal_tagger_name, language, date_granularity, document_type, document_creation_time], debug_mode=False, score_type='ByCorpus')
    else:
        result = Time_Matters_MultipleDocs(docs, time_matters=[ngram, num_of_keywords, 'full_document', N, TH], temporal_tagger=[temporal_tagger_name, date_granularity], debug_mode=False, score_type='ByCorpus')

    remove_files()
    return jsonify({'Score': result[0], 'TempExpressions': result[1], 'RelevantKWs': result[2], 'TextNormalized': result[3], 'TextTokens': result[4], 'SentencesNormalized': result[5], 'SentencesTokens': result[6]})

@app.route('/MultipleDocs/api/v1.0/ByDoc', methods=['POST'])
@swag_from('ByDocSentence_MD.yml')
def multidoc_byDoc():
    iFile = request.files.getlist('zip_file')[0]
    docs = get_docs(iFile)

    temporal_tagger_name = str(request.args.get('temporal_tagger_name')).lower()
    date_granularity = str(request.args.get('date_granularity')).lower()
    language = str(request.args.get('language')).lower()
    document_type = str(request.args.get('document_type')).lower()
    document_creation_time = str(request.args.get('document_creation_time')).lower()
    ngram = request.args.get('ngram')
    num_of_keywords = request.args.get('num_of_keywords')
    n_contextual_window = request.args.get('n_contextual_window')
    N = request.args.get('N')
    TH = request.args.get('TH')

    list_field_default = [(date_granularity, 'full'), (language, 'English'), (document_type, 'news'),
                          (document_creation_time, 'yyyy-mm-dd'), (ngram, 1), (num_of_keywords, 10),
                          (n_contextual_window, 'full_sentence'), (N, 'max'), (TH, 0.05)]

    date_granularity, language, document_type, document_creation_time, \
    ngram, num_of_keywords, \
    n_contextual_window, N, TH = get_default(list_field_default)
    heroku_set_permissions()
    if temporal_tagger_name == 'py_heideltime':
        result = Time_Matters_MultipleDocs(docs, time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH],
                                        temporal_tagger=[temporal_tagger_name, language, date_granularity, document_type, document_creation_time], debug_mode=False, score_type='ByDoc')
    else:
        result = Time_Matters_MultipleDocs(docs, time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH], temporal_tagger=[temporal_tagger_name, date_granularity], debug_mode=False, score_type='ByDoc')

    remove_files()
    return jsonify({'Score': result[0], 'TempExpressions': result[1], 'RelevantKWs': result[2], 'TextNormalized': result[3], 'TextTokens': result[4], 'SentencesNormalized': result[5], 'SentencesTokens': result[6]})


@app.route('/MultipleDocs/api/v1.0/ByDocSentence', methods=['POST'])
@swag_from('ByDocSentence_MD.yml')
def single_multidoc_byDocSentence():
    iFile = request.files.getlist('zip_file')[0]
    docs = get_docs(iFile)

    temporal_tagger_name = str(request.args.get('temporal_tagger_name')).lower()
    date_granularity = str(request.args.get('date_granularity')).lower()
    language = str(request.args.get('language')).lower()
    document_type = str(request.args.get('document_type')).lower()
    document_creation_time = str(request.args.get('document_creation_time')).lower()
    ngram = request.args.get('ngram')
    num_of_keywords = request.args.get('num_of_keywords')
    n_contextual_window = request.args.get('n_contextual_window')
    N = request.args.get('N')
    TH = request.args.get('TH')

    list_field_default = [(date_granularity, 'full'), (language, 'English'), (document_type, 'news'),
                          (document_creation_time, 'yyyy-mm-dd'), (ngram, 1), (num_of_keywords, 10),
                          (n_contextual_window, 'full_sentence'), (N, 'max'), (TH, 0.05)]

    date_granularity, language, document_type, document_creation_time, \
    ngram, num_of_keywords, \
    n_contextual_window, N, TH = get_default(list_field_default)
    heroku_set_permissions()
    if temporal_tagger_name == 'py_heideltime':
        result = Time_Matters_MultipleDocs(docs, time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH],
                                        temporal_tagger=[temporal_tagger_name, language, date_granularity, document_type, document_creation_time], debug_mode=False, score_type='ByDocSentence')
    else:
        result = Time_Matters_MultipleDocs(docs, time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH], temporal_tagger=[temporal_tagger_name, date_granularity], debug_mode=False, score_type='ByDocSentence')

    remove_files()
    return jsonify({'Score': result[0], 'TempExpressions': result[1], 'RelevantKWs': result[2], 'TextNormalized': result[3], 'TextTokens': result[4], 'SentencesNormalized': result[5], 'SentencesTokens': result[6]})


def get_docs(uploaded_file):
    import codecs
    # Create a ZipFile Object and load sample.zip in it
    with ZipFile(uploaded_file, 'r') as zipObj:
        # Extract all the contents of zip file in current directory
        zipObj.extractall('upload_files')
    docs = []
    files = [f for f in glob.glob('upload_files/'+'*.txt', recursive=True)]
    for file in files:
        with open(file, encoding="utf8", errors='ignore') as text_file:
            contents = text_file.read()
        docs.append(contents)
    return docs


def remove_files():
    filelist = glob.glob(os.path.join('upload_files', "*.*"))
    for f in filelist:
        os.remove(f)


def heroku_set_permissions(heroku=True):
    import imp
    import os
    if heroku:
        path = imp.find_module('py_heideltime')[1]
        full_path = path + "/Heideltime/TreeTaggerLinux/bin/*"
        command = 'chmod 111 ' + full_path
        result_comand = os.popen(command).read()

def is_int(s):
    if s != None:
        try:
            int(s)
            return int(s)
        except ValueError:
            return s
    else:
        s=''
        return s

def is_float(s):
    if s != None:
        try:
            float(s)
            return float(s)
        except ValueError:
            return s
    else:
        return s


def get_default(list_field_default):
    values= []
    for x in list_field_default:
        if x[0] == 'none' or x[0] == None:
            values.append(x[1])
        else:
            values.append(x[0])
    ngram = is_int(values[4])
    num_of_keywords = is_int(values[5])
    n_contextual_window = is_int(values[6])
    TH = is_float(values[8])
    N = is_int(values[7])
    return values[0], values[1], values[2], values[3], ngram, num_of_keywords, n_contextual_window, N, TH


def str2bool(v):
    return v in ("True")


if __name__== '__main__':
  main()