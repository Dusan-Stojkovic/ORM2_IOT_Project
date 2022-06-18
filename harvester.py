import time
from topic_message import TopicMessage
from threading import Thread, Event
from sys import getsizeof
from networking import init_socket_UDP, get_ip, init_socket_TCP
import json
import socket


# TODO merge this to my ROS architecture
class Harvester():
    def __init__(self):
        self.id = 120
        self.server_alive = False
        self.connected = False
        self.port_subscribe = 45003
        self.port_publish = 45002
        self.port_recieve = 45001
        self.port_broadcast = 45000
        self.ip = get_ip()
        self.alive = {'alive': True, 'ip': self.ip}
        self.try_conn = { 'clientID': self.id, 'ip': self.ip}
        self.alive_size = getsizeof(self.alive)
        self.sock_recieve = init_socket_UDP('0.0.0.0', self.port_recieve, False)
        self.sock_broadcast = init_socket_UDP('0.0.0.0', self.port_broadcast, False)
        self.threads = []

    def run(self):
        self.threads.append(Thread(target=self.callback, args=(), daemon=True))
        self.threads[-1].start()
        self._streams()

    def callback(self):
        while True: 
            if not self.server_alive:
                print("SERVER NOT ALIVE")
            try:
                bts, addr = self.sock_recieve.recvfrom(self.alive_size)
                msg = bts.decode()
                msg = json.loads(msg)
                self.serverIp = msg['ip']
                self.server_alive = msg['alive']
                if self.server_alive:
                    print(
                        "SERVER IS ALIVE ON IP: {0}, PORT: {1}".format(
                            self.serverIp,
                            self.port_recieve))
            except socket.timeout:
                self.server_alive = False
                self.connected = False
                continue

    def _connect_to_srv(self):
        # Keep alive time
        while self.server_alive:
            data = json.dumps(self.alive).encode()
            self.sock_broadcast.sendto(data, (self.serverIp, self.port_broadcast))
            time.sleep(0.1)

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

                    self.sock_broadcast.sendto(json.dumps(self.try_conn).encode(), (self.serverIp, self.port_broadcast))

                    time.sleep(0.1)
                    self.sock_pub = init_socket_TCP(self.serverIp, self.port_publish, False)
                    time.sleep(0.1)
                    self.sock_sub = init_socket_TCP(self.serverIp, self.port_subscribe, False)

                    register = TopicMessage({
                        'type': "register",
                        'id': self.id,
                        'ip': self.ip, 
                        'attributes': {
                            'manual': False,
                            'actuators': ["steer", "accel"],
                            'sensors': ["camera"]},
                        'topics_sub': ["/controler/manual",
                            "/controler/start",
                            "/controler/stop"]
                        }).toJSON()

                    self.sock_sub.send(register.encode())

            except Exception as e:
                # Reinitialize the socket for reconnecting to controler.
                print(e)
                self.connected = False
                pass

if __name__ == "__main__":
    c = Harvester()
    c.run()
