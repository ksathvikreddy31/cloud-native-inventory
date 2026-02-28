import os
import time
from pymongo import MongoClient

# Use environment variable to dynamically switch between 'localhost' or 'mongo' (docker)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

# Use a timeout so it doesn't hang indefinitely if the DB is down
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

# Access the database
mongo_db = client.inventory 

# Test the connection stringently with a retry loop to prevent WinError 10038 early disconnections
retries = 5
while retries > 0:
    try:
        client.admin.command('ping')
        print("MongoDB connected successfully!")
        break
    except Exception as e:
        print(f"MongoDB connection failed: {e}. Retrying in 3 seconds...")
        retries -= 1
        time.sleep(3)