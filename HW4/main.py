from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import urllib.parse
import mimetypes
import pathlib
import socket
import threading
import json
import os

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('HW4/index.html')
        elif pr_url.path == '/contact':
            self.send_html_file('HW4/message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('HW4/error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())
            
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}

        # Send the data to the Socket server for processing
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps(data_dict).encode(), ('localhost', 5000))

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

def run_socket_server():
    print(f'Running Socket server on thread {threading.get_ident()}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 5000))
    data={}
    while True:
        info, addr = sock.recvfrom(1024)
        info = json.loads(info.decode())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        data[timestamp] = info
        with open('storage/data.json', 'w') as f:
            json.dump(data, f)

def start_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    print(f'Running HTTP server on thread {threading.get_ident()}')
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def run(server_class=HTTPServer, handler_class=HttpHandler):
    # Check for the storage directory and data.json file
    if not os.path.exists('storage'):
        os.makedirs('storage')
    if not os.path.exists('storage/data.json'):
        with open('storage/data.json', 'w') as f:
            json.dump({}, f)

    # Start the Socket server on a separate thread
    t1 = threading.Thread(target=run_socket_server)
    t1.start()

    # Start the HTTP server on a separate thread
    t2 = threading.Thread(target=start_http_server)
    t2.start()

if __name__ == '__main__':
    run()

