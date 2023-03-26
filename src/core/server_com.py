import socket
import select
import queue
import threading
from src.core.cryptions import RSACipher, AESCipher


class ServerCom:
    """
    Class that handles the communication between the server and the clients.
    """

    def __init__(self, server_port: int, message_queue: queue.Queue, com_type: str = 'general', log=False):
        """
        Creates a server object for communicating with clients
        :param server_port: The server port
        :param message_queue: The message queue
        """
        self.FILE_CHUNK_SIZE = 4096  # The chunk size to send when sending files
        self.port = server_port  # The server's port
        self.message_queue = message_queue  # The message queue of the server
        self.socket = None  # The socket of the server
        self.open_clients = {}  # [soc]:[ip, key]
        self.rsa = RSACipher()  # The RSA encryption and decryption object
        self.com_type = com_type
        self.clients_keys = {}
        self.log = log

        # Start the main loop in a thread
        threading.Thread(target=self._main).start()

    def _main(self):
        """
        The main loop of the server
        :return: -
        """
        # Create the socket
        self.socket = socket.socket()
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen(4)

        while True:
            rlist, wlist, xlist = select.select([self.socket] + list(self.open_clients.keys()),
                                                list(self.open_clients.keys()), [], 0.03)
            for current_socket in rlist:
                if current_socket is self.socket:
                    # Connecting a new client
                    client, addr = self.socket.accept()
                    ip = addr[0]
                    if self.log:
                        print(f'{self.com_type.upper()}: new client trying to connect', ip)
                    # Start a thread to swap keys with the client
                    threading.Thread(target=self._change_keys, args=(client, addr[0],)).start()

                # A message has been sent from a client
                else:
                    try:
                        if self.com_type == 'files':
                            size = current_socket.recv(10).decode()
                        else:
                            # Receive the size of the data
                            size = current_socket.recv(4).decode()
                        # Convert the size to int
                        size = int(size)

                        # Receive the data
                        if size > 1024:
                            data = self.receive_file(size, current_socket)
                        else:
                            data = current_socket.recv(size)

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
                            try:
                                # Decrypt the data and decode it back to a string
                                dec_data = AESCipher.decrypt(self.open_clients[current_socket][1], data)
                            except Exception:
                                self._close_client(current_socket)
                            else:
                                # Add the message to the queue
                                self.message_queue.put((dec_data, self.open_clients[current_socket][0]))

    def _change_keys(self, client: socket.socket, ip: str):
        """
        Swaps public keys with a client and adds him to the open clients
        :param client: The client socket
        :param ip: The client's ip
        :return: -
        """
        try:
            # Get the server's public key in a string
            key = self.rsa.get_string_public_key()
            # Send the server's public key to the client
            client.send(key.encode())
            # Receive the client's public key and decode it into a string
            client_key = client.recv(1024).decode()
            # Convert the client's key from a string to a publicKey object
            client_rsa_key = client_key
            # Create a new aes key with the client
            aes_key = AESCipher.generate_key()
            enc_aes_key = self.rsa.encrypt(aes_key, client_rsa_key)
            # Send the key to the client
            client.send(enc_aes_key)

        except Exception as e:
            # Handle exceptions
            if self.log:
                print(f'{self.com_type.upper()}: Change keys with', ip, 'unsuccessful')
            self._close_client(client)

        else:
            # Add the client to the dict of connected clients and save his ip and public key
            self.open_clients[client] = [ip, aes_key]
            if self.log:
                print(f'{self.com_type.upper()}: Changed keys successfully with', ip)

    def receive_file(self, size: int, client_socket: socket.socket):
        """
        Receive a file from a client
        :param client_socket:
        :param size: The size of the file
        :return: The file (as bytes)
        """
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

    def _get_sock_by_ip(self, target_ip: str):
        """
        Find the socket that belongs to the target ip in the server's connected clients dict
        :param target_ip: The ip of the socket
        :return: The socket of the client
        """
        # Return value
        ret_sock = None

        # Loop over all the clients connected to the server
        for soc, (ip, key) in self.open_clients.items():
            # Check if the ip is the target ip
            if ip == target_ip:
                # Return the socket found
                ret_sock = soc
                break

        return ret_sock

    def send_data(self, data, dst_addr):
        """
        Send data to a client or a list of clients
        :param data: The data to send
        :param dst_addr: The destination ip
        :return: -
        """
        # Make the dst_addr a list
        if type(dst_addr) != list:
            dst_addr = [dst_addr]

        # Loop over all the ips to send to
        for ip in dst_addr:
            # The socket of the ip
            soc = self._get_sock_by_ip(ip)
            # Check if the socket is still connected to the server
            if soc and soc in self.open_clients.keys():
                try:
                    # encrypt the data
                    enc_data = AESCipher.encrypt(self.open_clients[soc][1], data).encode()
                    # Send the length of the data
                    soc.send(str(len(enc_data)).zfill(4).encode())
                    # send the encrypted data
                    soc.send(enc_data)
                except socket.error:
                    # close the client, remove it from the list of open clients
                    self._close_client(soc)

    def send_file(self, contents: bytes, dst_addr):
        """
        Send data to a client or a list of clients
        :param contents: The data to send
        :param dst_addr: The destination ip
        :return: -
        """
        # Make the dst_addr a list
        if type(dst_addr) != list:
            dst_addr = [dst_addr]

        # Loop over all of the ips to send to
        for ip in dst_addr:
            # The the socket of the ip
            soc = self._get_sock_by_ip(ip)
            # Check if the socket is still connected to the server
            if soc and soc in self.open_clients.keys():
                try:
                    # encrypt the data
                    enc_data = AESCipher.encrypt(self.open_clients[soc][1], contents).encode()
                    # Send the length of the data
                    soc.send(str(len(enc_data)).zfill(10).encode())
                    # send the encrypted data
                    soc.send(enc_data)
                except socket.error:
                    # close the client, remove it from the list of open clients
                    self._close_client(soc)

    def _close_client(self, client_socket: socket.socket):
        """
        Closes the connection with a client
        :param client_socket: the client socket to disconnect
        :return: -
        """

        if client_socket in self.open_clients.keys():
            if self.log:
                print(f'{self.com_type.upper()}: client disconnected', self.open_clients[client_socket][0])
            # Let the main program know that a user has disconnected by sending an empty message
            self.message_queue.put(('', self.open_clients[client_socket][0]))
            # Delete the user from the dict of open clients
            del self.open_clients[client_socket]

        client_socket.close()

    def is_connected(self, client_addr: str):
        """
        Checks if a client is connected
        :param client_addr: The address of the client
        :return: If the client is connected
        """
        flag = False
        for ip, key in self.open_clients.values():
            if ip == client_addr:
                flag = True
                break

        return flag
