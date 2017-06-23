#!flask/bin/python

import json
import datetime
from sys import argv
from werkzeug import Response
from bson.objectid import ObjectId 
from bson import json_util
from flask import Flask, request, abort

from depencies.handle_data import correlate_data

app = Flask(__name__)
serverip = '0.0.0.0'
serverport = 27017
find_data = correlate_data(serverip, serverport)

# BSON to JSON parser
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return unicode(obj)

        return json.JSONEncoder.default(self, obj)

# Rewriting flasks jsonify function with the above class in mind
def jsonify(*args, **kwargs):
    return Response(json.dumps(dict(*args, **kwargs), cls=JSONEncoder), \
        mimetype='application/json')

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(find_data.default_error())

# Default :)
@app.route('/', methods=['GET'])
def standard():
    return jsonify(find_data.default_error())

# Verify if the host is part of the API subscribers 
@app.route('/', methods=['POST'])
def add_task():
    data = {"error": "OMG SOMETHING WENT WRONG"}

    return jsonify(data)

# Lists all available categories
@app.route('/categories', methods=['GET'])
def get_categories():
    data = {"categories": []}
    for category in find_data.database.get_available_category_collections():
        data["categories"].append(category)

    return jsonify(data)

### FIX
# Used for debug purposes
@app.route('/clear', methods=['GET'])
def clear_data():
    find_data.database.clear_all_databases()
    return jsonify({"Status": "Database cleared."})

@app.route('/generate', methods=['GET'])
def generate_data():
    find_data.generate_data()
    return jsonify({"Status": "Generated data."})

@app.route('/<string:path>/<string:task>', methods=['GET'])
def get_tasks(path, task):

    # This shit is stupid.
    ip_db = find_data.database.mongoclient.ip
    url_db = find_data.database.mongoclient.url
    hash_db = find_data.database.mongoclient.hash

    data = find_data.get_data(ip_db, url_db, hash_db, path, task)

    if len(data) == 0:
        abort(404)

    try:
        return jsonify(result=data)
    except ValueError:
        return jsonify({"error": "%s is not a valid path." % path}) 


@app.route('/<string:path>', methods=['GET'])
def get_category(path): 
    return get_tasks(path, "")

if __name__ == '__main__':
    try:
        app.run(debug=True, threaded=True, host="0.0.0.0", port=int(argv[1]))
    except IndexError:
        app.run(debug=True, threaded=True, host="0.0.0.0", port=80)
