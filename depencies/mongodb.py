import json
import datetime
import sys
from pymongo import MongoClient, errors

# Class implemented to do mongodb-related functions
# Still contains useless functions that will be removed
class database_handler(object): 
    # Initialization of database connection
    def __init__(self, ip, port):
        self.mongoclient = MongoClient(ip, port)
        self.category_db = self.mongoclient.category

    # Returns all data in a collection 
    def return_collection(self, collection):
        return [items for items in collection.find({})]

    # Clears an entire collection and prints the ammount of objects removed
    def clear_collection(self, collection):
        cnt = 0

        for item in collection.find({}):
            collection.remove(item)
            cnt += 1

        if cnt > 0:
            print "Cleared %d elements in the collection" % cnt
        else:
            print "Nothing to clear."

    # Removes a single datapoint based on the datareference. 
    def remove_one(self, collection, id):
        data = collection.find_one({'_id': id})

        if data is not None:
            collection.remove({'_id': id})

    # Returns avilable docs in a collection
    def get_available_category_collections(self):
        category_collection = self.category_db.collection_names(include_system_collections=False)
        return category_collection

    # Adds data to a category and returns the ID generated by MongoDB
    def add_new_category_data(self, database, category, name, cur_time, ip="", url="", filehash=""):
        collection = database[category]

        if collection.find({"name": name}).count() > 0:
            category_data = collection.find_one({"name": name})

            # Might want to append ObjectID instead of IP? idk :)
            # Append appropriate data to list
            if ip and ip not in category_data["ips"]:	
                category_data["ips"].append(ip)
            if url and url not in category_data["urls"]:
                category_data["urls"].append(url)
            if filehash and filehash not in category_data["filehash"]:	
                category_data["filehash"].append(filehash)

            category_data["modifieddate"] = cur_time
            collection.save(category_data)
            return category_data["_id"]
        else:
            # To create a new object
            category_data = {
                "name": name,
                "ips": [],
                "urls": [],
                "filehash": [],
                "addeddate": cur_time,
                "modifieddate": cur_time
            }

            if ip:
                category_data["ips"].append(ip)
            if url:
                category_data["urls"].append(url)
            if filehash:
                category_data["filehash"].append(filehash)

            return_id = collection.insert_one(category_data).inserted_id
            return return_id

    # Adds data to a specific dataset. 
    def add_data(self, database, ip_collection, category_db, ip, category="", name=""):
        object_exists = False

        # Creates category data.
        category_id = ""
        cur_time = datetime.datetime.now()

        if category and name:
            category_id = self.add_new_category_data(category_db, category, name, cur_time, ip=ip) 

        ## FIX
        # ADD URL AND HASH
        # Item already exists.
        if ip_collection.find({"ip": ip}).count() > 0:
            tmp_data = ip_collection.find_one({"ip": ip})
            # Verify data in containers

            # Might be slow!
            category_exists = False
            for item in tmp_data["containers"]:
                if item["name"] == name and item["category"] == category:
                    category_exists = True
                    break

            # append
            if not category_exists:
                tmp_data["containers"].append({"name": name, \
                    "category": category, "mongo_id": category_id, "addeddate": cur_time})
                tmp_data["modifieddate"] = cur_time
                ip_collection.save(tmp_data)

        # Return otherwise - might want to modify date of category if category/name exists?

        else:
            # Base information to add to a colleciton
            tmp_data = {
                "ip": "%s" % ip,
                "containers": [],
                "addeddate": "%s" % cur_time,
                "modifieddate": "%s" % cur_time
            }

        if category_id:
            tmp_data["containers"].append({"name": name, \
                "category": category, "mongo_id": category_id, "addeddate": cur_time})

        try:
            return ip_collection.insert_one(tmp_data).inserted_id
        except errors.DuplicateKeyError:
            return False

    def find_category_object(self, collection, id):
        data = collection.find_one({"_id": id})
        return data

    def find_category_data(self, collection, name):
        for item in collection.find({}):
            if item["name"] == name:
                return item

        return False

    # Finds a single p in a collection - make generic
    def find_object(self, collection, name):
        ## FIX - Might break because of first part of list. Need all of them concated.
        if not name:
            return [x for x in collection.find({})]

        return collection.find_one({"ip": name})

    # Made to test lists - Needs to contain category and stuff
    def get_data(self):
        return open("blocklist.php", "r").readlines()

    # Clears the available databases 
    def clear_all_databases(self):
        data = self.mongoclient.database_names()
        for items in data:
            self.mongoclient.drop_database(self.mongoclient[items])	
            print "Dropped %s" % items

if __name__ == "__main__":
    mongodbserver = '127.0.0.1'
    mongodbport = 27017
    print "Connecting to mongodb at %s:%d" % (mongodbserver, mongodbport)

    client = database_handler(mongodbserver, mongodbport)
    try:
        if sys.argv[1] == "clear":
            client.clear_all_databases()
            exit()
    except IndexError:
        client.test_func()
        exit()

    client.test_func()
