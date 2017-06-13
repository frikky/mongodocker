#!flask/bin/python

import json
import datetime
from sys import argv
from werkzeug import Response
from pymongo import MongoClient
from mongodb import database_handler
from bson import ObjectId, json_util
from flask import Flask, request, abort

app = Flask(__name__)
serverip = '127.0.0.1'
serverport = 27017

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

class correlate_data(database_handler):
	def __init__(self, ip, port):
            self.database = database_handler(ip, port)

	# Returns error messages
	def default_error(self, data="", path=""):
            if not data or not path:	
                return {'error': 'Can\'t find the information you\'re looking for'}

            return {'error': 'Can\'t find %s in collection %s' % (data, path)}

        # Do mongodb stuff
	def get_data(self, ip_db, url_db, hash_db, path, data):
		resp = ""

		# Add url and ip
		if path == "ip":
			resp = self.database.find_object(ip_db["ips"], data)

		# Verifies after basic categories 
		# Can be verified here? Attempt URL, Hash and URL lookup -> Use in if
		if not resp:
			categories = self.database.get_available_category_collections()
                        
                        # Check if name in category exists > IP exists.
                        resp = self.database.find_category_data(\
                            find_data.database.mongoclient["category"][path], data)


			# Needs reverse path check to IP, URL or HASH.
			if path in categories and not resp:
				category_collection = find_data.database.mongoclient["category"][path]

                                # Matches category
				resp = self.database.find_object(find_data.database.mongoclient["category"][path], data)

				# Find IP/URL etc, lookup mognodb ID, find it and return
				# Validate if ip, url or hash with regex?

                                ### Finds IP
                                if not resp:
                                    resp = self.database.find_object(ip_db["ips"], data)

				if resp is None:
					return self.default_error(path, resp)

                                if isinstance(resp, dict):
                                    for item in resp["containers"]:
                                            if item["category"] == path:
                                                    cur_id = item["mongo_id"]	
                                                    break

                                    # Ad failcheck here in case it doesn't exist? Should _ALWAYS_ exist if everything work.
                                    #resp = self.database.find_category_object(category_collection, cur_id)

		if resp is None or not resp:
			return self.default_error(path, resp)

		return resp 

	def generate_data(self):
		db = self.database.mongoclient.ip
		category_db = self.database.mongoclient.category

		ip = "192.168.0.1\n"
		category = "c2"
		name = "zeus"

		# Generate other data first to append to the IP-range
		ip = ip[:-1]
		data = self.database.add_new_ip(db, db.ips, category_db, ip, \
			category=category, name=name)

		return data

find_data = correlate_data(serverip, serverport)

@app.errorhandler(404)
def page_not_found(e):
	return jsonify(find_data.default_error())

@app.route('/', methods=['GET'])
def standard():
	return jsonify(find_data.default_error())

@app.route('/', methods=['POST'])
def add_task():
# Verify if the host is part of the API subscribers 
	data = {"error": "OMG SOMETHING WENT WRONG"}
	return jsonify(data)


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

@app.route('/<string:path>/<string:task>', methods=['GET'])
def get_tasks(path, task):
	#find_data.generate_data()

	#db = find_data.database.mongoclient[path]
	ip_db = find_data.database.mongoclient.ip
	url_db = find_data.database.mongoclient.url
	hash_db = find_data.database.mongoclient.hash

	data = find_data.get_data(ip_db, url_db, hash_db, path, task)

	if len(data) == 0:
		abort(404)

        # LOGIC PLS
	try:
		tmp_ret = data
	except TypeError:
		return jsonify({"error": "Python fault error in jsonifying data."})

	try:
                #print data
		return jsonify(result=tmp_ret)
	except ValueError:
		return jsonify({"error": "%s is not a valid path." % path}) 

        # Jsonify list?

@app.route('/<string:path>', methods=['GET'])
def get_category(path): 
    return get_tasks(path, "")

if __name__ == '__main__':
	try:
		app.run(debug=True, threaded=True, port=int(argv[1]))
	except IndexError:
		app.run(debug=True, threaded=True, port=80)
