import os
from io import BytesIO
from pathlib import Path

from PIL import Image


class FileHandler:
    """
    A class that handles the saving and loading of files.
    """
    
    PFP_SIZE = (300, 300)
    PFPS_PATH = '\\user-profiles'
    CHATS_PATH = '\\chats'

    script_path = None
    base_path = None

    @staticmethod
    def initialize():
        """
        Initializes the FileHandler class with a given base path.
        """
        script_path = Path(os.path.abspath(__file__))
        FileHandler.base_path = str(script_path.parent.parent.parent)+"\\data"

        FileHandler._create_folders()

    @staticmethod
    def _create_folders():
        """
        Creates the necessary folders to store PFPs and chats, if they don't already exist.
        """
        if not os.path.exists(FileHandler.base_path+FileHandler.PFPS_PATH):
            os.mkdir(FileHandler.base_path+FileHandler.PFPS_PATH)

        if not os.path.exists(FileHandler.base_path+FileHandler.CHATS_PATH):
            os.mkdir(FileHandler.base_path+FileHandler.CHATS_PATH)

    @staticmethod
    def save_pfp(contents: bytes, username: str):
        """
        Saves a profile picture in the base_path/user-profiles folder, with the file name "user-<username>.png".

        :param contents: the binary contents of the image file.
        :param username: the username of the profile picture's owner.
        """

        resized_pfp = FileHandler._resize_image(contents)
        try:
            with open(f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\user-{username}.png', 'wb') as f:
                f.write(resized_pfp)
        except Exception:
            return None

        return f'user-{username}.png'

    @staticmethod
    def load_pfp(username=None, path=None):
        """
        Loads a profile picture from the base_path/user-profiles folder.

        :param path:
        :type path:
        :param username: the username of the profile picture's owner.
        :return: the binary contents of the image file.
        """
        if username:
            with open(f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\user-{username}.png', 'rb') as f:
                picture = f.read()
        if path:
            with open(f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\{path}', 'rb') as f:
                picture = f.read()
        else:
            picture = None

        return picture

    @staticmethod
    def save_file(contents: bytes, chat_id: int, file_name: str):
        """
        Saves a file in the base_path/chats/<chat_id> folder.

        :param contents: the binary contents of the file.
        :param chat_id: the id of the chat associated with the file.
        :param file_name: the name of the file.
        """
        with open(f'{FileHandler.base_path}{FileHandler.CHATS_PATH}\\{chat_id}\\{file_name}', 'wb') as f:
            f.write(contents)

    @staticmethod
    def load_file(chat_id: int, file_name: str):
        """
        Loads a file from the base_path/chats/<chat_id> folder.

        :param chat_id: the id of the chat associated with the file.
        :param file_name: the name of the file.
        """

        contents = None
        # Check if the filepath exists
        if os.path.exists(f'{FileHandler.base_path}{FileHandler.CHATS_PATH}\\{chat_id}\\{file_name}'):
            # Read the file
            with open(f'{FileHandler.base_path}{FileHandler.CHATS_PATH}\\{chat_id}\\{file_name}', 'rb') as f:
                contents = f.read()

        return contents

    @staticmethod
    def create_chat(chat_id):
        """
        Creates a folder for a chat in the base_path/chats folder.

        :param chat_id: the id of the chat.
        """

        dir_path = f'{FileHandler.base_path}{FileHandler.CHATS_PATH}\\{chat_id}'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

    @staticmethod
    def _resize_image(image_bytes: bytes):
        """
        Resizes an image to the size specified in PFP_SIZE.

        :param image_bytes: the binary contents of the image file.
        :return: the binary contents of the resized image file.
        """

        # Open image from bytes
        image = Image.open(BytesIO(image_bytes))

        # Resize image
        image = image.resize(FileHandler.PFP_SIZE)

        # Save image to bytes
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
