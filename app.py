from flask import Flask, jsonify, request
from flasgger import Swagger
from flasgger.utils import swag_from
from flask_cors import CORS
from Time_Matters_SingleDoc import Time_Matters_SingleDoc
from Time_Matters_MultipleDocs import Time_Matters_MultipleDocs
import json
from zipfile import ZipFile
import os
import glob


def main():
    """The main function for this script."""
    app.run(host='0.0.0.0', port='443', debug=True)
    CORS(app)


app = Flask(__name__)
SCRIPT_NAME = "/timematters"
app.config['JSON_SORT_KEYS'] = False

app.config['SWAGGER'] = {
    "title": "Time Matters! API",
    "headers": [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS"),
        ('Access-Control-Allow-Credentials', "false"),
    ],
    "info": {
        "title": "Time Matters API",
        "description": "Welcome to Time Matters! API webpage. Here you can try Time Matters directly calling our HTTP API. Alternatively you can play with our python package at https://github.com/LIAAD/Time-Matters",
        "contact": {
            "responsibleOrganization": "INESC TEC",
            "responsibleDeveloper": "Ricardo Campos",
            "email": "ricardo.campos@ipt.pt",
            "url": "http://www.ccc.ipt.pt/~ricardo/",
        },
        "termsOfService": "https://github.com/LIAAD/Time-Matters",
        "version": "0.0.1"
    },
    "schemes": [
        "http",
        "https"
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    #"basePath": SCRIPT_NAME,
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

Swagger(app)


def handle_time_matters(typeOfAnalysis, text, score_type, ngram, num_of_keywords, n_contextual_window, N, TH,
                        temporal_tagger_name, date_granularity, begin_date=None, end_date=None, language=None,
                        document_type=None, document_creation_time=None):
    if temporal_tagger_name == "rule_based":
        if typeOfAnalysis == "SingleDoc":
            result = Time_Matters_SingleDoc(text, score_type=score_type,
                                            time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH],
                                            temporal_tagger=[temporal_tagger_name, date_granularity, begin_date,
                                                             end_date])
        elif typeOfAnalysis == "MultiDocs":
            result = Time_Matters_MultipleDocs(text, score_type=score_type,
                                               time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH],
                                               temporal_tagger=[temporal_tagger_name, date_granularity, begin_date,
                                                                end_date])
    elif temporal_tagger_name == "py_heideltime":
        if typeOfAnalysis == "SingleDoc":
            if document_creation_time:
                result = Time_Matters_SingleDoc(text, score_type=score_type,
                                                time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH],
                                                temporal_tagger=[temporal_tagger_name, language, date_granularity,
                                                                 document_type, document_creation_time])
            else:
                result = Time_Matters_SingleDoc(text, score_type=score_type,
                                                time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH],
                                                temporal_tagger=[temporal_tagger_name, language, date_granularity,
                                                                 document_type])
        elif typeOfAnalysis == "MultiDocs":
            if document_creation_time:
                result = Time_Matters_MultipleDocs(text, score_type=score_type,
                                                   time_matters=[ngram, num_of_keywords, n_contextual_window, N, TH],
                                                   temporal_tagger=[temporal_tagger_name, language, date_granularity,
                                                                    document_type, document_creation_time])
            else:
                result = Time_Matters_MultipleDocs(text, score_type='ByDoc',
                                                   temporal_tagger=['py_heideltime', 'English', 'year', 'news',
                                                                    '2013-04-15'])

    model = {
        'Score': result[0],
        'TempExpressions': result[1],
        'RelevantKWs': result[2],
        'TextNormalized': result[3],
        'TextTokens': result[4],
        'SentencesNormalized': result[5],
        'SentencesTokens': result[6]
    }

    return model


# SINGLE DOC

# -------------HEIDELTIME

@app.route("/SingleDoc/Heideltime/api/v1.0/ScoreByDoc", methods=['POST'])
@swag_from('SingleDoc_Heideltime_ScoreByDoc_post.yml')
def SingleDoc_Heideltime_ScoreByDoc_post():
    try:
        typeOfAnalysis = "SingleDoc"
        data = request.form
        text = data['text']
        score_type = 'ByDoc'
        ngram = int(data.get('ngram', 1))
        num_of_keywords = int(data.get('num_of_keywords', 10))
        n_contextual_window = data.get('n_contextual_window', 'full_sentence')
        if n_contextual_window.isdigit():
            n_contextual_window = int(n_contextual_window)
        N = data.get('N', 'max')
        if N.isdigit():
            N = int(N)
        TH = float(data.get('TH', 0.05))
        temporal_tagger_name = "py_heideltime"
        date_granularity = data.get('date_granularity', 'full').lower()
        language = data.get('language', 'English')
        document_type = data.get('document_type', 'news')
        document_creation_time = data.get('document_creation_time')
        result_model = handle_time_matters(typeOfAnalysis, text, score_type, ngram, num_of_keywords,
                                           n_contextual_window, N, TH, temporal_tagger_name, date_granularity,
                                           begin_date=None, end_date=None, language=language,
                                           document_type=document_type, document_creation_time=document_creation_time)
        return jsonify(result_model)
    except Exception as e:
        return jsonify({'message': str(e)})


@app.route("/SingleDoc/Heideltime/api/v1.0/ScoreBySentence", methods=['POST'])
@swag_from('SingleDoc_Heideltime_ScoreBySentence_post.yml')
def SingleDoc_Heideltime_ScoreBySentence_post():
    try:
        typeOfAnalysis = "SingleDoc"
        data = request.form
        text = data['text']
        score_type = 'BySentence'
        ngram = int(data.get('ngram', 1))
        num_of_keywords = int(data.get('num_of_keywords', 10))
        n_contextual_window = data.get('n_contextual_window', 'full_sentence')
        if n_contextual_window.isdigit():
            n_contextual_window = int(n_contextual_window)
        N = data.get('N', 'max')
        if N.isdigit():
            N = int(N)
        TH = float(data.get('TH', 0.05))
        temporal_tagger_name = "py_heideltime"
        date_granularity = data.get('date_granularity', 'full').lower()
        language = data.get('language', 'English')
        document_type = data.get('document_type', 'news')
        document_creation_time = data.get('document_creation_time')
        result_model = handle_time_matters(typeOfAnalysis, text, score_type, ngram, num_of_keywords,
                                           n_contextual_window, N, TH, temporal_tagger_name, date_granularity,
                                           begin_date=None, end_date=None, language=language,
                                           document_type=document_type, document_creation_time=document_creation_time)
        return jsonify(result_model)
    except Exception as e:
        return jsonify({'message': str(e)})


# -------------RULE BASED
@app.route("/SingleDoc/RuleBased/api/v1.0/ScoreByDoc", methods=['POST'])
@swag_from('SingleDoc_RuleBased_ScoreByDoc_post.yml')
def SingleDoc_RuleBased_ScoreByDoc_post():
    try:
        typeOfAnalysis = "SingleDoc"
        data = request.form
        text = data['text']
        score_type = 'ByDoc'
        ngram = int(data.get('ngram', 1))
        num_of_keywords = int(data.get('num_of_keywords', 10))
        n_contextual_window = data.get('n_contextual_window', 'full_sentence')
        if n_contextual_window.isdigit():
            n_contextual_window = int(n_contextual_window)
        N = data.get('N', 'max')
        if N.isdigit():
            N = int(N)
        TH = float(data.get('TH', 0.05))
        temporal_tagger_name = "rule_based"
        date_granularity = data.get('date_granularity', 'full').lower()
        begin_date = int(data.get('begin_date', 0))
        end_date = int(data.get('end_date', 2100))
        result_model = handle_time_matters(typeOfAnalysis, text, score_type, ngram, num_of_keywords,
                                           n_contextual_window, N, TH, temporal_tagger_name, date_granularity,
                                           begin_date, end_date)
        return jsonify(result_model)
    except Exception as e:
        return jsonify({'message': str(e)})


@app.route("/SingleDoc/RuleBased/api/v1.0/ScoreBySentence", methods=['POST'])
@swag_from('SingleDoc_RuleBased_ScoreBySentence_post.yml')
def SingleDoc_RuleBased_ScoreBySentence_post():
    try:
        typeOfAnalysis = "SingleDoc"
        data = request.form
        text = data['text']
        score_type = 'BySentence'
        ngram = int(data.get('ngram', 1))
        num_of_keywords = int(data.get('num_of_keywords', 10))
        n_contextual_window = data.get('n_contextual_window', 'full_sentence')
        if n_contextual_window.isdigit():
            n_contextual_window = int(n_contextual_window)
        N = data.get('N', 'max')
        if N.isdigit():
            N = int(N)
        TH = float(data.get('TH', 0.05))
        temporal_tagger_name = "rule_based"
        date_granularity = data.get('date_granularity', 'full').lower()
        begin_date = int(data.get('begin_date', 0))
        end_date = int(data.get('end_date', 2100))
        result_model = handle_time_matters(typeOfAnalysis, text, score_type, ngram, num_of_keywords,
                                           n_contextual_window, N, TH, temporal_tagger_name, date_granularity,
                                           begin_date, end_date)
        return jsonify(result_model)
    except Exception as e:
        return jsonify({'message': str(e)})


# Multi DOCs

# -------------HEIDELTIME
@app.route("/MultiDocs/Heideltime/api/v1.0/ScoreByCorpus", methods=['POST'])
@swag_from('MultiDocs_Heideltime_ScoreByCorpus_post.yml')
def MultiDocs_Heideltime_ScoreByCorpus_post():
    try:
        typeOfAnalysis = "MultiDocs"
        data = request.form
        typeOfInput = str(data.get('typeOfInput', 'zip'))
        if typeOfInput == 'zip':
            iFile = request.files.getlist('text')[0]
            ListOfDocs = get_docs(iFile)
        else:
            text = data['text']
            ListOfDocs = json.loads(text)

        score_type = 'ByCorpus'
        ngram = int(data.get('ngram', 1))
        num_of_keywords = int(data.get('num_of_keywords', 10))
        n_contextual_window = data.get('n_contextual_window', 'full_document')
        if n_contextual_window.isdigit():
            n_contextual_window = int(n_contextual_window)
        N = data.get('N', 10)
        if N == 'max':
            N = str(N)
        else:
            N = int(N)
        TH = float(data.get('TH', 0.05))
        temporal_tagger_name = "py_heideltime"
        date_granularity = data.get('date_granularity', 'full').lower()
        language = data.get('language', 'English')
        document_type = data.get('document_type', 'news')
        document_creation_time = data.get('document_creation_time')
        result_model = handle_time_matters(typeOfAnalysis, ListOfDocs, score_type, ngram, num_of_keywords,
                                           n_contextual_window, N, TH, temporal_tagger_name, date_granularity,
                                           begin_date=None, end_date=None, language=language,
                                           document_type=document_type, document_creation_time=document_creation_time)
        return jsonify(result_model)
    except Exception as e:
        return jsonify({'message': str(e)})


@app.route("/MultiDocs/Heideltime/api/v1.0/ScoreByDoc", methods=['POST'])
@swag_from('MultiDocs_Heideltime_ScoreByDoc_post.yml')
def MultiDocs_Heideltime_ScoreByDoc_post():
    try:
        typeOfAnalysis = "MultiDocs"
        data = request.form
        typeOfInput = str(data.get('typeOfInput', 'zip'))
        if typeOfInput == 'zip':
            iFile = request.files.getlist('text')[0]
            ListOfDocs = get_docs(iFile)
        else:
            text = data['text']
            ListOfDocs = json.loads(text)

        score_type = 'ByDoc'
        ngram = int(data.get('ngram', 1))
        num_of_keywords = int(data.get('num_of_keywords', 10))
        n_contextual_window = data.get('n_contextual_window', 'full_sentence')
        if n_contextual_window.isdigit():
            n_contextual_window = int(n_contextual_window)
        N = data.get('N', 10)
        if N == 'max':
            N = str(N)
        else:
            N = int(N)
        TH = float(data.get('TH', 0.05))
        temporal_tagger_name = "py_heideltime"
        date_granularity = data.get('date_granularity', 'full').lower()
        language = data.get('language', 'English')
        document_type = data.get('document_type', 'news')
        document_creation_time = data.get('document_creation_time')
        result_model = handle_time_matters(typeOfAnalysis, ListOfDocs, score_type, ngram, num_of_keywords,
                                           n_contextual_window, N, TH, temporal_tagger_name, date_granularity,
                                           begin_date=None, end_date=None, language=language,
                                           document_type=document_type, document_creation_time=document_creation_time)
        return jsonify(result_model)
    except Exception as e:
        return jsonify({'message': str(e)})


@app.route("/MultiDocs/Heideltime/api/v1.0/ScoreByDocSentence", methods=['POST'])
@swag_from('MultiDocs_Heideltime_ScoreByDocSentence_post.yml')
def MultiDocs_Heideltime_ScoreByDocSentence_post():
    try:
        typeOfAnalysis = "MultiDocs"
        data = request.form
        typeOfInput = str(data.get('typeOfInput', 'zip'))
        if typeOfInput == 'zip':
            iFile = request.files.getlist('text')[0]
            ListOfDocs = get_docs(iFile)
        else:
            text = data['text']
            ListOfDocs = json.loads(text)

        score_type = 'ByDocSentence'
        ngram = int(data.get('ngram', 1))
        num_of_keywords = int(data.get('num_of_keywords', 10))
        n_contextual_window = data.get('n_contextual_window', 'full_sentence')
        if n_contextual_window.isdigit():
            n_contextual_window = int(n_contextual_window)
        N = data.get('N', 10)
        if N == 'max':
            N = str(N)
        else:
            N = int(N)
        TH = float(data.get('TH', 0.05))
        temporal_tagger_name = "py_heideltime"
        date_granularity = data.get('date_granularity', 'full').lower()
        language = data.get('language', 'English')
        document_type = data.get('document_type', 'news')
        document_creation_time = data.get('document_creation_time')
        result_model = handle_time_matters(typeOfAnalysis, ListOfDocs, score_type, ngram, num_of_keywords,
                                           n_contextual_window, N, TH, temporal_tagger_name, date_granularity,
                                           begin_date=None, end_date=None, language=language,
                                           document_type=document_type, document_creation_time=document_creation_time)
        return jsonify(result_model)
    except Exception as e:
        return jsonify({'message': str(e)})


# -------------rule-based
@app.route("/MultiDocs/RuleBased/api/v1.0/ScoreByCorpus", methods=['POST'])
@swag_from('MultiDocs_RuleBased_ScoreByCorpus_post.yml')
def MultiDocs_RuleBased_ScoreByCorpus_post():
    try:
        typeOfAnalysis = "MultiDocs"
        data = request.form
        typeOfInput = str(data.get('typeOfInput', 'zip'))
        if typeOfInput == 'zip':
            iFile = request.files.getlist('text')[0]
            ListOfDocs = get_docs(iFile)
        else:
            text = data['text']
            ListOfDocs = json.loads(text)

        score_type = 'ByCorpus'
        ngram = int(data.get('ngram', 1))
        num_of_keywords = int(data.get('num_of_keywords', 10))
        n_contextual_window = data.get('n_contextual_window', 'full_document')
        if n_contextual_window.isdigit():
            n_contextual_window = int(n_contextual_window)
        N = data.get('N', 10)
        if N == 'max':
            N = str(N)
        else:
            N = int(N)
        TH = float(data.get('TH', 0.05))
        temporal_tagger_name = "rule_based"
        date_granularity = data.get('date_granularity', 'full').lower()
        begin_date = int(data.get('begin_date', 0))
        end_date = int(data.get('end_date', 2100))
        result_model = handle_time_matters(typeOfAnalysis, ListOfDocs, score_type, ngram, num_of_keywords,
                                           n_contextual_window, N, TH, temporal_tagger_name, date_granularity,
                                           begin_date, end_date)
        return jsonify(result_model)
    except Exception as e:
        return jsonify({'message': str(e)})


@app.route("/MultiDocs/RuleBased/api/v1.0/ScoreByDoc", methods=['POST'])
@swag_from('MultiDocs_RuleBased_ScoreByDoc_post.yml')
def MultiDocs_RuleBased_ScoreByDoc_post():
    try:
        typeOfAnalysis = "MultiDocs"
        data = request.form
        typeOfInput = str(data.get('typeOfInput', 'zip'))
        if typeOfInput == 'zip':
            iFile = request.files.getlist('text')[0]
            ListOfDocs = get_docs(iFile)
        else:
            text = data['text']
            ListOfDocs = json.loads(text)

        score_type = 'ByDoc'
        ngram = int(data.get('ngram', 1))
        num_of_keywords = int(data.get('num_of_keywords', 10))
        n_contextual_window = data.get('n_contextual_window', 'full_sentence')
        if n_contextual_window.isdigit():
            n_contextual_window = int(n_contextual_window)
        N = data.get('N', 10)
        if N == 'max':
            N = str(N)
        else:
            N = int(N)
        TH = float(data.get('TH', 0.05))
        temporal_tagger_name = "rule_based"
        date_granularity = data.get('date_granularity', 'full').lower()
        begin_date = int(data.get('begin_date', 0))
        end_date = int(data.get('end_date', 2100))
        result_model = handle_time_matters(typeOfAnalysis, ListOfDocs, score_type, ngram, num_of_keywords,
                                           n_contextual_window, N, TH, temporal_tagger_name, date_granularity,
                                           begin_date, end_date)
        return jsonify(result_model)
    except Exception as e:
        return jsonify({'message': str(e)})


@app.route("/MultiDocs/RuleBased/api/v1.0/ScoreByDocSentence", methods=['POST'])
@swag_from('MultiDocs_RuleBased_ScoreByDocSentence_post.yml')
def MultiDocs_RuleBased_ScoreByDocSentence_post():
    try:
        typeOfAnalysis = "MultiDocs"
        data = request.form
        typeOfInput = str(data.get('typeOfInput', 'zip'))
        if typeOfInput == 'zip':
            iFile = request.files.getlist('text')[0]
            ListOfDocs = get_docs(iFile)
        else:
            text = data['text']
            ListOfDocs = json.loads(text)

        score_type = 'ByDocSentence'
        ngram = int(data.get('ngram', 1))
        num_of_keywords = int(data.get('num_of_keywords', 10))
        n_contextual_window = data.get('n_contextual_window', 'full_sentence')
        if n_contextual_window.isdigit():
            n_contextual_window = int(n_contextual_window)
        N = data.get('N', 10)
        if N == 'max':
            N = str(N)
        else:
            N = int(N)
        TH = float(data.get('TH', 0.05))
        temporal_tagger_name = "rule_based"
        date_granularity = data.get('date_granularity', 'full').lower()
        begin_date = int(data.get('begin_date', 0))
        end_date = int(data.get('end_date', 2100))
        result_model = handle_time_matters(typeOfAnalysis, ListOfDocs, score_type, ngram, num_of_keywords,
                                           n_contextual_window, N, TH, temporal_tagger_name, date_granularity,
                                           begin_date, end_date)
        return jsonify(result_model)
    except Exception as e:
        return jsonify({'message': str(e)})


def get_docs(uploaded_file):
    # Create a ZipFile Object and load sample.zip in it
    with ZipFile(uploaded_file, 'r') as zipObj:
        # Extract all the contents of zip file in current directory
        zipObj.extractall('upload_files')
    docs = []
    files = [f for f in glob.glob('upload_files/' + '*.txt', recursive=True)]
    for file in files:
        with open(file, encoding="utf8", errors='ignore') as text_file:
            contents = text_file.read()
        docs.append(contents)
    return docs


if __name__ == '__main__':
    main()
