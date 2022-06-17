from threading import Thread, Event
import socket
import json
from topic_message import TopicMessage
from networking import init_socket_UDP, get_ip
from sys import getsizeof
import time
import select


class Controler():
    def __init__(self):
        self.connection = None
        self.harvesters = []
        self.threads = []
        self.ip = get_ip()
        self.port_alive = 45000
        self.alive = {'alive': True, 'ip': self.ip}
        self.alive_size = getsizeof(self.alive)
        self.threads = []
        self.repeat = Event()

    def run(self):
        self.sock = init_socket_UDP('0.0.0.0', self.port_alive, True)
        self.threads.append(Thread(
            target=self._broadcast_alive, args=(), daemon=True))
        self.threads[0].start()                     # start broadcast_alive
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
                    print(
                        "client {0} has dropped his connection.".format(
                            harvester.ip))
                    remove = True
                    break
                i += 1

            if remove:
                self.harvesters.pop(i)

            i = 0
            for i in range(len(self.harvesters)):
                print("{0} is alive".format(self.harvesters[i].ip))
                self.harvesters[i].keep_alive = False

    def _broadcast_alive(self):
        bits = self.ip.split('.')
        addr_bit = bits[0] + '.' + bits[1] + '.' + bits[2] + '.'
        allips = [addr_bit + str(i) for i in range(2, 255)]
        # allips = [addr_bit + str(255)]  # real broadcast
        while True:
            for ip in allips:
                try:
                    if not ip == self.ip:
                        self.sock.sendto(
                            json.dumps(
                                self.alive).encode(), (ip, self.port_alive))
                        time.sleep(0.005)
                except BaseException as b:
                    print(b)
                    time.sleep(0.005)
                    pass

    def _read_stream(self):
        self.sock.setblocking(False)
        while True:
            try:
                ready = select.select([self.sock], [], [], 0.5)
                if ready[0]:
                    # TODO problem here: recv_size must be better
                    bts, addr = self.sock.recvfrom(self.alive_size)
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
                        topic_message = TopicMessage(msg, False)
                        self.harvesters.append(topic_message)
            except socket.timeout:
                self.connection = None
                pass

            except Exception as e:
                print(e)
                self.connection = None
                pass


if __name__ == "__main__":
    s = Controler()
    s.run()
