import re
import json
import tweepy
import requests
import config as cfg

pattern = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"

pattern = re.compile(pattern)

class StreamListener(tweepy.StreamListener):
    # Finds the IP in tweet
    def verify_ip(self, data):
        for item in data.split(" "):
            if pattern.match(item) is not None:
                return item 

        return False

    def on_data(self, data):
        decoded = json.loads(data)
        data = self.verify_ip(decoded["text"])

        if not data:
            return True

        request_data={"type": "ip", "data": "%s" % data, "category": "malware", "name": "scan"}
        resp = requests.post("%s/" % cfg.target, headers={"TOKEN": cfg.local_api_token}, \
            json=request_data, verify=False)

        return True

if __name__ == "__main__":
    listen = StreamListener()
    auth = tweepy.OAuthHandler(cfg.consumer_key, cfg.consumer_secret)
    auth.set_access_token(cfg.access_token, cfg.access_token_secret)

    # Create stream 
    stream = tweepy.Stream(auth, listen)

    # Credits to da_667 for this one. Users from his threat_tracking list
    users = [
        '718473978', 
        '2274861307', 
        '168692722', 
        '3248301079',
        '3365894273',
        '1525937365',
        '18087706'
    ]
    
    # Do something with stream here
    stream.filter(follow=users, async=True)
