# MongoDB docker
MongoDB and rest API to use as threat intel for different SI(E)Ms. Addon for QRadar is available in Intelligencefeed. Needs implementation with mongoDB thoo

# Current usage
1. Install Docker.
2. Run the mongodb\_scripts/build.sh file.
3. Run the mongodb\_scripts/run.sh file.
4. Change IP in flask/server.py to point to host running docker instance (top). Default to localhost.
5. Run python server.py 
6. Go to localhost:5000

# Todo? 
* Add logic option for json or raw format (not xml :)). Depends whats the best.
* Add logic for URLs and hashes. 
* Make proper category lookup work. 
* Add extensions management and script management for parsing of external sources.
* Add docker configuration for the flask server, and remove for mongodb. Only used now for fast cleanups.
* Make it able to automatically add data to the DB. On demand load or timebased?

*** When above is done - Create 
* Start using API tokens both in the database and the flask server. Not a rush as it's ran locally per now. 
* Go away localhost :^)
* More config ability \o/

# Logic
|client| -> webserver API -> mongoDB -> webserver -> |client|

[GET]:
e.g. IP 192.168.0.1 is categorized as a bot C&C:

https://127.0.0.1:5000/ip/192.168.0.1
Return:
        {
            "ip": "192.168.1.0",
            "id": "some_id",
            "containers": [{
				"category": "c2", 		# IP is part of a Bot C&C
				"name": zeus, 			# IP was found in the zeus logs	
				"id": asdasdasd			# Database ID for quicker lookups
	    }],
            "addeddate": datetime.datetime.utcnow(),
            "modifieddate": datetime.datetime.utcnow()
        }

*** The above can also be done towards e.g. c2/ip or phishing/ip, depending what collections exist.

[POST]:
Add an IP (192.168.0.1 here) to the bot C&C db
https://127.0.0.1:5000/ip/192.168.0.1

headers={"auth": "TOKENHERE"}
data={"name": "zeus", "category": "c2", "ip": \<ip\>}

Data will then be added to \<ip\> and the c2 database under name zeus.
Not sure about response yet.

# Configs
The data will have to have two seperate collections. One cleaned and updated every day, and one with continuous updates. Also, see usage.
