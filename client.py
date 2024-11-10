import socket
import threading
import argparse
import os
import sys
import tkinter as tk

class Send(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        while True:
            message = input(f'{self.name}: ')  # Sử dụng input trực tiếp
            if message.upper() == "QUIT":
                self.sock.sendall(f'Server: {self.name} has left the chat.'.encode('ascii'))
                break
            self.sock.sendall(f'{self.name}: {message}'.encode('ascii'))

        print('\nQuitting...')
        self.sock.close()
        os._exit(0)

class Receive(threading.Thread):
    def __init__(self, sock, messages):
        super().__init__()
        self.sock = sock
        self.messages = messages

    def run(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('ascii')
                if message:
                    self.messages.insert(tk.END, message)
                    print(f'\r{message}\n', end='')
                else:
                    raise ConnectionError("Connection lost.")
            except (ConnectionError, OSError):
                print('\nNo. We have lost connection to the server!')
                print('\nQuitting...')
                self.sock.close()
                os._exit(0)

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None

    def start(self):
        print(f'Trying to connect to {self.host}:{self.port}...')
        self.sock.connect((self.host, self.port))
        print(f'Successfully connected to {self.host}:{self.port}')

        self.name = input('Your name: ')
        print(f'Welcome, {self.name}! Getting ready to send and receive messages...')

        send_thread = Send(self.sock, self.name)
        receive_thread = Receive(self.sock, self.messages)

        send_thread.start()
        receive_thread.start()

        self.sock.sendall(f'Server: {self.name} has joined the chat. Say "what\'s up!"'.encode('ascii'))
        print("\rReady! Leave the chatroom by typing 'QUIT'.")
        return receive_thread

    def send(self, textInput):
        message = textInput.get()
        textInput.delete(0, tk.END)
        self.messages.insert(tk.END, f'{self.name}: {message}')

        if message.upper() == "QUIT":
            self.sock.sendall(f'Server: {self.name} has left the chat.'.encode('ascii'))
            print('\nQuitting...')
            self.sock.close()
            os._exit(0)
        else:
            self.sock.sendall(f'{self.name}: {message}'.encode('ascii'))

def main(host, port):
    client = Client(host, port)
    receive_thread = client.start()

    window = tk.Tk()
    window.title("Chatroom")

    fromMessage = tk.Frame(master=window)
    scrollBar = tk.Scrollbar(master=fromMessage)
    messages = tk.Listbox(master=fromMessage, yscrollcommand=scrollBar.set)
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    client.messages = messages
    receive_thread.messages = messages

    fromMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)

    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind("<Return>", lambda x: client.send(textInput))
    textInput.insert(0, "Write your message here.")

    btnSend = tk.Button(
        master=window,
        text='Send',
        command=lambda: client.send(textInput)
    )

    fromEntry.grid(row=1, column=0, padx=10, sticky="ew")
    btnSend.grid(row=1, column=1, padx=10, sticky="ew")

    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=100, weight=0)

    window.mainloop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chatroom Client")
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port (default 1060)')

    args = parser.parse_args()
    main(args.host, args.p)