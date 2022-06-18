from networking import init_socket_TCP, get_ip

if __name__ == "__main__":
    print("Server testing")
    sock = init_socket_TCP('0.0.0.0', 15000, True)
    while True:
        print(sock.recv(1024).decode())
