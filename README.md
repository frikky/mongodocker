# MongoDB docker
MongoDB and rest API to use as threat intel for different SI(E)Ms. Addon for QRadar is available in Intelligencefeed. Needs implementation with mongoDB thoo

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

# MongoDB logic
|client| -> webserver API -> mongoDB -> webserver -> |client|

[GET]:
e.g. IP 192.168.1.0 is categorized as a bot C&C:

https://192.168.1.0/ip/\<ip\>
Return:
        data = {
            "ip": "192.168.1.0"
            "id": counter?
            "containers": [{
				"category": "c2", 		# IP is part of a Bot C&C
				"name": zeus, 			# IP was found in the zeus logs	
				"id": aksdjalskjdalkj 	# Databsae ID for quicker lookups
	    }],
            "addeddate": datetime.datetime.utcnow(),
            "modifieddate": datetime.datetime.utcnow()
        }

[POST]:
Add an IP to the bot C&C db
https://192.168.1.0/ip/\<ip\>

headers={"auth": "TOKENHERE"}
data={"name": "zeus", "category": "c2", "ip": \<ip\>}

Data will then be added to \<ip\> and the zeus database under category c2.

# Configs
The data will have to have two seperate collections. One cleaned and updated every day, and one with continuous updates.
