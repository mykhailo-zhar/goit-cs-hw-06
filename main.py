import logging
import os
from multiprocessing import Process

from src.http_server import run
from src.socket_server import run_server


def main():
    run()


if __name__ == "__main__":
    pr = None

    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(levelname)s\t%(name)s\t%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    if os.environ.get("SOCKET_SERVER_DEPENDANT"):
        print("Starting socker server")
        pr = Process(
            target=run_server,
            args=(
                os.environ.get("SOCKET_MESSAGE_HOST", "127.0.0.1"),
                int(os.environ.get("SOCKET_MESSAGE_PORT", "5000")),
            ),
        )
        pr.start()

    main()

    if pr:
        pr.join()
