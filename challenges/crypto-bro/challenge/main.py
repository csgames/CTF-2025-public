import argparse
import select
import socket
import os

def main():
    FLAG = os.environ.get("FLAG", "FLAG").encode()

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Listen host", default="0.0.0.0")
    parser.add_argument("--port", type=int, help="Listen port", default=10000)
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((args.host, args.port))
        s.listen(5)
        s.setblocking(False)

        sockets_list = [s]
        clients = {}

        print(f"Running at {args.host}:{args.port}")

        while True:
            readable, writable, exceptional = select.select(sockets_list, [], sockets_list)

            for sock in readable:
                if sock is s:
                    # Handle new incoming connection
                    client_socket, addr = s.accept()
                    client_socket.setblocking(False)
                    sockets_list.append(client_socket)
                    clients[client_socket] = addr

                    client_socket.send(b"Message: ")
                else:
                    # Handle incoming data from a client
                    try:
                        data = sock.recv(1024).rstrip()
                        if data:
                            resp = bytes([a ^ b for a, b in zip(data, FLAG * (1 + len(data) // len(FLAG)))])
                            sock.sendall(b"Encryption: " + resp.hex().encode() + b"\nMessage: ")
                        else:
                            # Connection closed
                            sockets_list.remove(sock)
                            del clients[sock]
                            sock.close()
                    except Exception as e:
                        print("Error:", e)

            for sock in exceptional:
                # Handle exceptional conditions
                sockets_list.remove(sock)
                del clients[sock]
                sock.close()

if __name__ == "__main__":
    main()
