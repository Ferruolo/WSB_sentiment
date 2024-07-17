
from flask import Flask, request, make_response, jsonify, render_template
import pandas
import json
import datetime
# import fxns
print('PRE_REQS LOADED')
app = Flask(__name__)


@app.route("/getWSB", methods=['GET'])
def getWSB():
    with open('data.json', 'r') as f:
        response = json.load(f) 
    return make_response(response, 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
