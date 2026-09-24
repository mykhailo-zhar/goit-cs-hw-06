import json
import mimetypes
import os
import socket
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PUBLIC_PATH = Path(__file__).resolve().parents[1] / "public"

SERVER = (
    os.environ.get("SOCKET_MESSAGE_HOST", "127.0.0.1"),
    int(os.environ.get("SOCKET_MESSAGE_PORT", "5000")),
)


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.__parse_path()
        self.__POST_routes()

    def do_GET(self):
        self.__parse_path()
        self.__GET_routes()

    def send_through_socket(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.log_message("Sending data to socket %d on server %s", SERVER[1], SERVER[0])

        sock.sendto(data, SERVER)
        sock.close()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(PUBLIC_PATH / filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()

        with open(self.__get_static_path(), "rb") as file:
            self.wfile.write(file.read())

    def __GET_static(self):
        static_path = self.__get_static_path()
        if static_path.exists() and not self.parsed_path.endswith(".html"):
            self.send_static()
        else:
            self.send_html_file("error.html", 404)

    def __GET_routes(self):
        match self.parsed_path:
            case "/":
                self.send_html_file("index.html")
            case "/index":
                self.send_html_file("index.html")
            case "/message":
                self.send_html_file("message.html")
            case _:
                self.__GET_static()

    def __POST_routes(self):
        match self.parsed_path:
            case "/message":
                self.__message_POST()
            case _:
                self.send_html_file("error.html", 404)

    def __message_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        self.log_message("Sending data: %s", data_dict)
        self.send_through_socket(json.dumps(data_dict).encode())
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def __parse_path(self):
        self.parsed_path = urllib.parse.urlparse(self.path).path

    def __get_static_path(self):
        return PUBLIC_PATH.joinpath(self.parsed_path[1:])


def end_socket_server():
    if not os.environ.get("SOCKET_SERVER_DEPENDANT") and not os.environ.get(
        "CONTROL_SOCKET_SERVER"
    ):
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Ending socket server on socket %d with address %s", SERVER[1], SERVER[0])

    sock.sendto(b"END", SERVER)
    sock.close()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = (
        os.environ.get("HTTP_SERVER_HOST", ""),
        int(os.environ.get("HTTP_SERVER_PORT", "3000")),
    )
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
    finally:
        end_socket_server()


if __name__ == "__main__":
    run()
