import os

from pymongo import MongoClient


def get_mongo_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    return client.get_database(name="galapagos")


def insert_seaplanes(seaplanes):
    db = get_mongo_db()
    db.seaplanes.insert_many(seaplanes)


def insert_lockers(lockers):
    db = get_mongo_db()
    db.lockers.insert_many(lockers)
