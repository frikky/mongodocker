#!/bin/python

import json
import ssl
import os
import datetime
from sys import argv
from werkzeug import Response
from bson.objectid import ObjectId 
from bson import json_util
from flask import Flask, request, abort, render_template, redirect

from depencies.handle_data import correlate_data
from scripts.virustotal import virustotal
import config.config as conf

app = Flask(__name__)
serverip = 'localhost'
serverport = 27017
find_data = correlate_data(serverip, serverport)

if not os.path.isdir("tmp_data/"):
    os.mkdir("tmp_data")

server_ip = "localhost"

# FIX - Top kek
API_KEY = conf.API_KEY

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

# Basic error handler for 404's
@app.errorhandler(404)
def page_not_found(e):
    return render_template("index.html", title="hi")

# Basic errorhandler for 400's
@app.errorhandler(400)
def page_not_found(e):
    return jsonify({"error": "Invalid data requested."})

# Default route
@app.route('/', methods=['GET'])
def standard():
    paragraph=["PARAGRAPH"]
    try:
        return render_template("index.html", title="hi", paragraph=paragraph)
    except Exception, e:
        return str(e)

# Handles post request searches
@app.route('/search', methods=['POST'])
def search():
    data = request.form["search"]
        
    # FIX error code and else statement
    if not data or data == "\n" or data is None:
        code = 301
        try:
            if request.headers["Referer"] in request.url:
                return redirect(request.headers["Referer"], code=code)
            else:
                return redirect(server_ip, code=code)
        except KeyError:
            return redirect(server_ip, code=code)

    # Finds IP, URL, hash etc
    data_type = find_data.regex_check(data)
    
    # FIX - URL should always contain dots? Idk
    if data_type == "url" and not "." in data:
        # Might be error in redirect.
        return redirect("http://%s" % server_ip, code=301)

    # server.py->handle_data->mongodb->function
    return_data = find_data.database.find_object_new(data_type, data)
    # FIX EXAMPLE SEARCHES (should be in db):
    # 81.177.140.251
    # 83.15.254.242
    # 83.212.117.233
    print return_data

    #print "IS THERE DATA? %s" % return_data
    if return_data == None:
        return redirect("http://%s" % server_ip, code=301)

    # FIX - ADD ip and URL OSint \o/
    # FIX virustotal - hash shouldn't be in object creation
    if data_type == "hash":
        # Adds data before redirecting if file exists
        vt = virustotal(data)
        vt_data = vt.check_vt()
        vt.injest(data=vt_data) # Also adds to the DB :)
        try:
            if vt_data["positives"] > 0:
                return redirect("https://virustotal.com/en/file/%s/analysis" % data.lower(), code=301)
        except KeyError:
            pass
    else:
        return jsonify(return_data)

    return render_template("index.html", code=404)

def verify_error(data):
    try:
        data["result"]["error"]
    except KeyError:
        return data

    return False

# Handles manual search
@app.route('/search/<string:data>', methods=['GET'])
def search_manual(data):
    return_data = get_tasks(find_data.regex_check(data), data)

    if verify_error(return_data.data):
        return return_data 

    return render_template("index.html", code=404)


# API to add data to the DB with POST requests.
@app.route('/', methods=['POST'])
def add_task():
    try:
        # Too cluttered, move to handle_data.py -- FIX
        if request.headers["auth"] == API_KEY:
            try:
                data = json.loads(request.data)
            except ValueError:
                return jsonify({"error": "Invalid request."})
                
            # Not sure if static types are smart 
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
        else:
            data = {"error": "Wrong API key."}
    except KeyError:
        data = {"error": "Missing API key. Header: \"TOKEN\""}
        pass

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
"""
@app.route('/clear', methods=['GET'])
def clear_data():
    find_data.database.clear_all_databases()
    return jsonify({"Status": "Database cleared."})
"""

### FIX 
# Used for testing purposes
@app.route('/generate', methods=['GET'])
def generate_data():
    find_data.read_config_new()
    return jsonify({"Status": "Generated data. Check /categories"})

@app.route('/<string:path>/<string:task>', methods=['GET'])
def get_tasks(path, task):
    # ffs bootstrap
    if path == "fonts":
        return ""
    
    find_data.regex_check(task)

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
    data = get_tasks(path, "")
    return data

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
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Strict-Transport-Security"] = "max-age=31536000 ; includeSubDomains"

    # Overwrites the default response. Can't simply delete it apparently. 
    # Overwrite werkzeug request handler, not Flask
    #response.headers["Server"] = ":)"

    return response

if __name__ == '__main__':
    debug = True
    server_ip = "localhost"
    try:
        if not int(argv[1]) == 443:
            debug = False
            app.run(debug=debug, threaded=True, host=server_ip, port=int(argv[1]))
        else:
            context = (conf.crt, conf.key)
            debug = False
            app.run(debug=debug, ssl_context=context, threaded=True, host=server_ip, port=int(argv[1]))
    except IndexError:
        app.run(debug=debug, threaded=True, host=server_ip, port=80)
