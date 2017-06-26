#!/bin/python

import json
import datetime
import os
from sys import argv
from werkzeug import Response
from bson.objectid import ObjectId 
from bson import json_util
from flask import Flask, request, abort, render_template, redirect

from depencies.handle_data import correlate_data

app = Flask(__name__)
serverip = '0.0.0.0'
serverport = 27017
find_data = correlate_data(serverip, serverport)

if not os.path.isdir("tmp_data/"):
    os.mkdir("tmp_data")

## FIX
API_KEY = "TESTING"

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
    return render_template("index.html", title="hi")

@app.errorhandler(400)
def page_not_found(e):
    return jsonify({"error": "Invalid data requested."})

# Default :)
@app.route('/', methods=['GET'])
def standard():
    paragraph=["PARAGRAPH"]
    try:
        return render_template("index.html", title="hi", paragraph=paragraph)
    except Exception, e:
        return str(e)

# Handles in browser search
@app.route('/search', methods=['POST'])
def search():
    data = request.form["search"]
    request.title = data
    return get_tasks(find_data.regex_check(data), data)

# Handles manual search
"""
@app.route('/search/<string:data>', methods=['GET'])
def search_manual(data):
    return get_tasks(find_data.regex_check(data), data)
"""

# Verify if the host is part of the API subscribers 
@app.route('/', methods=['POST'])
def add_task():
    try:
        # Too cluttered, move to handle_data.py -- FIX
        if request.headers["TOKEN"] == API_KEY:
            try:
                data = json.loads(request.data)
            except ValueError:
                return jsonify({"error": "Invalid request."})
                
            accepted_types = ["ip", "url", "hash"]
            if data["type"] in accepted_types:
                ret = find_data.verify_post_data(data["type"], \
                    data["data"], data["category"], data["name"])

                # Should always return valid data?
                try:
                    return jsonify(ret)
                except (ValueError, TypeError):
                    pass

            # FIX - Better error messages.
            return jsonify({"error": "Invalid request."})
            # Verify request now
    except KeyError:
        pass

    data = {"error": "Missing or wrong API key. Header: TOKEN"}
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

### FIX 
# Used for testing purposes
@app.route('/generate', methods=['GET'])
def generate_data():
    find_data.read_config()
    return jsonify({"Status": "Generated data. Check /categories"})

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

# FIX - HTTPS redirect
"""
@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
"""

# FIX - verify headers
@app.after_request
def apply_caching(response):
    """
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Strict-Transport-Security"] = "max-age=31536000 ; includeSubDomains"
    """
    response.headers["Server"] = ":)"

    return response

if __name__ == '__main__':
    try:
        app.run(debug=True, threaded=True, host="0.0.0.0", port=int(argv[1]))
    except IndexError:
        app.run(debug=True, threaded=True, host="0.0.0.0", port=80)
