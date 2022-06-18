import select
import json

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
            for sock in self.topics[data['topic']]:
                sock.send(json.dumps(data).encode())

def subscribe_listener(sock, func):
    readable, writable, exceptional = select.select([sock], [], [])
    while True:
        if readable[0]:
            #New data found!
            published_data = sock.recv(200)
            published_data = json.loads(published_data.decode())
            func(published_data)

if __name__ == "__main__":
    print("Broker example.")
    print("Not implemented.")
