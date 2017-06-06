#!flask/bin/python
from pymongo import MongoClient
from flask import Flask, jsonify, request
import datetime
from mongodb import database_handler

app = Flask(__name__)

class correlate_data(database_handler):
	def __init__(self, ip, port):
		self.database = database_handler(ip, port)

	# Returns error messages
	def default_error(self, data="", path=""):
		if not data or not path:	
			return {'error': 'Can\'t find the information you\'re looking for'}

		return {'error': 'Can\'t find %s in collection %s' % (data, path)}

		# Do mongodb stuff
	def get_data(self, collection, path, data):
		data = self.database.find_object(collection, data)

		print data.count()
		return self.default_error(path, data)

serverip = '172.28.3.163'
serverport = 80
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
	data = {"error": "OMG SOMETHING WENT WRONG"} ## ADD STUFF
	return jsonify(data)

@app.route('/<string:path>/<string:task>', methods=['GET'])
def get_tasks(path, task):
	db = find_data.database.mongoclient
	data = find_data.get_data(db.ip[path], path, task)

	print request.headers["host"]

	if len(task) == 0:
		abort(404)

	return jsonify(data)


# ip, category, timeadded, timemodified

if __name__ == '__main__':
	app.run(debug=True)
