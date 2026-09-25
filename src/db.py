import os

from pymongo import MongoClient
from pymongo.server_api import ServerApi


def create_mongo_connection():
    """Create a MongoDB client and return the cats database.

    Credentials are read from MONGODB_USER, MONGODB_PASSWORD, MONGODB_HOST,
    and MONGODB_APPNAME.
    """
    port = os.environ.get("MONGODB_PORT")
    app_name = os.environ.get("MONGODB_APPNAME")

    db = f"appName={app_name}" if app_name else ""

    if not os.environ.get("MONGODB_NOSERV"):
        connection_string = "mongodb+srv://{username}:{password}@{host}?{db}retryWrites=true&w=majority".format(
            username=os.environ.get("MONGODB_USER"),
            password=os.environ.get("MONGODB_PASSWORD"),
            host=os.environ.get("MONGODB_HOST"),
            db=db,
        )
    else:
        connection_string = "mongodb://{username}:{password}@{host}{port}?{db}directConnection=true".format(
            username=os.environ.get("MONGODB_USER"),
            password=os.environ.get("MONGODB_PASSWORD"),
            host=os.environ.get("MONGODB_HOST"),
            db=db,
            port=f":{port}" if port else "",
        )

    client = MongoClient(
        connection_string,
        server_api=ServerApi("1"),
    )
    db = client.messages
    return db
