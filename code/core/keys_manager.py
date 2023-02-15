from cryptions import RSACipher
import rsa


class KeysManager:
    """
    Class for managing keys of the clients and the server.
    """
    clients_keys = {}
    public_key = None
    private_key = None

    @staticmethod
    def initialize():
        """
         generates public and private keys.
        """
        KeysManager._generate_keys()

    @staticmethod
    def _generate_keys():
        """
        Generates public and private keys of the server.
        """
        KeysManager.public_key, KeysManager.private_key = rsa.newkeys(RSACipher.KEY_SIZE)

    @staticmethod
    def get_client_key(username):
        return KeysManager.clients_keys.get(username)

    @staticmethod
    def set_client_key(username, key):
        KeysManager.clients_keys[username] = key
