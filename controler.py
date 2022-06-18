from threading import Thread, Event
import socket
import json
from topic_message import TopicMessage
from networking import init_socket_UDP, get_ip, init_socket_TCP
from sys import getsizeof
import time
import select


class Controler:
    def __init__(self):
        self.connection = None
        self.connected_devices = []
        self.ip = get_ip()
        self.port_subscribe = 45002
        self.port_publish = 45003
        self.port_recieve = 45000
        self.port_broadcast = 45001
        self.alive = {'alive': True, 'ip': self.ip}
        self.alive_size = getsizeof(self.alive)
        self.threads = []
        self.repeat = Event()

    def run(self):
        self.sock_recieve = init_socket_UDP('0.0.0.0', self.port_recieve, True)
        self.sock_broadcast = init_socket_UDP('0.0.0.0', self.port_broadcast, True)
        self.threads.append(Thread(
            target=self._broadcast_alive, args=(), daemon=True))
        self.threads[0].start()                     # start broadcast_alive
        self.threads.append(Thread(
            target=self.callback, args=(), daemon=True))        # start keep_alive listener
        self.threads[-1].start()
        self._read_stream()                                     # main loop reads stream

    class Device:
        ip = ''
        alive = False
        def __init__(self, ip, alive):
            self.alive = alive
            self.ip = ip

    def callback(self):
        while not self.repeat.wait(1):
            i = 0
            remove = False
            for device in self.connected_devices:
                if not device.alive:
                    print(
                        "client {0} has dropped his connection.".format(
                            device.ip))
                    remove = True
                    break
                i += 1

            if remove:
                self.connected_devices.pop(i)

            i = 0
            for i in range(len(self.connected_devices)):
                print("{0} is alive".format(self.connected_devices[i].ip))
                self.connected_devices[i].alive = False

    def _broadcast_alive(self):
        bits = self.ip.split('.')
        addr_bit = bits[0] + '.' + bits[1] + '.' + bits[2] + '.'
        #allips = [addr_bit + str(i) for i in range(2, 255)]
        allips = [addr_bit + str(255)]  # real broadcast
        while True:
            for ip in allips:
                try:
                    if not ip == self.ip:
                        self.sock_broadcast.sendto(
                            json.dumps(
                                self.alive).encode(), (ip, self.port_broadcast))
                        time.sleep(0.5)
                except BaseException as b:
                    print(b)
                    time.sleep(0.005)
                    pass

    def _read_stream(self):
        while True:
            try:
                bts, addr = self.sock_recieve.recvfrom(self.alive_size)
                msg = bts.decode()
                msg = json.loads(msg)
                if 'alive' in msg:
                    if msg['alive']:
                        i = 0
                        for device in self.connected_devices:
                            if device.ip == msg['ip']:
                                self.connected_devices[i].alive = True
                                break
                            i += 1
                if 'clientID' in msg:
                    self.sock_sub = init_socket_TCP('0.0.0.0', self.port_subscribe, True)
                    print("Sock_sub created")
                    self.sock_pub = init_socket_TCP('0.0.0.0', self.port_publish, True)
                    print("Sock_pub created")
                    self.connected_devices.append(self.Device(msg['ip'], True))
                    
                    bts = self.sock_pub.recv(1024) 
                    register = json.loads(bts.decode())
                    print(register)
            except socket.timeout:
                pass

            except Exception as e:
                print(e)
                pass


if __name__ == "__main__":
    s = Controler()
    s.run()
