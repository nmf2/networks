from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path
# from urllib3.request import FileHandler
import mimetypes
import os

USER = ''
BASE = Path.cwd()

# TODO Use BASE in all file operations
# TODO Implement GET_SHARED to get files from other users
# TODO Finish POST. Receive file. Read from rfile?


class AwesomeHTTPHandler(BaseHTTPRequestHandler):
    logged = False
    
    def simple_response(self, code, message):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytearray(message, 'ascii'))
    
    def clean_path(self):
        i = 0
        while (self.path[i] is '.' or self.path[i] is '/'):
            i += 1
        return self.path[i:]
    
    def create_folder(self, path):
        try:
            os.makedirs(path)
            self.simple_response(200, "Path " + path +
                                 " created successfully.")
        except():
            self.send_response(500)
            self.end_headers()
            raise
    
    def file_info(self, path):
        # determine file name
        i = -1
        while (self.path[i] is '/'):
            i -= 1
        file_name = path[i:]

        # determine file's content type
        content_type = mimetypes.guess_type(path)[0]

        if content_type is None:
            content_type = 'application/octet-stream'

        return file_name, content_type
    
    def is_logged(self):
        if not self.logged:
            self.simple_response(400, "Must make login")
            return False
        return True

    def do_GET(self):
        assert(self.is_logged())
        path = self.clean_path()
        if path is '':
            self.simple_response(403, "The root path is not accesible.")
        elif path.endswith('/'):
            self.simple_response(403, "Use POST to create folders")
        elif os.path.isfile(path):
            file_name, content_type = self.file_info(path)
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-Disposition',
                             'attachment; filename="{}"'.format(file_name))
            self.end_headers()
            with open(path, 'rb') as data:
                self.wfile.write(data.read())
        else:
            self.simple_response(403, '')
    
    def do_POST(self):
        assert(self.is_logged())
        path = self.clean_path()
        if path is '':
            self.simple_response(403, "The root path is not accesible.")
        # detect login or folder creation attempt
        elif path.endswith('/'):
            self.create_folder(path)
        else:
            file_name, content_type = self.file_info(path)

    def do_LOGIN(self):
        path = Path(self.clean_path())
        USER = path.name
        BASE = BASE / user
        if not os.path.isdir(path):
            os.mkdir(path)
        self.logged = True


class MultiThreadedHTTPServer(HTTPServer, ThreadingMixIn):
    "All set up, requests will be handled in separate threads"
    pass


# if __name__ is "__main__":
#     http_server = MultiThreadedHTTPServer(('', 12345), AwesomeHTTPHandler)
#     print("Server up and running. Control-C to terminate.")
#     http_server.serve_forever()

def main():
    http_server = MultiThreadedHTTPServer(('', 12345), AwesomeHTTPHandler)
    print("Server up and running. Control-C to terminate.")
    http_server.serve_forever()
