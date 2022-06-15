from threading import Thread, Event
import socket
import json
from topic_message import TopicMessage
from sys import getsizeof
import time
import select


class Controler():
    def __init__(self):
        self.connection = None
        self.harvesters = []
        self.threads = []
        self.ip = self.get_ip()
        self.alive = {'alive': True, 'ip': self.ip}
        self.alive_size = getsizeof(self.alive)
        self.threads = []
        self.threads.append(Thread(
            target=self._broadcast_alive, args=(), daemon=True))
        self.repeat = Event()

    def run(self):
        self._init_socket()
        self.threads[0].start()                                 # start broadcast_alive
        self.threads.append(Thread(
            target=self.callback, args=(), daemon=True))        # start keep_alive listener
        self.threads[-1].start()
        self._read_stream()                                     # main loop reads stream

    def callback(self):
        while not self.repeat.wait(1):
            i = 0
            remove = False
            for harvester in self.harvesters:
                if not harvester.keep_alive:
                    print("client {0} has dropped his connection.".format(harvester.ip))
                    remove = True
                    break
                i += 1

            if remove:
                self.harvesters.pop(i)

            i = 0
            for i in range(len(self.harvesters)):
                print("{0} is alive".format(self.harvesters[i].ip))
                self.harvesters[i].keep_alive = False

    def _init_socket(self):
        """Initialize the communication socket server.
        """
        self.port = 45000
        self.serverIp = '0.0.0.0'
        # self.broadcast = '192.168.252.255'

        self.server_socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM
        )
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_socket.bind((self.serverIp, self.port))
        # self.server_socket.settimeout(1)
        # self.server_socket.setblocking(0)

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

    def _broadcast_alive(self):
        bits = self.ip.split('.')
        addr_bit = bits[0] + '.' + bits[1] + '.' + bits[2] + '.'
        allips = [addr_bit + str(i) for i in range(0, 255)]
        # allips = [addr_bit + str(255)] real broadcast
        while True:
            for ip in allips:
                try:
                    if not ip == self.get_ip():
                        self.server_socket.sendto(
                            json.dumps(self.alive).encode(),
                            (ip, self.port))
                        # print(ip)
                        time.sleep(0.005)
                except BaseException:
                    time.sleep(0.1)
                    pass

    def _read_stream(self):
        self.server_socket.setblocking(False)
        while True:
            try:
                ready = select.select([self.server_socket], [], [], 0.5)
                if ready[0]:
                    bts, addr = self.server_socket.recvfrom(self.alive_size)
                    msg = bts.decode()
                    msg = json.loads(msg)
                    if 'alive' in msg:
                        if msg['alive']:
                            i = 0
                            for harvester in self.harvesters:
                                if harvester.ip == msg['ip']:
                                    self.harvesters[i].keep_alive = True
                                    break
                                i += 1

                            # print("client on ip: {0} is alive".format(msg['ip']))
                    else:
                        # TODO main sub loop and setup for communication
                        # must start here, new thread for each device in network
                        topic_message = TopicMessage(msg, False)
                        print(topic_message)

                        # TODO detach thread to work with the new harvesters
                        # TODO rename harvester to devices or something
                        # TODO move logic to our broker
                        self.harvesters.append(topic_message)

            except Exception as e:
                # Reinitialize the socket for reconnecting to client.
                print(e)
                self.connection = None
                self.init_socket()
                pass
            # except BaseException:
            #     self.server_socket.close()
            #     pass


if __name__ == "__main__":
    s = Controler()
    s.run()