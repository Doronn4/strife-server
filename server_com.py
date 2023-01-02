import socket
import select
import queue


class ServerCom:
    """
    Class that handles the communication between the server and the clients.
    """

    def __init__(self, server_port: int, message_queue: queue.Queue):
        """
        Creates a server object for communicating with clients
        :param server_port: The server port
        :param message_queue: The message queue
        """
        self.FILE_CHUNK_SIZE = 4096
        self.port = server_port
        self.message_queue = message_queue
        self.socket = None
        self.open_clients = {}

    def _main(self):
        """
        The main loop of the server
        :return: -
        """
        # Create the socket
        self.socket = socket.socket()
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen(5)

        while True:
            rlist, wlist, xlist = select.select([self.socket] + list(self.open_clients.keys()),
                                                list(self.open_clients.keys()), [])
            for current_socket in rlist:
                if current_socket is self.socket:
                    # Connecting a new client
                    client, addr = self.socket.accept()
                    # Add the client to the dict of open clients
                    self.open_clients[client] = addr

                # A message has been sent from a client
                else:
                    try:
                        # Try to receive the size of the data
                        size = int(self.socket.recv(2).decode())
                        # Receive the data
                        data = self.socket.recv(size).decode()

                    # Handle exceptions
                    except ValueError:
                        self._close_client(current_socket)
                    except socket.error:
                        self._close_client(current_socket)

                    else:
                        if data == '':
                            # Client disconnected
                            self._close_client(current_socket)
                        else:
                            # Add the message to the queue
                            self.message_queue.put(data)

    def receive_file(self, from_addr, size: int):
        """
        Receive a file from a client
        :param from_addr: The addr of the client
        :param size: The size of the file
        :return: The file (as bytes)
        """
        # Get the client socket by his addr
        client_socket = [soc for soc, addr in self.open_clients.items() if addr == from_addr][0]

        # Initialize an empty bytearray to store the file data
        file_data = bytearray()

        # Keep receiving data until the entire file has been received
        while len(file_data) < size:
            try:
                chunk = client_socket.recv(self.FILE_CHUNK_SIZE)
            # Handle exceptions
            except socket.error:
                file_data = None
                self._close_client(client_socket)
                break
            else:
                if not chunk:
                    break
                file_data += chunk

        return file_data

    def send_data(self, data: bytes, dst_addr):
        # A list of the sockets that had the message sent to them
        sent_to = []
        # Make the dst_addr a list
        if type(dst_addr) != list:
            dst_addr = [dst_addr]

        # send the data to all clients, run while loop until all the data is sent to all clients
        while len(sent_to) < len(dst_addr):
            for soc in self.open_clients.keys():
                # if the client is in the list of ips to send to
                if self.open_clients[soc] in dst_addr and self.open_clients[soc] not in sent_to:
                    try:
                        # send the length of the data first (2 bytes)
                        soc.send(str(len(data)).zfill(2).encode())
                        # send the data
                        soc.send(data)
                        sent_to.append(self.open_clients[soc])
                    except socket.error:
                        # close the client, remove it from the list of open clients
                        # and remove it from the list of ips to send to
                        dst_addr.remove(self.open_clients[soc])
                        self._close_client(soc)
                        break

    def _close_client(self, client_socket: socket.socket):
        """
        Closes the connection with a client
        :param client_socket: the client socket to disconnect
        :return: -
        """
        if client_socket in self.open_clients.keys():
            del self.open_clients[client_socket]

        client_socket.close()

    def is_connected(self, client_addr):
        """
        Checks if a client is connected
        :param client_addr: The address of the client
        :return: If the client is connected
        """
        return client_addr in self.open_clients.values()

