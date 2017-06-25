import json
import tweepy

# ADD DATA
consumer_key=
consumer_secret=
access_token=
access_token_secret=

class Listener(tweepy.Streamlistener):
    def data(self, data):
        decoded = json.loads(data):

        print decoded
        return True

    def error(self, status):
        print status

if __name__ == "__main__":
    listen = Listener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Create stream 
    stream = tweepy.Stream(auth, listen)

    # Do something with stream here
