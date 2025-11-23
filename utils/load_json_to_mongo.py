import os
import json
from pymongo import MongoClient

# Config do Mongo (pega default do docker compose se não tivermos no env)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://imoveis:imoveis@mongo:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "imoveis_db")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "imoveis")

_mongo_client = MongoClient(MONGO_URI)


def save_elements_to_mongo(json_name: str) -> None:
    with open(json_name, "r", encoding="utf-8") as f:
        docs = json.load(f)
    if not docs:
        return

    _mongo_collection = _mongo_client[MONGO_DB_NAME]["data_base_imoveis"]
    _mongo_collection.insert_many(docs)
