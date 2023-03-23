from flask import Flask, jsonify
from predict import infer
import os
import json
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

app = Flask(__name__)

@app.route('/infer', methods=['GET'])
def infer_api():
    result = infer()
    return json.dumps(result)

if __name__ == '__main__':
    app.run(debug=True)
