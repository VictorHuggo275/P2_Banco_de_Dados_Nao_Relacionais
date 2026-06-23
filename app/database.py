from pymongo import MongoClient

from app.config import Settings

settings = Settings.from_env()

client = MongoClient(settings.mongodb_url)

database = client[settings.mongodb_database]

pedidos_collection = database[settings.mongodb_collection]
