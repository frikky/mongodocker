#!flask/bin/python
from pymongo import MongoClient
from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

class correlate_data(object):
	def __init__(self, ip, port):
		self.save_data()
		self.connect_database(ip, port)

	def connect_database(self, ip, port):
		self.mongoclient = MongoClient('192.168.1.129', 27017)

	def save_data(self):
		self.data = [
			{
				'id': '192.168.0.1',
				'title': u'Buy groceries',
				'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
				'done': False
			},
			{
				'id': '192.168.0.2',
				'title': u'Learn Python',
				'description': u'Need to find a good Python tutorial on the web', 
				'done': False
			}
		]

	def default_error(self, data="", path=""):
		if not data or not path:	
			return {'error': 'Can\'t find the information you\'re looking for'}
			
		return {'error': 'Can\'t find %s in %s' % (path, data)}

	# Find the right database
	def find_database(self, path):
		return True

	# Do mongodb stuff
	def get_data(self, path, data):
		if not self.find_database(path):
			return self.default_error(data, path)
			
		# Add path check
		for item in self.data:
			if item["id"] == data:
				return item

		return self.default_error(data, path)

#find_data = correlate_data()
@app.errorhandler(404)
def page_not_found(e):
    return find_data.default_error()

@app.route('/<string:path>/<string:task>', methods=['GET'])
def get_tasks(path, task):
	data = find_data.get_data(path, task)
	print request.headers["host"]

	if len(task) == 0:
		abort(404)
	#task = [task for task in data.get_data(path, ) if task['id'] == task_id]

	return jsonify(data)


# ip, category, timeadded, timemodified

if __name__ == '__main__':
	#app.run(debug=True)
	mongoclient = MongoClient('192.168.1.129', 27017)
	db = mongoclient.ip
	posts = db.ips
	post = {
		"ip": "192.168.0.1",
		"id": "1",
		"containers": [{
			"dbname": "c2",	
			"containername": "zeus",
			"id": 1
		}],
		"addeddate": datetime.datetime.utcnow(),
		"modifieddate": datetime.datetime.utcnow()
	}

	post_id = posts.insert_one(post).inserted_id
	for document in posts.find({}):
		print document
