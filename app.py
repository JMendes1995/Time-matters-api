from time_matters import timeMatters, timeMattersPerSentence
from flask import Flask, request
from flask_restplus import Api, Resource, fields, inputs
import os

flask_app = Flask(__name__)
app = Api(app=flask_app)


bool_inputs_text = app.parser()
bool_inputs_text.add_argument('analysis_sentence', type=inputs.boolean, default=True)
bool_inputs_text.add_argument('ignore_contextual_window_distance', type=inputs.boolean, default=False)
name_space = app.namespace('Time_Matters', description='get relevant dates and his score form a text')
@name_space.route("/")
class MyResource(Resource):
    @app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
             params={'text': 'Insert Text',
                     'contextual_window_distance': 'max distance between words',
                     'Th': 'th is the minimum DICE threshold similarity value that defines the terms that are part of the contexto vector',
                     'N': 'N is the size of the context vector',
                     'max_keywords': 'define max keywords'})
    @app.expect(bool_inputs_text)
    def get(self):
        text = str(request.args.get('text'))
        max_distance = int(request.args.get('contextual_window_distance', 10))
        threshold = float(request.args.get('Th', 0.05))
        max_array_length = int(request.args.get('N', 0))
        max_keywords = int(request.args.get('max_keywords', 10))
        data = bool_inputs_text.parse_args()

        json_dates = timeMatters(text, max_distance, threshold, max_array_length, max_keywords, data['analysis_sentence'], data['ignore_contextual_window_distance'])
        return json_dates


bool_inputs_sentence = app.parser()
bool_inputs_sentence.add_argument('ignore_contextual_window_distance', type=inputs.boolean, default=False)
name_space = app.namespace('Time_Matters_per_sentence', description='get relevant dates and his score per sentence')
@name_space.route("/")
class MyResource(Resource):
    @app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
             params={'text': 'Insert Text',
                     'contextual_window_distance': 'max distance between words',
                     'Th': 'th is the minimum DICE threshold similarity value that defines the terms that are part of the contexto vector',
                     'N': 'N is the size of the context vector',
                     'max_keywords': 'define max keywords'})
    @app.expect(bool_inputs_sentence)
    def get(self):
        text = str(request.args.get('text'))
        max_distance = int(request.args.get('contextual_window_distance', 10))
        threshold = float(request.args.get('Th', 0.05))
        max_array_length = int(request.args.get('N', 0))
        max_keywords = int(request.args.get('max_keywords', 10))
        data = bool_inputs_sentence.parse_args()

        json_dates = timeMattersPerSentence(text, max_distance, threshold, max_array_length, max_keywords, data['ignore_contextual_window_distance'])
        return json_dates

if __name__ == '__main__':
    flask_app.debug = True
    port = int(os.environ.get("PORT", 443))
    flask_app.run(host='0.0.0.0', port=port)
    flask_app.run()
