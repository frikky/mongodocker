import os
import sys
import json
import requests
import config as cfg

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
            return response.json()
        
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
            request_data={"type": "hash", "data": data, "category": "malware", "name": "virustotal"}
            resp = requests.post("%s/" % cfg.target, headers={"auth": cfg.API_KEY}, \
                json=request_data, verify=False)

if __name__ == "__main__":
    vt = virustotal(sys.argv[1])
    data = vt.check_vt()
    vt.injest(data=data)
