# MongoDB docker
MongoDB and REST API to use as a Threat Intel framework for different SI(E)Ms. Addon for QRadar is available in Intelligencefeed. It's basically an attempt at a proper implementation compared to the in Intelligencefeed github repo.

# Current usage
1. Install Docker.
2. Run the mongodb\_scripts/build.sh file.
3. Run the mongodb\_scripts/run.sh file.
4. Change IP in flask/server.py to point to host running docker instance (top). Default to localhost.
5. Run python server.py 
6. Go to localhost:5000

# Config
This is where the data is handled. Will add more data soon, and do some test runs of different categories etc. before locking it down. Run handle\_data.py to regenerate data from config file.

# Data storing
For now, while testing, all the data collected from config/config.json is stored in tmp\_data.

# Clearing the DB
There are currently three ways that all work well:
1. Restart docker container (It's not gonna run in docker soonish)
2. Run "python mongodb.py clear"
3. Start the webserver and go to localhost/clear

All of these will clear the entire database. 

# Done from todo
* Add logic for IP
* Make search work better (faster)
* Make proper category lookup work. 

# Todo? 
* Add logic for URL and HASH (Dupe IP for now)
* Apparently I some stuff was killed in the process of creating new ones. ITS A FEATURE
* Add logging
* Make it able to automatically add data to the DB. On demand load or timebased? - Starting with on demand - Almost done - needs to use a refreshtime or similar.
* Add extensions management and script management for parsing of external sources. Most likely their own config files.
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
