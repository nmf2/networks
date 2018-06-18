from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path
# from urllib3.request import FileHandler
import mimetypes
import os
import shutil

# TODO Create file db


class AwesomeHTTPHandler(BaseHTTPRequestHandler):
    LOGGED = False
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
        # print(self.path)
        print('cp.path.cl ', self.path)
        print('cp.path.ba ', self.get_base())
        file = str(self.get_base()) + '/' + self.path
        file = Path(file)
        print('cp.path ', file)
        # print('    ', path.resolve())
        return file.resolve(strict=False)

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
        # print(str(path), ' ', str(Path.cwd()))
        if path == Path.cwd():
            self.simple_response(400, "The root path is not accessible")
            return False
        return str(path).startswith(str(Path.cwd()))

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
        if data == b'' and self.path.endswith('/'):
            path.mkdir()
            self.simple_response(200, "Directory created")
        else:
            with open(path, 'wb') as file:
                # print(data)
                file.write(data)
        self.simple_response(200, "File received successfully")

    def do_GET(self):
        path = self.clean_path()
        print('gpath = ', path)
        assert(self.is_logged())
        assert(self.path_requirements(path))
        print('get ', path)
        if path.is_file():
            # send file
            self.send_response(200)
            self.send_header('Content-type', self.file_type(str(path)))
            self.send_header('Content-Disposition',
                             'attachment; filename="{}"'.format(path.name))
            self.end_headers()
            with open(str(path), 'rb') as data:
                self.wfile.write(data.read())
        elif path.exists():
            self.simple_response(500, 'Requested a directory')
        else:
            self.simple_response(404, 'File does not exist')

    def do_POST(self):
        path = self.clean_path()
        assert(self.is_logged())
        assert(self.path_requirements(path))
        print(path)
        print(self.headers)
        file = Path(path)
        if not file.exists():
            self.save(path)
        else:
            self.simple_response(400, "File/folder already exists")

    def do_DELETE(self):
        path = self.clean_path()
        assert(self.is_logged())
        assert(self.path_requirements(path))
        print(path)
        if path.is_file():
            path.unlink()
            self.simple_response(200,
                                 "File {} removed successfully."
                                 .format(path.name))
        elif path.exists():
            shutil.rmtree(str(path))
            self.simple_response(200,
                                 "Directory {} removed successfully."
                                 .format(path.name))
        else:
            self.simple_response(400,
                                 "File {} doesn't exist."
                                 .format(path.name))

    def do_PUT(self):
        path = self.clean_path()
        assert(self.is_logged())
        assert(self.path_requirements(path))
        self.save(path)
        self.simple_response(200, "File received successfully")

    def do_LIST(self):
        path = self.clean_path()
        print('lpath = ', path)
        assert(self.is_logged())
        assert(self.path_requirements(path))
        if path.exists():
            files_list = os.listdir(str(path))
            files_list.sort()
            self.simple_response(200, '\n'.join(files_list))
        else:
            self.simple_response(400, "Invalid username")

    def do_LOGIN(self):
        path = self.clean_path()
        self.set_user(Path(self.path).name)
        self.set_base(Path(Path.cwd()))
        if not path.exists():
            try:
                path.mkdir()
            except():
                self.simple_response(400, "Bad username")
                self.set_logged(False)
                raise
        self.set_logged(True)
        self.simple_response(200, "User " + self.get_user() +
                             " logged in successfully")

    def do_LOGOUT(self):
        self.set_logged(False)
        self.simple_response(200, "User " + self.get_user() +
                             " logged out successfully")
        self.USER = ''


class MultiThreadedHTTPServer(HTTPServer, ThreadingMixIn):
    "All set up, requests will be handled in separate threads"
    pass


http_server = MultiThreadedHTTPServer(('', 12345), AwesomeHTTPHandler)
print("Server up and running. Control-C to terminate.")
try:
    http_server.serve_forever()

except(KeyboardInterrupt):
    print("\nServer terminated. Good bye :)")
