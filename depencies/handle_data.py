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

    # Do mongodb stuff
    def get_data(self, ip_db, url_db, hash_db, path, data):
        resp = ""

        # Add url and ip
        if path == "ip":
            resp = self.database.find_object(ip_db["ips"], data)

        # Verifies after basic categories 
        # Can be verified here? Attempt URL, Hash and URL lookup -> Use in if
        if resp:
            return resp

        categories = self.database.get_available_category_collections()

        # Check if name in category exists > IP exists.
        resp = self.database.find_category_data(\
        self.database.mongoclient["category"][path], data)

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
    def download_file(self, category, name, download_location):
        filename = "%s_%s" % (category, name)
         
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
    ###### FIX!!!
    def format_data(self, filepath):
        with open(filepath, "r") as tmp:
            cur_data = [x[:-1] for x in tmp.readlines() if x and not x.startswith("#") and len(x) > 1]

        return cur_data

    """
    def add_data_to_db(self, data, type, category, name):
        # Uhm where 
        self.database.add_data(

    #def add_data(self, database, ip_collection, category_db, ip, category="", name=""):

    #def add_data(self, database, ip_collection, category_db, ip, category="", name=""):

        self.add_new_data(
        self.database.add_new_ip(
    """

        
    # Reads config and downloads stuff
    # Maybe try not working with files at all, use direct request feedback?
    def read_config(self):

        # FIX -- Remove ..
        cwd = os.getcwd()
        config = "%s/../config/config.json" % cwd
        tmp_location = "%s/../tmp_data" % cwd

        json_data = json.load(open(config, 'r'))
        
        intelnames = [item["name"] for item in json_data]
        intelcategories = [item["category"] for item in json_data]

        # Should use full paths.
        # Maybe try not working with files at all, use direct request feedback?
        # Uncomment :D

        for item in json_data:
            #IF ITEM DOESNT EXIST, DO:
            if not os.path.isfile("%s/%s" % (tmp_location, item["filename"])):
                #file = self.download_file(item["category"], \
                    #item["name"], item["base_url"])
                #data = self.move_file("%s_%s" % (item["category"], \
                    #item["name"]), item["category"], tmp_location)
                formatted_data = self.format_data("%s/%s/%s" % (tmp_location, item["category"], \
                    ("%s_%s" % (item["category"], item["name"]))))
                #self.add_data_to_db(formatted_data, item["type"], item["category"], item["name"])

                # Format data? 
                #Check database first?

            exit()
        # Remove file?
              
        print intelnames 
        

    def generate_data(self):
        self.read_config()
        return False
        # Read data from config
        db = self.database.mongoclient.ip
        category_db = self.database.mongoclient.category

        ip = "192.168.0.1\n"
        category = "c2"
        name = "zeus"

        # Generate other data first to append to the IP-range
        ip = ip[:-1]
        data = self.database.add_data(db, db.ips, category_db, ip, \
                category=category, name=name)

        return data

if __name__ == "__main__":
    find_data = correlate_data("127.0.0.1", 27017)
    find_data.read_config()
