from Time_Matters_SingleDoc import Time_Matters_SingleDoc, Time_Matters_SingleDoc_PerSentence
from flask import Flask, request
from flask_restplus import Api, Resource, fields, inputs
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from Time_Matters_MultipleDoc import Time_Matters_MultipleDoc
import glob, codecs
import os
from zipfile import ZipFile


flask_app = Flask(__name__, instance_path='D:\programming\codePython\Time-matters-api>')
app = Api(app=flask_app)


bool_inputs_text = app.parser()
bool_inputs_text.add_argument('analysis_sentence', type=inputs.boolean, default=True)
bool_inputs_text.add_argument('ignore_contextual_window_distance', type=inputs.boolean, default=False)
name_space = app.namespace('Time-Matters-SingleDoc', description='get relevant dates and his score form a text')
@name_space.route("/")
class MyResource(Resource):
    @app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
             params={'text': 'Insert Text',
                     'Language': 'Select on of the following languages under quotes "": English, Portuguese, Spanish, Germany, Dutch, Italian, French.',
                     'contextual_window_distance': 'max distance between words',
                     'Th': 'th is the minimum DICE threshold similarity value that defines the terms that are part of the contexto vector',
                     'N': 'N is the size of the context vector',
                     'max_keywords': 'define max keywords',
                     'heideltime_document_type': 'Type of the document specified by <file> (options: News, Narrative, Colloquial, Scientific).',
                     'heideltime_document_creation_time': 'Document creation date in the format (YYYY-MM-DD). Note that this date will only be taken into account when News or Colloquial texts are specified.',
                     'heideltime_date_granularity': 'Value of granularity. Options: Year, Month, day (e.g., “Year”)'
                     })
    @app.expect(bool_inputs_text)
    def get(self):
        text = str(request.args.get('text'))
        lang = str(request.args.get('Language', 'English'))
        hdt = str(request.args.get('heideltime_document_type', 'News'))
        hdct = str(request.args.get('heideltime_document_creation_time', ''))
        max_distance = int(request.args.get('contextual_window_distance', 10))
        threshold = float(request.args.get('Th', 0.05))
        max_array_length = int(request.args.get('N', 0))
        max_keywords = int(request.args.get('max_keywords', 10))
        heideltime_date_granularity = str(request.args.get('heideltime_date_granularity',''))
        data = bool_inputs_text.parse_args()
        print(lang)
        json_dates = Time_Matters_SingleDoc(text, lang, max_distance, threshold, max_array_length, max_keywords, data['analysis_sentence'], data['ignore_contextual_window_distance'], hdt, hdct, heideltime_date_granularity)
        return json_dates


bool_inputs_sentence = app.parser()
bool_inputs_sentence.add_argument('ignore_contextual_window_distance', type=inputs.boolean, default=False)
name_space = app.namespace('Time-Matters-SingleDoc', description='get relevant dates and his score per sentence')
@name_space.route("/Time_Matters_SingleDoc_PerSentence")
class MyResource(Resource):
    @app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
             params={'text': 'Insert Text',
                     'Language': 'Select on of the following languages under quotes "": English, Portuguese, Spanish, Germany, Dutch, Italian, French.',
                     'contextual_window_distance': 'max distance between words',
                     'Th': 'th is the minimum DICE threshold similarity value that defines the terms that are part of the contexto vector',
                     'N': 'N is the size of the context vector',
                     'max_keywords': 'define max keywords',
                     'heideltime_document_type': 'Type of the document specified by <file> (options: News, Narrative, Colloquial, Scientific).',
                     'heideltime_document_creation_time': 'Document creation date in the format (YYYY-MM-DD). Note that this date will only be taken into account when News or Colloquial texts are specified.',
                     'heideltime_date_granularity': 'Value of granularity. Options: Year, Month, day (e.g., “Year”)'
                     })
    @app.expect(bool_inputs_sentence)
    def get(self):
        text = str(request.args.get('text'))
        lang = str(request.args.get('Language', 'English'))
        hdt = str(request.args.get('heideltime_document_type', 'News'))
        hdct = str(request.args.get('heideltime_document_creation_time', ''))
        max_distance = int(request.args.get('contextual_window_distance', 10))
        threshold = float(request.args.get('Th', 0.05))
        max_array_length = int(request.args.get('N', 0))
        max_keywords = int(request.args.get('max_keywords', 10))
        heideltime_date_granularity = str(request.args.get('heideltime_date_granularity', ''))
        data = bool_inputs_sentence.parse_args()

        json_dates, sentences = Time_Matters_SingleDoc_PerSentence(text, lang, max_distance, threshold, max_array_length, max_keywords, data['ignore_contextual_window_distance'], hdt, hdct, heideltime_date_granularity)
        return json_dates


# time Matters multi-docs

upload_parser = app.parser()
upload_parser.add_argument('Zip_file', location='files',
                           type=FileStorage, required=True)
bool_inputs_sentence = app.parser()
bool_inputs_sentence.add_argument('ignore_contextual_window_distance', type=inputs.boolean, default=False)
name_space = app.namespace('Time-Matters-MultipleDoc', description='get relevant dates and his score from multiple docs'    )
@name_space.route("/")
class MyResource(Resource):
    @app.expect(upload_parser)
    @app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
             params={'Language': 'Select on of the following languages under quotes "": English, Portuguese, Spanish, Germany, Dutch, Italian, French.',
                     'contextual_window_distance': 'max distance between words',
                     'Th': 'th is the minimum DICE threshold similarity value that defines the terms that are part of the contexto vector',
                     'N': 'N is the size of the context vector',
                     'max_keywords': 'define max keywords',
                     'heideltime_document_type': 'Type of the document specified by <file> (options: News, Narrative, Colloquial, Scientific).',
                     'heideltime_document_creation_time': 'Document creation date in the format (YYYY-MM-DD). Note that this date will only be taken into account when News or Colloquial texts are specified.',
                     'heideltime_date_granularity': 'Value of granularity. Options: Year, Month, day (e.g., “Year”)'
                     })

    @app.expect(bool_inputs_sentence)
    def post(self):
        lang = str(request.args.get('Language', 'English'))
        hdt = str(request.args.get('heideltime_document_type', 'News'))
        hdct = str(request.args.get('heideltime_document_creation_time', ''))
        max_distance = int(request.args.get('contextual_window_distance', 10))
        threshold = float(request.args.get('Th', 0.05))
        max_array_length = int(request.args.get('N', 0))
        max_keywords = int(request.args.get('max_keywords', 10))
        heideltime_date_granularity = str(request.args.get('heideltime_date_granularity', ''))
        data = bool_inputs_sentence.parse_args()

        # Get file data
        f = request.files['Zip_file']
        f.save(secure_filename(f.filename))
        text_list = get_docs(f.filename)

        # Docs analysis
        json_dates, sentences = Time_Matters_MultipleDoc(text_list, lang, max_distance, threshold, max_array_length, max_keywords, data['ignore_contextual_window_distance'], hdt, hdct, heideltime_date_granularity)
        remove_files(f.filename)
        return json_dates


def get_docs(uploaded_file):
    # Create a ZipFile Object and load sample.zip in it
    with ZipFile(uploaded_file, 'r') as zipObj:
        # Extract all the contents of zip file in current directory
        zipObj.extractall('upload_files')
    docs = []
    files = [f for f in glob.glob('upload_files/'+'*.txt', recursive=True)]
    for file in files:
        text_file = codecs.open(file, "r", "utf-8")
        contents = text_file.read()
        docs.append(contents)
    return docs


def remove_files(uploaded_file):
    filelist = glob.glob(os.path.join('upload_files', "*.*"))
    for f in filelist:
        os.remove(f)
    os.remove(uploaded_file)


if __name__ == '__main__':
    flask_app.debug = True
    flask_app.run()
