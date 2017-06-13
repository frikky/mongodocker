import os 
import json
import requests
from pymongo import MongoClient
from mongodb import database_handler

# Data handler for the flask server
class correlate_data(database_handler):
    def __init__(self, ip, port):
        self.database = database_handler(ip, port)

    # Returns error messages
    def default_error(self, data="", path=""):
        if not data or not path:	
            return {'error': 'Can\'t find the information you\'re looking for'}

        return {'error': 'Can\'t find %s in collection %s' % (data, path)}

    # Do mongodb searches and stuff. 
    # IP/URL/HASH > 
    def get_data(self, ip_db, url_db, hash_db, path, data):
        resp = ""

        # Add url and ip
        ### FIX
        if path == "ip":
            resp = self.database.find_object(ip_db["ip"], data)
        elif path == "url":
            resp = self.database.find_object(url_db["url"], data)
        elif path == "hash":
            resp = self.database.find_object(hash_db["hash"], data)

        # Verifies after basic categories 
        # Can be verified here? Attempt URL, Hash and URL lookup -> Use in if
        if resp:
            return resp

        # Check if name in category exists > IP exists.
        resp = self.database.find_category_data(\
            self.database.mongoclient["category"][path], data)

        categories = self.database.get_available_category_collections()
        # Needs reverse path check to IP, URL or HASH.
        if path in categories and not resp:
            category_collection = self.database.mongoclient["category"][path]

            # Matches category
            resp = self.database.find_object(self.database.mongoclient["category"][path], data)

            # Find IP/URL etc, lookup mognodb ID, find it and return
            # Validate if ip, url or hash with regex?

            if not resp:
                resp = self.database.find_object(ip_db["ips"], data)

            if resp is None:
                return self.default_error(path, resp)

            if isinstance(resp, dict):
                for item in resp["containers"]:
                    if item["category"] == path:
                        cur_id = item["mongo_id"]	
                        break

        if resp is None or not resp:
            return self.default_error(path, resp)

        return resp 

    # Return filelocation
    def download_file(self, category, name, type, download_location):
        filename = "%s_%s_%s" % (category, name, type)
         
        r = requests.get(download_location, stream=True)
        with open(filename, 'wb') as tmp:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    tmp.write(chunk)

        return filename

    # Creates folder
    def create_folder(self, path):
        os.mkdir(path)

    # Can deduce category from filename
    # Moves file to appropriate location
    def move_file(self, filename, category, location):
        try:
            os.rename(filename, "%s/%s/%s" % (location, category, filename))
        except OSError:
            self.create_folder("%s/%s" % (location, category))
            os.rename(filename, "%s/%s/%s" % (location, category, filename))

        return True

    # Hardcoded for IPs in Zeus
    ###### FIX!!! - Might make it a standard.
    def format_data(self, filepath, filter=""):
        if not filter:
            with open(filepath, "r") as tmp:
                cur_data = [x[:-1] for x in tmp.readlines() if x and \
                    not x.startswith("#") and len(x) > 1]

        return cur_data

    # Adds a list of x to the correct db
    def add_data_to_db(self, data, type, category, name):
        # Uhm what
        db = self.database.mongoclient.ip
        category_db = self.database.mongoclient.category
    
        cnt = 0
        for item in data:
            if self.database.add_data(db, db[type], category_db, item, category=category, name=name):
                cnt += 1

        if cnt:
            print "Added %d items to db." % cnt
        else:
            print "Added nothing to db."
                

    # Reads config and downloads stuff
    # Maybe try not working with files at all, use direct request feedback?
    def read_config(self):
        # FIX -- Remove ..
        cwd = os.getcwd()
        config = "%s/../config/config.json" % cwd
        tmp_location = "%s/../tmp_data" % cwd

        json_data = json.load(open(config, 'r'))
        
        # Should use full paths.
        # Maybe try not working with files at all, use direct request feedback?

        # Lmao, this is garbage
        for item in json_data:
            if not os.path.isfile("%s/%s/%s" % (tmp_location, item["category"], \
                "%s_%s_%s" % (item["category"], item["name"], item["type"]))):

                file = self.download_file(item["category"], \
                    item["name"], item["type"], item["base_url"])
                data = self.move_file("%s_%s_%s" % (item["category"], \
                    item["name"], item["type"]), item["category"], tmp_location)

            formatted_data = self.format_data("%s/%s/%s" % (tmp_location, item["category"], \
                ("%s_%s_%s" % (item["category"], item["name"], item["type"]))))
            self.add_data_to_db(formatted_data, item["type"], item["category"], item["name"])

if __name__ == "__main__": 
    find_data = correlate_data("127.0.0.1", 27017)
    
    #find_data.add_data_to_db(["192.168.0.1"], "ip", "phish", "phishtank")
    #hello = find_data.database.return_collection(find_data.database.mongoclient.ip.ip)

    # Generates all of config file
    find_data.read_config()
