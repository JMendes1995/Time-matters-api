from time_matters import timeMatters
from flask import Flask, request
from flask_restplus import Api, Resource, fields
import os

flask_app = Flask(__name__)
app = Api(app=flask_app)


name_space = app.namespace('Time_Matters', description='get relevant dates and his score form a text')
@name_space.route("/<string:text>")
class MyResource(Resource):
    @app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
             params={'text': 'Insert text', 'max_distance': 'max distance between words',
                     'threshold': 'minimum value allow of dice calculation (default 0.05)',
                     'max_array_length': 'max length considered of vector'})
    def get(self, text):
        max_distance = int(request.args.get('max_distance', 5))
        threshold = float(request.args.get('threshold', 0.05))
        max_array_length = int(request.args.get('max_distance', 0))
        arr = timeMatters(text, max_distance, threshold, max_array_length)

        json_dates = format_data(arr)
        return {'Value': json_dates}


def format_data(dates_list):
    json_dates = []
    for i in range(len(dates_list)):
        for k in range(len(dates_list[i])):
            json_dates.append({'date': dates_list[i], 'score': dates_list[i][1]})
    print(json_dates)
    return json_dates


if __name__ == '__main__':
    flask_app.debug = True
    port = int(os.environ.get("PORT", 443))
    flask_app.run(host='0.0.0.0', port=port)
    flask_app.run()
