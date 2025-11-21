from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database(os.getenv("MONGO_DB_NAME"))
print(db.list_collection_names())