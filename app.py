from flask import Flask
from time_matters import timeMatters
import os

app = Flask(__name__)
@app.route("/")
def home():
    return "Hello, World!"


if __name__ == '__main__':  
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port)
