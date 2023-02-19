from code.core.keys_manager import KeysManager
from code.handlers.file_handler import FileHandler


def init_all():
    KeysManager.initialize()
    FileHandler.initialize()
