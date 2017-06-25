import os
import sys
import json
import requests
import config as cfg

from handle_data import correlate_data

class virustotal(object):
    def __init__(self, hash):
        self.vttoken = cfg.virustotal 
        self.hash = hash

    def check_vt(self):
        params = {
            'apikey': '%s' % self.vttoken, 
            'resource': '%s' % self.hash
        }

        headers = {
            "Accept-Encoding": "gzip, deflate",
            "User-Agent" : "gzip,  verify_python"
        }

        response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', 
        params=params, headers=headers)

        if response.status_code == 200:
            self.injest(data=response.json())
        
        return False 

    def injest(self, data=""):
        if not data:
            with open("data", "r") as tmp:
                data = json.load(tmp)

        # Indicates if an error occured.
        try:
            positives = data["positives"]
        except KeyError:
            return False

        # Direct or via post requests? Idk.
        if positives > 0:
            class_handler = correlate_data("0.0.0.0", 27017)
            class_handler.add_data_to_db(self.hash, "hash", "malware", "virustotal")

        # Convert to sha256 in case of md5

if __name__ == "__main__":
    vt = virustotal(sys.argv[1])
    data = vt.check_vt()
