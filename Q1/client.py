from socket import socket
from http import client

ADDRESS = ('', 12345)


def tcp(data, encoding='utf-8'):
    sock = socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(ADDRESS)
    sock.send(bytearray(data, encoding))
    sock.close()


def udp(data, encoding='utf-8'):
    sock = socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytearray(data, encoding), ADDRESS)
    sock.close()


def http():
    conn = client.HTTPConnection("localhost", 12345)
    conn.request("GET", "/* .py")
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data.decode())


def send_forever(send):
    while True:
        message = input()
        send(message)


http()
# send_forever(udp)
