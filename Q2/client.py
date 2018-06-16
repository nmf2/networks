import urllib
import urllib.request as req
import http.client as http
import random
import string
from pathlib import Path

server = '127.0.0.1:12345'
USER = ''

# TODO Fix post encoding data issue (study how curl -F does it)


def simple_request(method, *args):
    conn = http.HTTPConnection(server)
    conn.request(method, '/' + str((*args)))
    res = conn.getresponse()
    conn.close()
    return str(res.read(), 'utf-8')


def create_form(path):

    with open(path, 'rb') as file:
        data = file.read()
    strings = string.ascii_letters + string.digits
    boundary = '---------' + ''.join(random.choice(strings) for _ in range(10))

    temp = [boundary + '\r\n',
            'Content-Disposition: file; filename="file"\r\n',
            'Content-Type: application/octet-stream\r\n',
            '\r\n',
            data,
            '\r\n',
            boundary + '\r\n'
            ]
    form = bytearray()
    for piece in temp:
        form += bytearray(piece, 'utf-8')

    return form


def login(user):
    USER = user
    return simple_request("LOGIN", USER)


def ls(user):
    return simple_request("LIST", user)


def get(filename):
    if '/' in filename:  # it means it's a file from another user
        url = "http://" + server + '/' + filename
    else:
        url = "http://" + server + '/' + USER + '/' + filename
    try:
        file, headers = req.urlretrieve(url, filename)
    except urllib.error.HTTPError as err:
        print(headers)
        return str(err)
    return "File {} retrieved successfully".format(filename)


def post(filename):
    url = "http://" + server + '/' + USER + '/' + filename
    req.urlopen(url, create_form(str(Path.cwd()) + '/' + filename))
    return 'lol'


def main():
    def do(method):
        return {
            "GET": get,
            "LOGIN": login,
            "LIST": ls,
            "POST": post
        }.get(method,
              lambda method: print("Method '{}' not supported".format(method)))

    print("Type in your commands: ")
    try:
        while (True):
            command = input("> ")
            if command == '':
                continue
            method, *tokens = list(filter(lambda x: x != '',
                                   command.split(" ")))
            try:
                res = do(method.upper())(*tokens)
                print(str(res))
            except(TypeError):
                print("Wrong set of arguments")

    except(KeyboardInterrupt):
        
        print("\nClosing client")


if __name__ == '__main__':
    main()
