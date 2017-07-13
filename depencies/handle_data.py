import os 
import re
import json
import time
import requests
from pymongo import MongoClient
from mongodb import database_handler

# Data handler for the flask server
class correlate_data(database_handler):
    def __init__(self, ip, port):
        self.database = database_handler(ip, port)
        self.timestampcheck = 12

    # Returns error messages
    def default_error(self, data="", path=""):
        if not data or not path:	
            return {'error': 'Can\'t find the information you\'re looking for'}

        return {'error': 'Can\'t find %s in collection %s' % (data, path)}

    # Do mongodb searches and stuff. 
    # IP/URL/HASH > 
    # This is garbage. Redo it all \o/
    def get_data(self, ip_db, url_db, hash_db, path, data):
        resp = ""
        cur_db = ""

        # Add url and ip
        ### FIX
        if path == "ip":
            cur_db = ip_db["ip"]
        elif path == "url":
            cur_db = url_db["url"]
        elif path == "hash":
            cur_db = hash_db["hash"]

        if cur_db:
            resp = self.database.find_object(cur_db, path, data)

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
            resp = self.database.find_object(self.database.mongoclient["category"][path], path, data)

            # Find IP/URL etc, lookup mognodb ID, find it and return
            # Validate if ip, url or hash with regex?
            # Most likely something wrong. Try /malware/asdasd
            if not resp:
                try:
                    resp = self.database.find_object(cur_db, path, data)
                except AttributeError:
                    pass

            if resp is None:
                return self.default_error(path, resp)

            if isinstance(resp, dict):
                for item in resp["containers"]:
                    if item["category"] == path:
                        cur_id = item["mongo_id"]	
                        break

        # ADD SHIT HERE
    
        if resp is None or not resp:
            return self.default_error(path, resp)

        return resp 

    def download_file_new(self, category, name, type, download_location):
        #filename = "%s_%s_%s" % (category, name, type)
        print "Downloading %s" % download_location
         
        # In case of no internet or stuff
        try:
            r = requests.get(download_location, stream=True, timeout=10)
        except (
            requests.exceptions.SSLError, 
            requests.exceptions.ReadTimeout, 
            requests.exceptions.ConnectionError
        ):
            return False

        return r.text

    # Hardcoded for IPs in Zeus
    ###### FIX!!! - Might make it a standard.
    # Can use the Golang script for the parsing here.
    def format_data(self, filepath, filter=""):
        if not filter:
            with open(filepath, "r") as tmp:
                cur_data = [x[:-1] for x in tmp.readlines() if x and \
                    not x.startswith("#") and len(x) > 1]

        return cur_data

    # Check if list or single IP :) - FIX, dont have to load regex on every request
    def verify_ip(self, type, data):
        if type == "ip":
            pattern = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
        # Only allows sha256 for now.
        elif type == "hash":
            pattern = "([A-Fa-f0-9]{64})"

        pattern = re.compile(pattern)

        if isinstance(data, list):
            ip_list = []
            for item in data:
                if pattern.match(item) is not None:
                    ip_list.append(item)

            # Return here
            return ip_list

        if pattern.match(data) is not None:
            return data 

        return False

    def verify_post_data(self, type, data, category, name):
        # FIX
        # Make category global to reduce load for every request
        all_categories = [item for item in self.database.get_available_category_collections()]
        if category.lower() not in all_categories:
            {"error": "Category %s doesn't exist and is therefore not permitted." % category}
            return False

        verification = self.verify_ip(type, data)
        if not verification:
            return False

        # Add data after all checks have been done
        ## FIX - check size of list. Can't handle too big requests
        # If single IP, do lookup at the same time (thread)
        if isinstance(verification, list):
            for item in verification:
                self.add_data_to_db(item, type, category, name)
            return {"result": "%d %ss added to the db." % (len(verification), type)}
        else:
            self.add_data_to_db(item, type, category, name)
            return {"result": "1 %s added to the db." % type}


    # Add kwargs to be able to add url and stuff as well. Comment maybe?
    def add_data_to_db(self, data, type, category, name):
        if type == "ip":
            db = self.database.mongoclient.ip
        elif type == "url":
            db = self.database.mongoclient.url
        elif type == "hash":
            db = self.database.mongoclient.hash

        category_db = self.database.mongoclient.category
    
        if isinstance(data, list):
            cnt = 0
            for item in data:
                if self.database.add_data(db, db[type], category_db, \
                    type, item, category=category, name=name):
                    cnt += 1

            ## FIX
            if cnt:
                print "Added %d items to %s db with category %s." % \
                    (cnt, type, category)
            else:
                print "Added nothing to db %s db with category %s." % \
                    (type, category)
        else:
            self.database.add_data(db, db[type], category_db, type, data, \
                category=category, name=name)

    # FIX - Format data properly
    def format_data_new(self, data):
        arr = []
        for item in data.split("\n"):
            if item.startswith("#") or len(item) < 2: 
                continue
           
            # Only takes a plain list
            arr.append(item)

        return arr
            
    # Handles modular data being used
    # Seems to be a working demo PoC \o/
    # FIX -- Test if the 12 hour timestamp works.
    def read_config_new(self):
        # FIX -- Remove ..
        cwd = os.getcwd()
        config = "%s/config/config.json" % cwd

        try:
            json_data = json.load(open(config, 'r'))
        except IOError:
            config = "%s/../config/config.json" % cwd  
            json_data = json.load(open(config, 'r'))

        # Check for timestamp in json
        # Write timestamp download timestamp back to config file
        # Format data the right way (make new format_data)
        # Push to add_data_to_db_new (or skip this step and straight to add data

        new_json_file = []

        for item in json_data:
            # Refresh if 12 hours ago
            try:
                if item["lastedited"] < (self.timestampcheck+43200):
                    new_json_file.append(item)
                    continue
            except KeyError:
                item["lastedited"] = 0
                
            # Downloads and returns the data available
            data = self.download_file_new(item["category"], \
                item["name"], item["type"], item["base_url"])

            if not data:
                new_json_file.append(item)
                continue

            # DO STUFF HERE
            formatted_data = self.format_data_new(data)

            timestamp = int(time.time())
            item["lastedited"] = timestamp
            new_json_file.append(item)

            # Now add the freaking data
            db = self.database.mongoclient[item["type"]] 
            self.database.add_data_new(db, item["type"], \
                formatted_data, item["category"], item["name"])

        print "WRITING BACK TO FILE"
        with open(config, 'w+') as tmp:
            json.dump(new_json_file, tmp, indent=4)

    # Reads config and downloads stuff
    # Keep this function for testing purposes. Check __name__ main at bottom
    # (Based on no internet connection) 
    def read_config(self):
        cwd = os.getcwd()
        config = "%s/config/config.json" % cwd

        # FIX
        # Make it only run in memory, no local save.
        tmp_location = "%s/tmp_data" % cwd

        # Verifies if it's ran as main or not
        try:
            json_data = json.load(open(config, 'r'))
        except IOError:
            config = "%s/../config/config.json" % cwd  
            tmp_location = "%s/../tmp_data" % cwd
            json_data = json.load(open(config, 'r'))
        
        for item in json_data:
            check_file = "%s/%s/%s" % (tmp_location, item["category"], \
                    "%s_%s_%s" % (item["category"], item["name"], item["type"]))

            formatted_data = self.format_data(check_file)
            self.add_data_to_db_new(formatted_data, item["type"], item["category"], item["name"])

    # Checks what the regex matches
    def regex_check(self, data):
        if re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', data):
            return "ip"
        elif re.match('^([A-Fa-f0-9]{64})', data):
            return "hash"
        elif re.match('^([a-f0-9]{32})', data):
            return "hash"
        elif re.match('[^@]+@[^@]+\.[^@]+', data):
            return "mail"
        else:
            return "url"

if __name__ == "__main__": 
    find_data = correlate_data("127.0.0.1", 27017)
    
    # Tests a single
    """
    db = find_data.database.mongoclient.ip
    data_type = "ip"
    item = ["185.28.100.99", "192.168.0.1"]
    category = "testing"
    name = "virustotal"
    find_data.add_data_new(db, data_type, item, category, name)
    """

    ips = find_data.database.get_available_ip_collections()
    biggestnumber = 0
    biggest_name = 0

    for item in ips:
        count = find_data.database.mongoclient.ip[item].find({}).count()
        if count > biggestnumber:
            biggestnumber = count
            biggest_name = item

    for items in find_data.database.mongoclient.ip[biggest_name].find({}):
        print items["ip"]
        print


    #find_data.read_config()
    #find_data.read_config_new()
    #for items in item:
    #    print find_data.find_object_new(data_type, items)
