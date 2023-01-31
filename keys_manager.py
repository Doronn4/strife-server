from cryptions import RSACipher
import rsa


class KeysManager:
    """
    Class for managing keys of the clients and the server.
    """
    def __init__(self):
        """
        Initializes the clients_keys dictionary, generates public and private keys.
        """
        self.clients_keys = {}
        self.public_key = None
        self.private_key = None

        self._generate_keys()

    def _generate_keys(self):
        """
        Generates public and private keys of the server.
        """
        self.public_key, self.private_key = rsa.newkeys(RSACipher.KEY_SIZE)

    def get_client_key(self, username):
        return self.clients_keys.get(username)

    def set_client_key(self, username, key):
        self.clients_keys[username] = key
