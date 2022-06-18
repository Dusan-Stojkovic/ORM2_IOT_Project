
import socket


def init_socket_UDP(ip, port, server):
    sock = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_DGRAM
    )
    if server:
        sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((ip, port))
    else:
        sock.bind((ip, port))
        sock.setblocking(0)
        sock.settimeout(1)
    return sock

def init_socket_TCP(ip, port, server):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if server:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, port))
        s.listen()
        conn, addr = s.accept()
        return conn
    else:
        s.connect((ip, port))
        return s

# We ask our system do try and connect like this and it will give us it's
# default ip
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception as e:
        print(e)
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
