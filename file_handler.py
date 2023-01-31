import os
from io import BytesIO
from PIL import Image


class FileHandler:
    def __init__(self, base_path):
        """
        Initializes the FileHandler class with a given base path.

        :param base_path: the base directory path.
        """

        self.PFP_SIZE = (100, 100)
        self.base_path = base_path
        self.PFPS_PATH = '\\user-profiles'
        self.CHATS_PATH = '\\chats'
        self._create_folders()

    def _create_folders(self):
        """
        Creates the necessary folders to store PFPs and chats, if they don't already exist.
        """

        if not os.path.exists(self.base_path+self.PFPS_PATH):
            os.mkdir(self.base_path+self.PFPS_PATH)

        if not os.path.exists(self.base_path+self.CHATS_PATH):
            os.mkdir(self.base_path+self.CHATS_PATH)

    def save_pfp(self, contents: bytes, username: str):
        """
        Saves a profile picture in the base_path/user-profiles folder, with the file name "user-<username>.png".

        :param contents: the binary contents of the image file.
        :param username: the username of the profile picture's owner.
        """

        resized_pfp = self._resize_image(contents)
        with open(f'{self.base_path}{self.PFPS_PATH}\\user-{username}.png', 'wb') as f:
            f.write(resized_pfp)

    def load_pfp(self, username):
        """
        Loads a profile picture from the base_path/user-profiles folder.

        :param username: the username of the profile picture's owner.
        :return: the binary contents of the image file.
        """

        with open(f'{self.base_path}{self.PFPS_PATH}\\user-{username}.png', 'rb') as f:
            picture = f.read()
        return picture

    def save_file(self, contents: bytes, chat_id: int, file_name: str):
        """
        Saves a file in the base_path/chats/<chat_id> folder.

        :param contents: the binary contents of the file.
        :param chat_id: the id of the chat associated with the file.
        :param file_name: the name of the file.
        """

        with open(f'{self.base_path}{self.CHATS_PATH}\\{chat_id}\\{file_name}', 'wb') as f:
            f.write(contents)

    def create_chat(self, chat_id):
        """
        Creates a folder for a chat in the base_path/chats folder.

        :param chat_id: the id of the chat.
        """

        dir_path = f'{self.base_path}{self.CHATS_PATH}\\{chat_id}'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

    def _resize_image(self, image_bytes: bytes):
        """
        Resizes an image to the size specified in PFP_SIZE.

        :param image_bytes: the binary contents of the image file.
        :return: the binary contents of the resized image file.
        """

        # Open image from bytes
        image = Image.open(BytesIO(image_bytes))

        # Resize image
        image = image.resize(self.PFP_SIZE)

        # Save image to bytes
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()


if __name__ == '__main__':
    my = FileHandler('C:\\Users\doron\Desktop\\testdir')
    my.create_chat(69)
    with open("C:\\Users\doron\Pictures\\2.jpeg", 'rb') as f:
        my.save_pfp(f.read(), 'gabzo')
