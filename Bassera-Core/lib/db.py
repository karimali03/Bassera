from pymongo import MongoClient
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

db = None

def get_mongo_client():
    global db
    if db is None:
        uri = os.environ.get('MONGODB_ATLAS_URI')
        import certifi
        db = MongoClient(uri, appname="bassera-core", tlsCAFile=certifi.where())['BasseraDB']
    return db

def get_collection(collection_name):
    if db is None:
        get_mongo_client()
    return db[collection_name]
