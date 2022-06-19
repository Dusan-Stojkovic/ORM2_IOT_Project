import time
from topic_message import TopicMessage
from threading import Thread
from sys import getsizeof
from networking import init_socket_UDP, get_ip, init_socket_TCP
import json
import socket
from broker import subscribe_listener
import cv2

class Monitoring():
    def __init__(self):
        self.id = 80
        self.server_alive = False
        self.connected = False
        self.port_subscribe = 45002
        self.port_publish = 45003
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

    def repl(self):
        command = ""
        prompt = ">> "
        while command != "exit":
            print(">> ", end = '')
            command = input()
            if command == "print":
                with open("log_monitor.txt", 'r') as file:
                    lines = file.readlines()
                    for i in range(-5, 0):
                        # have a bug here, careful not to kill this thread
                        try:
                            print(lines[i])
                        except Exception as e:
                            print(e)
                            pass
            elif command == "stop":
                # publish stop 
                stop_message = TopicMessage({
                    'type': "publish",
                    'id': self.id,
                    'ip': self.ip,
                    'topic': "/monitor/stop",
                    'value': True,
                    'value_type': "bool"
                }).toJSON()
                self.sock_pub.send(stop_message.encode())
            elif command == "go":
                go_message = TopicMessage({
                    'type': "publish",
                    'id': self.id,
                    'ip': self.ip,
                    'topic': "/monitor/start",
                    'value': True,
                    'value_type': "bool"
                    }).toJSON()
                self.sock_pub.send(go_message.encode())


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
                #if self.server_alive:
                #    print(
                #        "SERVER IS ALIVE ON IP: {0}, PORT: {1}".format(
                #            self.serverIp,
                #            self.port_recieve))
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

                    self.sock_pub = init_socket_TCP('0.0.0.0', self.port_publish, True)
                    print("Sock_sub created")
                    self.sock_sub = init_socket_TCP('0.0.0.0', self.port_subscribe, True)
                    print("Sock_pub created")

                    register = TopicMessage({
                        'type': "register",
                        'id': self.id,
                        'ip': self.ip, 
                        'attributes': {
                            'manual': False,
                            'actuators': [],
                            'sensors': ["keyboard"]},
                        'topics': ["/automobile/accel",
                            "/automobile/steer",
                            "/automobile/camera"]
                        }).toJSON()

                    self.sock_sub.send(register.encode())

                    # TODO make a thread to listen for data
                    self.threads.append(
                        Thread(
                            target=lambda: subscribe_listener(self.sock_sub, display),
                            daemon=True
                        )
                    )
                    self.threads[-1].start()
                    self.threads.append(Thread(
                        target=lambda: self.repl(),
                        daemon=True
                    ))
                    self.threads[-1].start()
            except Exception as e:
                # Reinitialize the socket for reconnecting to controler.
                print(e)
                self.connected = False
                pass

#TODO make this display cleaner
def display(data):
    print(data['value_type'])
    if data['value_type'] == "float":
        with open("log_monitor.txt", 'a') as file:
            file.write(str(data) + '\n')
    elif data['value_type'] == "Image":
        print("here")
        imdata = base64.b64decode(load['value'])
        image = cv2.open(imdata)
        cv2.imshow(image)
        cv2.waitKey(0)

if __name__ == "__main__":
    c = Monitoring()
    c.run()
