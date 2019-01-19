import socket
import time
import logging
import signal
import sys
from web import RequestHandler

class HTTPHandler:

    def __init__(
        self,
        client,
        data,
        dir = './html',
        default_dir = './html'
    ):
        self.client = client
        self.data = data
        self.file_dir = dir
        self.file_default_dir = default_dir

        self.request = RequestHandler(data)
        self.header = self.request.parser_header()
        self.response = None

    def handler(self):

        method = self.request.get_method()

        if method == 'GET':
            self.get()

        elif method == 'POST':
            self.post()

        self.client.send(self.response)
        logging.debug('sending')
        self.client.close()

    def get(self):

        file_request = self.request.get_file_request()
        file_dir = self.file_dir + file_request

        try:
            file = open(file_dir, 'rb')
            content = file.read()
            file.close()
            header = self.gen_headers(200)

        except Exception as e:
            file = open(self.file_default_dir + '/not_found.html', 'rb')
            content = file.read()
            file.close()
            header = self.gen_headers(404)

        response = header + content
        self.response = response

    def post(self):
        pass

    def gen_headers(self, status_code = 200):

        r = RequestHandler()
        date = time.strftime('%a, %d, %b, %Y, %H:%M:%S', time.localtime())

        r.set_header('Date', date)
        r.set_header('Server', 'MyPythonWeb')
        r.set_header('Connection', 'close')

        if status_code == 200:
            header = 'HTTP/1.1 200 OK\r\n'
        elif status_code == 404:
            header = 'HTTP/1.1 404 Not Found\r\n'

        header += r.build_header()
        return header.encode()

class HttPServer:

    def __init__(self,
        bind = 'localhost',
        port = 8088,
        file_dir = './html'
    ):
        self.bind = bind
        self.port = port
        self.file_dir = file_dir
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((bind, port))

    def listen(self, backlog = 5):

        self.socket.listen(backlog)

        self.running = True

        while self.running:

            logging.info('Awaiting new connection')
            client, address = self.socket.accept()
            data = client.recv(1024)

            if data:
                data = bytes.decode(data)
                logging.debug(data)
                h = HTTPHandler(client, data, self.file_dir)
                h.handler()
            else:
                logging.debug('test')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    server = HttPServer()
    server.listen()

    def signal_handler(signal, frame):
        server.running = False
        sys.exit()
    signal.signal(signal.SIGINT, signal_handler)
