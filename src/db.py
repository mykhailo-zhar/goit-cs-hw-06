import os

from pymongo import MongoClient
from pymongo.server_api import ServerApi


def create_mongo_connection():
    """Create a MongoDB client and return the cats database.

    Credentials are read from MONGODB_USER, MONGODB_PASSWORD, MONGODB_HOST,
    and MONGODB_APPNAME.
    """
    client = MongoClient(
        "mongodb+srv://{username}:{password}@{host}?appName={db}&retryWrites=true&w=majority".format(
            username=os.environ.get("MONGODB_USER"),
            password=os.environ.get("MONGODB_PASSWORD"),
            host=os.environ.get("MONGODB_HOST"),
            db=os.environ.get("MONGODB_APPNAME"),
        ),
        server_api=ServerApi("1"),
    )
    db = client.messages
    return db
