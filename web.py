import socket

class RequestHandler:

    def __init__(self, request = None):

        if request is not None:
            self.request = request.split('\r\n\r\n')
        self.header = {}
        self.content = ''

    def parser_header(self):

        header = {}

        for line in self.request[0].split('\r\n')[1:]:
            row = line.split(': ')
            header[row[0].lower()] = row[1]

        self.header = header
        return header

    def build_header(self):

        header = ''
        for key in self.header:
            header += key + ': ' + self.header[key] + '\r\n'

        header += '\r\n'

        return header

    def set_header(self, key, value):

        self.header[key] = value
