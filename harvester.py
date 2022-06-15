import socket
import time
from topic_message import TopicMessage
from threading import Thread, Event
from sys import getsizeof
import json


# TODO merge this to my ROS architecture
class Harvester():
    def __init__(self):
        self.server_alive = False
        self.connection = None
        self.connected = False
        self.ip = self.get_ip()
        self.alive = {'alive': True, 'ip': self.ip}
        self.alive_size = getsizeof(self.alive)
        self.repeat = Event()
        self.threads = []

    def run(self):
        self.init_socket()

        self.threads.append(Thread(target=self.callback, args=(), daemon=True))
        self.threads[-1].start()
        self._streams()

    def callback(self):
        while not self.repeat.wait(1):
            if not self.server_alive:
                print("SERVER NOT ALIVE")

            try:
                bts, addr = self.client_socket.recvfrom(self.alive_size)
                msg = bts.decode()
                msg = json.loads(msg)
                self.server_alive = msg['alive']
                self.serverIp = msg['ip']
                print(
                    "SERVER IS ALIVE ON IP: {0}, PORT: {1}".format(
                        self.serverIp,
                        self.port))
            except socket.timeout:
                self.server_alive = False
                self.connected = False
                continue

    def _connect_to_srv(self):
        # Keep alive time
        while self.server_alive:
            # reply mechanism
            data = json.dumps(self.alive).encode()
            self.client_socket.sendto(data, (self.serverIp, self.port))
            time.sleep(0.1)

    # We ask our system do try and connect like this and it will give us it's default ip
    def get_ip(self):
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

    def init_socket(self):
        """Initialize the socket client.
        """

        self.port = 45000            # com port

        self.clientIp_ack = '0.0.0.0'

        self.client_socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM
        )

        self.client_socket.bind((self.clientIp_ack, self.port))
        self.client_socket.setblocking(0)
        self.client_socket.settimeout(1)

    def _streams(self):
        while True:
            try:
                if self.server_alive and not self.connected:
                    self.connected = True

                    self.threads.append(
                        Thread(
                            target=self._connect_to_srv,
                            args=(),
                            daemon=True))
                    self.threads[-1].start()

                    # TODO improve this mechanism so that our broadcast/reciever
                    # can start working
                    topic_message = TopicMessage(
                        {'id': 120, 'ip': self.ip,
                            'manual': True, 'actuators': [
                                "accel", "steer"], 'sensors': ["camera"]}
                    ).toJSON()
                    # print(discovery_message)
                    data = topic_message.encode()
                    self.client_socket.sendto(data, (self.serverIp, self.port))
                    time.sleep(1)

            except Exception as e:
                # Reinitialize the socket for reconnecting to controler.
                print(e)
                self.connection = None
                self.init_socket()
                pass


if __name__ == "__main__":
    c = Harvester()
    c.run()
