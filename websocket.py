import socket
import struct
import base64
import hashlib
import logging
from threading import Thread
import signal
import sys
from select import select
import time
from web import RequestHandler

OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xa
MAGIC_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class WebSocket:

    def __init__(self, client, server):
        self.client = client
        self.server = server
        self.handshaken = False
        self.data = ''

    def feed(self, data, client):

        if not self.handshaken:
            logging.debug('start handshake')
            data = bytes.decode(data)
            r = RequestHandler(data)
            header = r.parser_header()

            if header['upgrade'].lower() == 'websocket' and header['connection'].lower() == 'upgrade':
                self.do_handshake(header['sec-websocket-key'])
                self.handshaken = True
                logging.info('handshake successful')

        else:
            f = Frame(data = data)
            msg = f.parser()

            logging.debug(msg)

            self.send(msg, client)

    def send(self, msg, clients):

        f = Frame(fin = 1, rsv1 = 0, rsv2 = 0, rsv3 = 0, opcode = OPCODE_TEXT, body = msg)
        data = f.build()

        for client in clients:
            client.send(data)

    def do_handshake(self, key):

        combined = key + MAGIC_GUID
        value = base64.b64encode(hashlib.sha1(str.encode(combined)).digest()).decode()

        r = RequestHandler()
        r.set_header('Upgrade', 'WebSocket')
        r.set_header('Connection', 'Upgrade')
        r.set_header('Sec-WebSocket-Accept', value)
        r.set_header('Server', 'MyPythonWebSocket')
        r.set_header('Access-Control-Allow-Origin', 'http://localhost')
        r.set_header('Access-Control-Allow-Credentials', 'true')

        header = 'HTTP/1.1 101 Web Socket Protocol Handshake\r\n' + r.build_header()

        self.client.send(header.encode())

    def close(self):
        pass

class WebSocketServer:

    def __init__(self, bind, port, cls):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((bind, port))
        self.bind = bind
        self.port = port
        self.cls = cls
        self.connections = {}
        self.clients = []
        self.listeners = [self.socket]

    def listen(self, backlog = 5):

        self.socket.listen(backlog)

        self.running = True

        while self.running:

            rList, wList, xList = select(self.listeners, [], self.listeners, 1)

            for ready in rList:

                if ready == self.socket:
                    client, address = self.socket.accept()
                    logging.info('accept listener')
                    self.clients.append(client)
                    fileno = client.fileno()
                    self.listeners.append(fileno)
                    self.connections[fileno] = self.cls(client, self)
                else:
                    logging.debug("Client ready for reading %s" % ready)
                    client = self.connections[ready].client
                    fileno = client.fileno()
                    data = client.recv(4096)
                    logging.info('received data')

                    if data:
                        logging.debug('to feed function')
                        self.connections[fileno].feed(data, self.clients)
                    else:
                        self.connections[fileno].close()
                        del self.connections[fileno]
                        self.listeners.remove(ready)

class Frame:

    def __init__(
        self,
        data = None,
        fin = 0,
        rsv1 = 0,
        rsv2 = 0,
        rsv3 = 0,
        opcode = 0,
        body = b''
    ):
        self.data = data
        self.fin = fin
        self.rsv1 = rsv1
        self.rsv2 = rsv2
        self.rsv3 = rsv3
        self.opcode = opcode
        self.masked_key = 0
        self.body = body
        self.payload_length = len(body)

    def build(self):

        header = b''

        if self.fin > 0x1:
            #fin must be 0 or 1
            pass

        if 0x2 < self.opcode < 0x8 or 0xA < self.opcode:
            #Unknown opcode
            pass

        header = struct.pack('!B', ((self.fin << 7)
                             | (self.rsv1 << 6)
                             | (self.rsv2 << 5)
                             | (self.rsv3 << 4)
                             | self.opcode))

        mask = 0
        length = self.payload_length
        if length < 126:
            header += struct.pack('!B', (mask | length))
        elif lenght < (1 << 16):
            header += struct.pack('!B', (mask | 126)) + struct.pack('!H', length)
        elif length < (1 << 63):
            header += struct.pack('!B', (mask | 127)) + struct.pack('!Q', lenght)
        else:
            #too large size
            pass

        body = self.body

        return bytes(header + body)



    def parser(self):
        #get first bytes
        first_bytes = self.data[0]

        self.fin = (first_bytes >> 7) & 1
        self.rsv1 = (first_bytes >> 6) & 1
        self.rsv2 = (first_bytes >> 5) & 1
        self.rsv3 = (first_bytes >> 4) & 1
        self.opcode = first_bytes & 0xf

        if self.rsv1 or self.rsv2 or self.rsv3:
            #if rsv is not 1, dissconnected.
            pass

        if 2 < self.opcode < 8 or self.opcode > 0xA:
            #Unknown opcode, you must dissconnect
            pass

        if self.opcode > 0x7 and self.fin == 0:
            # don't continue opcode in that
            pass

        second_bytes = self.data[1]

        mask = (second_bytes >> 7) & 1
        self.payload_length = second_bytes & 0x7f

        if self.opcode > 0x7 and payload_length > 125:
            #ping, pong must not be too lenght
            pass

        #check payload length
        if self.payload_length == 127:
            buf = self.data[2:10]
            some_bytes = self.data[10:]
        elif self.payload_length == 126:
            buf = self.data[2:4]
            some_bytes = self.data[4:]
        else:
            some_bytes = self.data[2:]

        #get masking key
        if mask:
            self.masked_key = some_bytes[0:4]
            some_bytes = some_bytes[4:]

        self.body = some_bytes
        return self.mask()

    def mask(self):

        masked = bytearray(self.body)

        for i in range(len(self.body)):
            masked[i] = masked[i] ^ self.masked_key[i % 4]

        return masked

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    server = WebSocketServer("", 8000, WebSocket)
    server_thread = Thread(target=server.listen, args=[5])
    server_thread.start()

    def signal_handler(signal, frame):
        server.running = False
        sys.exit()
    signal.signal(signal.SIGINT, signal_handler)
