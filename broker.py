import select
import json
from sys import getsizeof
import struct

class Broker:
    def __init__(self):
        print("Broker starting...")
        self.topics = {}

    def add_topics(self, sock, topics):
        for topic in topics:
            if not topic in self.topics:
                self.topics[topic] = [sock]
            else:
                self.topics[topic].append(sock)

    def notify_subscribers(self, data):
        if data['topic'] in self.topics:
            j = json.dumps(data)
            for sock in self.topics[data['topic']]:
                #print("notify {0}", data['topic'])
                send_msg(j, sock)


def subscribe_listener(sock, func):
    readable, writable, exceptional = select.select([sock], [], [])
    while True:
        if readable[0]:
            #New data found!
            #print(getsizeof(published_data))
            try:
                published_data = recv_msg(sock)
                published_data = json.loads(published_data.decode())
                #print(published_data)
                func(published_data)
            except AttributeError as a:
                #print(a)
                pass
            except Exception:
                pass

def send_msg(data, sock):
    msg = struct.pack('>I', len(data)) + data.encode()
    sock.sendall(msg)

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

if __name__ == "__main__":
    print("Broker example.")
    print("Not implemented.")
