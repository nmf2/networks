from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path
# from urllib3.request import FileHandler
import mimetypes
import os

# TODO Create file db


class AwesomeHTTPHandler(BaseHTTPRequestHandler):
    LOGGED = True
    BASE = ''
    USER = ''

    def set_logged(self, value):
        AwesomeHTTPHandler.LOGGED = value

    def get_logged(self):
        return AwesomeHTTPHandler.LOGGED

    def set_user(self, value):
        AwesomeHTTPHandler.USER = value

    def get_user(self):
        return AwesomeHTTPHandler.USER

    def set_base(self, value):
        AwesomeHTTPHandler.BASE = value

    def get_base(self):
        return AwesomeHTTPHandler.BASE

    def simple_response(self, code, message):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(bytearray(message+'\n', 'ascii'))

    def clean_path(self):
        i = 0
        print(self.path)
        try:
            while (self.path[i] is '.' or self.path[i] is '/'):
                i += 1
        except(IndexError):
            i -= 1
        return self.path[i:]

    def file_type(self, path):
        content_type = mimetypes.guess_type(str(path))[0]
        if content_type is None:
            content_type = 'application/octet-stream'
        return content_type

    def is_logged(self):
        if not self.get_logged():
            self.simple_response(400, "Must make login")
            return False
        return True

    def path_requirements(self, path):
        if str(path) is '':
            self.simple_response(400, "The root path is not accessible")
            return False
        elif str(path).endswith('/'):
            self.simple_response(400, "Folders are not supported")
            return False
        return True

    def clean_payload(self, payload):
        data = payload
        i = data.find(b'\r\n\r\n')
        data = data[i+4:]
        data = data[:-2]
        i = data.rfind(b'\r\n')
        data = data[:i]
        return data

    def save(self, path):
        length = int(self.headers['content-length'])
        data = self.clean_payload(self.rfile.read(length))
        with open(path, 'wb') as file:
            print(data)
            file.write(data)
        self.simple_response(200, "File received successfully")

    def do_GET(self):
        path = self.clean_path()
        assert(self.is_logged())
        assert(self.path_requirements(path))
        file = Path(path)
        if file.exists():
            # send file
            self.send_response(200)
            self.send_header('Content-type', self.file_type(str(file)))
            self.send_header('Content-Disposition',
                             'attachment; filename="{}"'.format(file.name))
            self.end_headers()
            with open(str(file), 'rb') as data:
                self.wfile.write(data.read())
        else:
            self.simple_response(403, 'File does not exist')

    def do_POST(self):
        path = self.clean_path()
        assert(self.is_logged())
        assert(self.path_requirements(path))
        print(path)
        print(self.headers)
        if not Path(path).exists():
            self.save(path)
        else:
            self.simple_response(400, "File already exists")

    def do_DELETE(self):
        assert(self.is_logged())
        assert(self.path_requirements(self.clean_path()))
        file = Path(self.clean_path()).name
        print(file)
        file = self.get_base() / file
        print(file)
        if file.exists():
            file.unlink()
            self.simple_response(200,
                                 "File {} removed successfully."
                                 .format(file.name))
        else:
            self.simple_response(400,
                                 "File {} doesn't exist."
                                 .format(file.name))

    def do_PUT(self):
        path = self.clean_path()
        assert(self.is_logged())
        assert(self.path_requirements(path))
        self.save(path)
        self.simple_response(200, "File received successfully")

    def do_LIST(self):
        assert(self.is_logged())
        user = Path(self.clean_path()).name
        if user is '':
            self.simple_response(400, "Bad path")
            return
        print("user: '{}'".format(user))
        files_list = os.listdir(str(Path.cwd()) + '/' + user)
        files_list.sort()
        self.simple_response(200, '\n'.join(files_list))

    def do_LOGIN(self):
        path = Path(self.clean_path())
        self.set_user(path.name)
        self.set_base(Path.cwd() / self.get_user())
        if not self.get_base().exists():
            try:
                self.get_base().mkdir()
            except():
                self.simple_response(400, "Bad username")
                self.set_logged(False)
                raise
        self.set_logged(True)
        self.simple_response(200, "User " + self.get_user() +
                             " logged in successfully")


class MultiThreadedHTTPServer(HTTPServer, ThreadingMixIn):
    "All set up, requests will be handled in separate threads"
    pass


http_server = MultiThreadedHTTPServer(('', 12345), AwesomeHTTPHandler)
print("Server up and running. Control-C to terminate.")
try:
    http_server.serve_forever()

except(KeyboardInterrupt):
    print("\nServer terminated. Good bye :)")