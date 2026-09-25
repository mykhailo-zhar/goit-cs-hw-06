import json
import os
import socket
import time
from datetime import UTC, datetime
from functools import wraps
from threading import Thread
from typing import Any

from pymongo.errors import PyMongoError
from pymongo.synchronous.database import Database

if __name__ == "__main__":
    from db import create_mongo_connection
else:
    from src.db import create_mongo_connection


import logging

logger = logging.getLogger()


def pymongo_error_message(e: PyMongoError):
    """Build a human-readable message from a PyMongo exception.

    :param e: exception raised by a MongoDB operation
    :return: formatted error string
    """
    return f"Error when executing the query: {e}"


def error_decorator(func):
    """Wrap a MongoDB operation and print PyMongoError instead of crashing.

    :param func: function that performs a database operation
    :return: wrapped function with the same name and docstring
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Run the wrapped function and catch PyMongo errors."""
        try:
            return func(*args, **kwargs)
        except PyMongoError as e:
            logger.error(pymongo_error_message(e))

    return wrapper


@error_decorator
def create_message(db: Database, data: dict[str, Any]):
    """Insert randomly generated cat documents into the cats collection.

    :param db: MongoDB database that contains the cats collection
    :param num: number of cat documents to create
    """

    username, message = data.get("username", None), data.get("message", None)
    if not username or not message:
        logger.warning("No user to save")

    logger.info("Writing to mongodb")
    result = db.messages.insert_one(
        {
            "date": datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "username": username,
            "message": message,
        }
    )
    logger.info("Result: %s with inserted_id = %s", result, result.inserted_id)
    return result.inserted_id


@error_decorator
def print_found_message(db: Database, id):
    time.sleep(5)
    logger.info(
        "The message in remote host: %s for id = %s",
        db.messages.find_one({"_id": id}),
        id,
    )


def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    logger.info("Starting server. Host: %s on socket %d", ip, port)
    sock.bind(server)
    con = create_mongo_connection()

    threads = []
    try:
        while True:
            data, address = sock.recvfrom(1024)
            result = data.decode()

            if result == "END":
                logger.info("Stopping server due to http server request")
                break

            data_dict = json.loads(result)
            logger.info(f"Received data: {data_dict} from: {address}")

            id = create_message(con, data_dict)

            tr = Thread(target=print_found_message, args=(con, id))
            tr.start()
            threads.append(tr)

    except KeyboardInterrupt:
        logger.info("Destroy server")
    finally:
        sock.close()
        for tr in threads:
            tr.join()


if __name__ == "__main__":
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(levelname)s\t%(name)s\t%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    run_server(
        os.environ.get("SOCKET_MESSAGE_HOST", "127.0.0.1"),
        int(os.environ.get("SOCKET_MESSAGE_PORT", "5000")),
    )
