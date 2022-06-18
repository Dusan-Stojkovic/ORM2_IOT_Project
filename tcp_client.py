from networking import init_socket_TCP, get_ip

if __name__ == "__main__":
    print("Client testing")
    sock = init_socket_TCP('192.168.43.92', 15000, False)
    while True:
        sock.send("test".encode())
