import datetime
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

# Database structure. Name can be random
db = client.test_database

# Collection within a db. Basically categories/tables.

post = {
    "author": "Frikky",
    "text": "Testing stuff",
    "tags": ["mongodb", "python", "pymongo"],
    "date": datetime.datetime.utcnow()
}

posts = db.posts

post_id = posts.insert_one(post).inserted_id

# Iters all documents
for document in posts.find({}):
    print document

## Needed functions:
# Remove
# Bulk add
# Edit

## Other things:
# Data even when docker container doesn't exist. Offload data location. That means the folder /data/db from the Dockerfile.
# Data backup
