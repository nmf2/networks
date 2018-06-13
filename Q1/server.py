from socket import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler


def tcp():
    server_socket = socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 12345))
    server_socket.listen(5)
    print('##################################################')
    print('TCP Server up and running. Control-C to terminate.')
    print('##################################################\n')

    while (True):
        try:
            client_socket, port = server_socket.accept()
            message = client_socket.recv(2048)
            print(message.decode())
            client_socket.close()
        except KeyboardInterrupt:
            server_socket.close()
            print("TCP Server terminated")


def udp():
    server_socket = socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', 12345))
    print('##################################################')
    print('UDP Server up and running. Control-C to terminate.')
    print('##################################################\n')

    while (True):
        try:
            message, sender = server_socket.recvfrom(2048)
            print(message.decode())
        except KeyboardInterrupt:
            server_socket.close()
            print("UDP Server terminated")


def http():
    print('##################################################')
    print('HTTP Server up and running. Control-C to terminate.')
    print('##################################################\n')

    server = HTTPServer(('', 12345), SimpleHTTPRequestHandler)
    server.serve_forever()


def get_protocol():
    with open('protocol.txt', 'r+') as f:
        return f.readline()


def start_server():
    protocol = get_protocol()
    print(protocol)

    if protocol.lower() == 'udp':
        udp()
    elif protocol.lower() == 'http':
        http()
    else:
        tcp()


start_server()
