# MongoDB docker
Testing mongoDB in docker for storage later

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
		"category": "c2", 	# IP is part of a Bot C&C
		"name": zeus, 		# IP was found in the zeus logs	
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
