import os
from io import BytesIO
from pathlib import Path

from PIL import Image


class FileHandler:
    
    PFP_SIZE = (100, 100)
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
        with open(f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\user-{username}.png', 'wb') as f:
            f.write(resized_pfp)

    @staticmethod
    def load_pfp(username):
        """
        Loads a profile picture from the base_path/user-profiles folder.

        :param username: the username of the profile picture's owner.
        :return: the binary contents of the image file.
        """

        with open(f'{FileHandler.base_path}{FileHandler.PFPS_PATH}\\user-{username}.png', 'rb') as f:
            picture = f.read()
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


if __name__ == '__main__':
    my = FileHandler
    FileHandler.initialize()
    my.create_chat(69)
    with open("C:\\Users\\doron\\Pictures\\2.jpeg", 'rb') as f:
        my.save_pfp(f.read(), 'gabzo')
