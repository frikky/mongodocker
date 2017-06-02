from pymongo import MongoClient
import json
import datetime

class database_handler(object): 
    def __init__(self, ip, port):
        self.mongoclient = MongoClient(ip, port)
        self.ip_cnt = 0

    def print_data(self, collection):
        return [items for items in collection.find({})]

    def clear_collection(self, collection):
        cnt = 0
        for item in collection.find({}):
            collection.remove(item)
            cnt += 1

        print "Cleared %d elements in the collection" % cnt

    def modify_ip(self, database, ip):
        pass

    def add_category_data(self, database, ip, category, name):
        category = database[category]
        category.find(
        
        category.find( 
        data = {
            "name": name,    
            "ips": [],
        }

        post_id = collection.insert_one(data).inserted_id

    def add_new_ip(self, database, collection, ip, category="", name="", id=0):
        data = collection.find({"ip": "%s" % ip})

        if category and name:
            verify = self.add_category_data(self, database, ip, category, name) 

        if data.count() != 0:
            return False
            
        # Base information to add to a colleciton
        data = {
            "ip": "%s" % ip,
            "id": "%d" % self.ip_cnt,
            "containers": [],
            "addeddate": datetime.datetime.utcnow(),
            "modifieddate": datetime.datetime.utcnow()
        }

        # Adds it :)
        post_id = collection.insert_one(data).inserted_id

        # This ID sucks.
        self.ip_cnt += 1
        return post_id

    def get_data(self):
        return open("blocklist.php", "r").readlines()

    def generate_test_data(self):
        ips = []
        ip = "192.168.0."
        for i in range(0, 254):
            ips.append(ip+str(i))

        return ips

    def test_func(self):
        db = self.mongoclient.ip
        #testdata = self.generate_test_data()
        testdata = self.get_data()
        category = "c2"
        name = "zeus"

        self.clear_collection(db.ips)
        
        cnt = 0
        # Generate other data first to append to the IP-range
        for ip in testdata:
            if self.add_new_ip(db, db.ips, ip, category=category, name=name, id=cnt):
                cnt += 1

        if cnt > 0:
            print "Added %d elements to %s" % (cnt, "ips")
        else:
            print "All data already in database."

        for items in self.print_data(db.ips):
            print items
            exit()


if __name__ == "__main__":
    #app.run(debug=True)
    mongodbserver = '172.28.3.163'
    mongodbport = 27017
    print "Connecting to mongodb at %s:%d" % (mongodbserver, mongodbport)

    client = database_handler(mongodbserver, mongodbport)
    client.test_func()
