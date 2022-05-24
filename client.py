
import socket
import time
from discovery_message import DiscoveryMessage
from threading import Thread
import json
import select


class Client():
    def __init__(self):
        self.server_alive = False
        self.connection = None
        self.connected = False
        self.ip = self.get_ip()
        self.alive = {'alive': True, 'ip': self.ip}

    def run(self):
        self.init_socket()
        t = Thread(target=self._connect_to_srv, args=(), daemon=True)
        t.start()
        self._streams()

    def _connect_to_srv(self):
        while not self.server_alive:
            print("SERVER NOT ALIVE")

            ready = select.select([self.client_socket], [], [], 0.1)
            if ready[0]:
                bts, addr = self.client_socket.recvfrom(1024)
                msg = bts.decode()
                msg = json.loads(msg)
                self.server_alive = msg['alive']
                self.serverIp = msg['ip']
            time.sleep(1)

        print(
            "SERVER IS ALIVE ON IP: {0}, PORT: {1}".format(
                self.serverIp,
                self.port))

        # Keep alive time
        while True:
            bts, addr = self.client_socket.recvfrom(1024)
            if bts.decode() == "":
                print("server lost")

            data = json.dumps(self.alive).encode()
            self.client_socket.sendto(data, (self.serverIp, self.port))
            time.sleep(0.1)

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

        self.client_socket_ack = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM
        )

        self.client_socket.bind((self.clientIp_ack, self.port))

        self.client_socket.setblocking(0)

    def _streams(self):
        while True:
            try:
                if self.server_alive and not self.connected:
                    self.connected = True
                    discovery_message = DiscoveryMessage(
                        {'id': 120, 'ip': self.ip,
                            'manual': True, 'actuators': [
                                "accel", "steer"], 'sensors': ["camera"]}
                    ).toJSON()
                    # print(discovery_message)
                    data = discovery_message.encode()
                    self.client_socket.sendto(data, (self.serverIp, self.port))
                    time.sleep(1)

            except Exception as e:
                # Reinitialize the socket for reconnecting to client.
                print(e)
                self.connection = None
                self.init_socket()
                pass


if __name__ == "__main__":
    c = Client()
    c.run()
