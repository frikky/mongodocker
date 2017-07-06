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
        self.ip_db = self.mongoclient.ip

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

    def get_available_ip_collections(self):
        ip_collection = self.ip_db.collection_names(include_system_collections=False)
        return ip_collection

    # Returns avilable docs in a collection
    def get_available_category_collections(self):
        category_collection = self.category_db.collection_names(include_system_collections=False)
        return category_collection

    # Finds the IP collection
    def evaluate_collection(self, data_type, item):
        if data_type == "ip":
            type_collection = ""
            for dot_value in range(len(item)):
                if item[dot_value] == ".":
                    collection = item[:dot_value]
                    if int(collection) < 256 and int(collection) > -1:
                        return collection
        else:
            # Uses the last part as TLD can't be < 2
            if "." in item[:2]:
                return item[-2:]

            return item[:2]

    # Now able to handle bulk input
    def add_data_new(self, database, data_type, item, category, name, extra_data={}, **kwargs):
        """ 
            database - Which database to use
            category_db - Who was the sender? What kind of information?
            data_type - ip, url, hash
            item - actual data
            category - what category (malware, scanning etc)
            name - name of the service that it was recieved from
        """
        cur_time = datetime.datetime.now()

        # Should be able to add multiple new items at the same time
        not_found_list = []
        if not isinstance(item, list):
            tmp_item = item
            item = [tmp_item]

        for data in item:
            # Might make it slower to compute double
            type_collection = database[self.evaluate_collection(data_type, data)]

            tmp_data = type_collection.find_one({data_type: data})
            if not tmp_data:
                type_data = {
                    data_type: data,
                    "containers": [],
                    "addeddate": "%s" % cur_time,
                    "modifieddate": "%s" % cur_time
                }

                category_data = {
                    "name": name,
                    "category": category,
                    "addeddate": cur_time,
                    "modifieddate": cur_time
                }
                
                if extra_data:
                    category_data["comment"] = extra_data 

                type_data["containers"].append(category_data)
                type_collection.insert_one(type_data).inserted_id

            else:
                containers = tmp_data["containers"]

                # Verifies if a container is there 
                # and updates time if it exists (last seen)
                exists_check = False
                for container in containers:
                    if container["name"] == name and container["category"] == category:
                        container["modifieddate"] == cur_time
                        container["comment"] = extra_data
                        exists_check = True

                # Appends only if it doesn't exist
                if not exists_check:
                    category_data = {
                        "name": name,
                        "category": category,
                        "addeddate": cur_time,
                        "modifieddate": cur_time
                    }

                    if extra_data:
                        category_data["comment"] = extra_data

                    tmp_data["containers"].append(category_data)

                print "Updated document for %s" % data
                type_collection.save(tmp_data)

    def find_category_object(self, collection, id):
        data = collection.find_one({"_id": id})
        return data

    def find_category_data(self, collection, name):
        for item in collection.find({}):
            if item["name"] == name:
                return item

        return False

    # Find basic
    def find_object_new(self, data_type, item):
        db = self.mongoclient[data_type]
        collection = db[self.evaluate_collection(data_type, item)]
        #print data_type, item

        return collection.find_one({data_type: item})

    def find_category_object(self, collection, id):
        data = collection.find_one({"_id": id})
        # Finds the database that should be used
                
        #data = type_collection.find({data_type: item})
        #print data.count()

    # Finds a single p in a collection - make generic
    def find_object(self, collection, type, name):
        ## FIX - Might break because of first part of list. Need all of them concated.
        if not name:
            return [x for x in collection.find({})]

        return collection.find_one({type: name})

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
        print "Did you mean to use the argument \"clear\" or run handle_data.py?"
        exit()
    
