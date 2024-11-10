# import socket
# import threading
# import argparse
# import os

# class Server(threading.Thread):
#     def __init__(self, host, port):
#         super().__init__()
#         self.connections = []
#         self.host = host
#         self.port = port

#     def run(self):
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         sock.bind((self.host, self.port))

#         sock.listen(1)
#         print("Listening at", sock.getsockname())

#         while True:
#             # Accepting new connection
#             sc, sockname = sock.accept()
#             print(f"Accepting a new connection from {sc.getpeername()} to {sc.getsockname()}")

#             # Create a new thread
#             server_socket = ServerSocket(sc, sockname, self)

#             # Start new thread
#             server_socket.start()

#             # Add thread to active connections
#             self.connections.append(server_socket)
#             print("Ready to receive message from", sc.getpeername())

#     def broadcast(self, message, source):
#         for connection in self.connections:
#             # Send to all connected clients except the source client
#             if connection.sockname != source:
#                 connection.send(message)

#     def remove_connection(self, connection):
#         self.connections.remove(connection)

# class ServerSocket(threading.Thread):
#     def __init__(self, sc, sockname, server):
#         super().__init__()
#         self.sc = sc
#         self.sockname = sockname
#         self.server = server

#     def run(self):
#         while True:
#             message = self.sc.recv(1024).decode('ascii')

#             if message:
#                 print(f"{self.sockname} says: {message}")
#                 self.server.broadcast(message, self.sockname)
#             else:
#                 print(f"{self.sockname} has closed the connection")
#                 self.sc.close()
#                 server.remove_connection(self)
#                 return

#     def send(self, message):
#         self.sc.sendall(message.encode('ascii'))

# def exit_server(server):
#     while True:
#         ipt = input("")
#         if ipt == "q":
#             print("Closing all connections...")
#             for connection in server.connections:
#                 connection.sc.close()
#             print("Shutting down the server...")
#             os._exit(0)  # Use os._exit to terminate the process

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description="Chatroom Server")
#     parser.add_argument('host', help='Interface the server listens at')
#     parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port (default 1060)')

#     args = parser.parse_args()

#     # Create and start server thread
#     server = Server(args.host, args.p)
#     server.start()

#     exit = threading.Thread(target=exit_server, args=(server,))
#     exit.start()
import socket
import threading
import argparse
import os

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(5)  # Cho phép nhiều kết nối
        print("Listening at", sock.getsockname())

        while True:
            # Accepting new connection
            sc, sockname = sock.accept()
            print(f"Accepting a new connection from {sc.getpeername()} to {sc.getsockname()}")

            # Create and start a new thread for the connection
            server_socket = ServerSocket(sc, sockname, self)
            server_socket.start()

            # Add thread to active connections
            self.connections.append(server_socket)
            print("Ready to receive message from", sc.getpeername())

    def broadcast(self, message, source):
        """Send message to all connected clients except the source."""
        for connection in self.connections:
            if connection.sockname != source:
                connection.send(message)

    def remove_connection(self, connection):
        """Remove a connection from the active list."""
        self.connections.remove(connection)

class ServerSocket(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server

    def run(self):
        while True:
            try:
                message = self.sc.recv(1024).decode('ascii')

                if message:
                    print(f"{self.sockname} says: {message}")
                    self.server.broadcast(message, self.sockname)
                else:
                    raise ConnectionError("Connection closed by the client.")
            except (ConnectionError, OSError):
                print(f"{self.sockname} has closed the connection")
                self.sc.close()
                self.server.remove_connection(self)
                return

    def send(self, message):
        self.sc.sendall(message.encode('ascii'))

def exit_server(server):
    """Handle server shutdown command."""
    while True:
        if input("") == "q":
            print("Closing all connections...")
            for connection in server.connections:
                connection.sc.close()
            print("Shutting down the server...")
            os._exit(0)  # Use os._exit to terminate the process

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chatroom Server")
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port (default 1060)')

    args = parser.parse_args()

    # Create and start server thread
    server = Server(args.host, args.p)
    server.start()

    # Start a thread to handle server exit
    exit_thread = threading.Thread(target=exit_server, args=(server,))
    exit_thread.start()