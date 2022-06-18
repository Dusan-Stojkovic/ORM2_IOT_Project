from threading import Thread, Event
import socket
import json
from topic_message import TopicMessage
from networking import init_socket_UDP, get_ip, init_socket_TCP
from sys import getsizeof
import time
from broker import Broker, subscribe_listener

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
        self.broker = Broker()

    def run(self):
        # basic udp sockets for discovery and keep alive 
        self.sock_recieve = init_socket_UDP('0.0.0.0', self.port_recieve, True)
        self.sock_broadcast = init_socket_UDP('0.0.0.0', self.port_broadcast, True)

        # thread to broadcast life
        self.threads.append(Thread(
            target=self._broadcast_alive, args=(), daemon=True))
        self.threads[0].start()                     

        # thread to listen for replys
        self.threads.append(Thread(
            target=self.callback, args=(), daemon=True))        
        self.threads[-1].start()


        # subscribe to car topics so that we can test that this shit works

        # start main register loop
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
                # print("{0} is alive".format(self.connected_devices[i].ip))
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
                    time.sleep(0.1)
                    self.sock_sub = init_socket_TCP(msg['ip'], self.port_subscribe, False)
                    time.sleep(0.1)
                    self.sock_pub = init_socket_TCP(msg['ip'], self.port_publish, False)
                    self.connected_devices.append(self.Device(msg['ip'], True))
                    
                    bts = self.sock_sub.recv(1024) 
                    register = json.loads(bts.decode())
                    print(register)
                    
                    self.broker.add_topics(self.sock_sub, register['topics'])
                     
                    self.threads.append(
                        Thread(
                            target=lambda: subscribe_listener(self.sock_sub, self.broker.notify_subscribers),
                            daemon=True
                        )
                    )
                    self.threads[-1].start()
                    print("broker listener thread started.")

            except socket.timeout:
                pass

            except Exception as e:
                print(e)
                pass

if __name__ == "__main__":
    s = Controler()
    s.run()
