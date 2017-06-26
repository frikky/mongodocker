# MongoDB docker
MongoDB and REST API to use as a Threat Intel framework for different SI(E)Ms. Addon for QRadar is available in Intelligencefeed. It's basically an attempt at a proper implementation compared to the in Intelligencefeed github repo.

# Current usage
1. Install Docker.
2. Run the mongodb\_scripts/build.sh file.
3. Run the mongodb\_scripts/run.sh file.
4. Change IP in flask/server.py to point to host running docker instance (top). Default to localhost. (Should be in config file)
5. Run python server.py (Via docker or not) 
6. Go to localhost:80

# Config
This is where the data is handled. Will add more data soon, and do some test runs of different categories etc. before locking it down. Run handle\_data.py to regenerate data from config file.

# Local data storing
For now, while testing, all the data collected from config/config.json is stored in tmp\_data.

# Clearing the DB
There are currently three ways that all work well:
1. Restart docker container (It's not gonna run in docker soonish)
2. Run "python mongodb.py clear"
3. Start the webserver and go to localhost/clear

All of these will clear the entire database. 

# Adding data
Currently there are plans for three different ways of adding data:
* config file  	- cronjob for calling depencies/handle\_data.read\_config
* external 		- posting to localhost/80 using a specific call. Supports bulk but not kwargs yet.
* manual		- Using the function depencies/handle\_data.add\_data\_to\_db

# Done from todo
* Add logic for IP, URL, hashes and categories 
* Make proper category lookup work. ~ish
* Make search work more dynamic (Can continue this)
* Make config file work properly.
* Make it able to automatically add data to the DB. POST requests implemented (see above). Missing Docker implementation
* Add docker configuration for the flask server, and remove for mongodb. Only used now for fast cleanups.
* A plain search site (GUI) 

# Todo? 
* Fix bottleneck for adding large amounts of data. 
* Add logging
* Add extensions management and script management for parsing of external sources. Most likely their own config files.
* Better iterator to see if items already exist. Loop before > while. Will need to remake some functions. Might not be necessary as mongodb already checks. Same as first part of todo.

*** When above is done
* Filter what data to return (json > bson). (No object IDs)
* Start using API tokens both in the database and the flask server. Not a rush as it's ran locally per now. (Done a stupid attempt with flask that doesn't work :)))))))
* Try hosted solution - Proper config webserver and mongoDB setup required. See Security below.
* More config-possibilites \o/ - More than the adding data chapter shows.
* Finish up readme and stuff

# Security
Set HTTP(S) header 				 - refer to owasp
Setup API authentication (flask) - Not sure how to implement it yet. Most likely static config file.
Open specific ports in firewall. - IPTables config

# Logic
|client| -> webserver API -> mongoDB -> webserver -> |client|

[GET]:
e.g. IP 192.168.0.1 is categorized as a bot C&C:

https://127.0.0.1:5000/ip/192.168.0.1

        {
            "ip": "192.168.1.0",
            "id": "some_id",
            "containers": [{
				"category": "c2", 
				"name": zeus, 			
				"id": asdasdasd			
	    }],
            "addeddate": datetime.datetime.utcnow(),
            "modifieddate": datetime.datetime.utcnow()
        }

*** The above can also be done towards e.g. c2/ip or phishing/ip, depending what collections exist.

[POST]:
Add an IP (192.168.0.1 here) to the bot C&C db
https://127.0.0.1:5000/ip/192.168.0.1

headers={"auth": "TOKENHERE"}<br>
data={"name": "zeus", "category": "c2", "type": "ip", "data": \<ip\>}<br>

Data will then be added to \<ip\> and the c2 database under name zeus.
Not sure about response yet.
