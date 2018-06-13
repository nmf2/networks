from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
# from urllib3.request import FileHandler
import mimetypes
import os


class AwesomeHTTPHandler(BaseHTTPRequestHandler):
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
                                 "created successfully.")
        except:
            self.send_response(500)
            self.end_headers()
            raise

    def login(self, path):
        if not os.path.isdir(path):
            os.mkdir(path)
            self.simple_response(200, "User " + path +
                                 " successfully logged in.\n")
        else:
            self.simple_response(200, "Already logged in\n")
    
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

    def do_GET(self):
        path = self.clean_path()
        if path is '':
            self.simple_response(403, "The root path is not accesible.")
        elif path.endswith('/'):
            self.simple_response(403, "Use POST to create folders or login.")
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
        path = self.clean_path()
        if path is '':
            self.simple_response(403, "The root path is not accesible.")
        # detect login or folder creation attempt
        elif path.endswith('/'):
            if path.count('/') is 1:
                self.login(path)
            else:
                self.create_folder(path)
        else:
            file_name, content_type = self.file_info(path)            


class MultiThreadedHTTPServer(HTTPServer, ThreadingMixIn):
    "All set up, requests will be handled in separate threads"
    pass


# if __name__ is "__main__":
#     http_server = MultiThreadedHTTPServer(('', 12345), AwesomeHTTPHandler)
#     print("Server up and running. Control-C to terminate.")
#     http_server.serve_forever()

http_server = MultiThreadedHTTPServer(('', 12345), AwesomeHTTPHandler)
print("Server up and running. Control-C to terminate.")
http_server.serve_forever()
