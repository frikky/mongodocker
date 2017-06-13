# MongoDB docker
MongoDB and rest API to use as threat intel for different SI(E)Ms. Addon for QRadar is available in Intelligencefeed. It's basically a proper database compared to the PoC in the Intelligencefeed github repo.

# Current usage
1. Install Docker.
2. Run the mongodb\_scripts/build.sh file.
3. Run the mongodb\_scripts/run.sh file.
4. Change IP in flask/server.py to point to host running docker instance (top). Default to localhost.
5. Run python server.py 
6. Go to localhost:5000

# Config
This is where the data is handled. Will add more data soon

# Data storing
For now, while testing, all the data collected from connfig/config.json is stored in tmp\_data.

# Done from todo
* Add logic for IP, URLs and hashes. 
* Make search work-ish
* Make proper category lookup work. 

# Todo? 
* Make it able to automatically add data to the DB. On demand load or timebased? - Starting with on demand
* Add extensions management and script management for parsing of external sources.
* Better iterator to see if items already exist. Loop before > while. Will need to remake some functions.

*** When above is done
* Filter what data to return.
* Add docker configuration for the flask server, and remove for mongodb. Only used now for fast cleanups.
* Start using API tokens both in the database and the flask server. Not a rush as it's ran locally per now. 
* Try hosted solution - Proper HTTPS config and MongoDB security
* A plain search site (GUI) 
* More config-possibilites \o/
* Finish up readme and stuff

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
