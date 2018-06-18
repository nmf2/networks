import urllib
import urllib.request as req
import http.client as http
import random
import string
from pathlib import Path

global USER
server = '127.0.0.1:12345'
USER = ''

# TODO Fix post encoding data issue (study how curl -F does it)


def get_user(user=False):
    if not user:
        return USER
    else:
        return user


def simple_request(method, *args):
    conn = http.HTTPConnection(server)
    conn.request(method, str(*args))
    try:
        res = conn.getresponse()
        conn.close()
    except:
        return "400 Bad Request"
    return str(res.read(), 'utf-8')


def create_form(path):
    if path.endswith('/'):
        return b''
    with open(path, 'rb') as file:
        data = file.read()
    strings = string.ascii_letters + string.digits
    boundary = '---------' + ''.join(random.choice(strings) for _ in range(10))
    boundary = bytes(boundary, 'utf-8')

    form = boundary + b'\r\n' + \
        b'Content-Disposition: file; filename="file"\r\n' + \
        b'Content-Type: application/octet-stream\r\n' + \
        b'\r\n' + \
        data + \
        b'\r\n' + \
        boundary + b'\r\n'

    return form


def special_request(filename, method, data=True, target=''):
    form = None
    url = get_url(filename)
    if data:
        form = create_form(filename)        
    if not target == '':
        url = get_url(target)
        
    opener = req.build_opener(req.HTTPHandler)
    r = req.Request(url,
                    data=form,
                    method=method)
    r.get_method = lambda: method
    try:
        res = opener.open(r)
    except urllib.error.HTTPError as err:
        return str(err)
    return ' '.join([str(res.status), res.reason])


def login(user):
    global USER
    USER = user
    return simple_request("LOGIN", USER)


def ls(user):
    return simple_request("LIST", user)


def get_url(filename):
    global USER
    url = "http://" + server + '/' + USER + '/' + filename
    print('get_url ', url)
    return url


def get(filename):
    url = get_url(filename)
    try:
        file, headers = req.urlretrieve(url, Path(filename).name)
    except urllib.error.HTTPError as err:
        return str(err)
    return "File {} retrieved successfully".format(filename)


def post(filename, location=''):
    return special_request(filename, 'POST', target=location)
    # url = get_url(filename)
    # try:
    #     res = req.urlopen(url, create_form(str(Path.cwd()) + '/' + filename))
    # except urllib.error.HTTPError as err:
    #     return str(err.code) + ' ' + str(err.reason)
    # return ' '.join([str(res.status), res.reason])


def put(filename, location=''):
    return special_request(filename, 'PUT', target=location)


def delete(filename):
    return special_request(filename, 'DELETE', data=False)


def logout():
    return simple_request('LOGOUT')


def main():
    def switch(method):
        return {
            "GET": get,
            "LOGIN": login,
            "LIST": ls,
            "POST": post,
            "PUT": put,
            "DELETE": delete,
            "LOGOUT": logout,
        }.get(method,
              lambda method: print("Method '{}' not supported".format(method)))

    print("Type in your commands: ")
    try:
        logged = False
        while (True):
            command = input("> ")
            if command == '':
                continue
            method, *tokens = list(filter(lambda x: x != '',
                                   command.split(" ")))
            if method.upper() == "LOGIN":
                global USER
                USER = tokens
                logged = True
            elif method.upper() == "LOGOUT":
                logged = False
            elif not logged:
                print("Must login")
                continue
            elif method.upper() == "LIST":
                tokens = [get_user(*tokens)]
            try:
                res = switch(method.upper())(*tokens)
                print(str(res))
            except(TypeError):
                print("Wrong set of arguments")
                raise

    except(KeyboardInterrupt):
        print(logout())
        print("\nClosing client")
    except Exception as e:
        print(str(e))
        print(logout())
    except:
        pass


if __name__ == '__main__':
    main()
