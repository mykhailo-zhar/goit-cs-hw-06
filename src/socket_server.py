import mimetypes
from  pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

PUBLIC_PATH = Path(__file__).resolve().parents[1] / 'public'

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.__parse_path()
        if self.parsed_path != '/message':
            self.send_html_file('error.html', 404)
            return
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print(data_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        self.__parse_path()
        if self.parsed_path == '/' or self.parsed_path == '/index':
            self.send_html_file('index.html')
        elif self.parsed_path == '/contact':
            self.send_html_file('contact.html')
        else:
            static_path = self.__get_static_path()
            if static_path.exists() and not self.parsed_path.endswith('.html'):
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(PUBLIC_PATH / filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()

        with open(self.__get_static_path(), 'rb') as file:
            self.wfile.write(file.read())

    def __parse_path(self):
        self.parsed_path = urllib.parse.urlparse(self.path).path
    def __get_static_path(self):
        return PUBLIC_PATH.joinpath(self.parsed_path[1:])


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
