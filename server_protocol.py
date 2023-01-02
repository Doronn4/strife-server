class Protocol:
    """
    A class for creating and deconstructing messages (server side) according to the protocol
    """

    def __init__(self):
        # A char for separating fields in the message
        self.FIELD_SEPARATOR = '@'
        # A chat for separating items in a list of items in a field
        self.LIST_SEPARATOR = '$'

        # Opcodes to construct messages (server -> client)
        self.general_opcodes = {
            'approve_reject': 1,
            'friend_request': 2,
            'added_to_group': 3,
            'voice_call_started': 5,
            'video_call_started': 6,
            'voice_call_info': 7,
            'video_call_info': 8,
            'voice_user_joined': 9,
            'video_user_joined': 10,
            'chats_list': 11,
            'group_members': 12,
            'user_status': 13,
            'friend_added': 14
        }
        self.chat_opcodes = {
            'text_message': 1,
            'file_description': 2
        }
        self.files_opcodes = {
            'file_in_chat': 1,
            'user_profile_picture': 2
        }

        # Opcodes to read messages (client -> server)
        self.c_general_opcodes = {
            'register': 1,
            'sign_in': 2,
            'add_friend': 3,
            'create_group': 4,
            'start_voice': 5,
            'start_video': 6,
            'change_username': 7,
            'change_status': 8,
            'change_password': 9,
            'get_chat_history': 10,
            'request_file': 11,
            'remove_friend': 12,
            'join_voice': 13,
            'join_video': 14,
            'add_group_member': 15,
            'request_group_members': 16,
            'request_user_picture': 17,
            'request_user_status': 18,
            'request_chats': 19
        }
        self.c_chat_opcodes = {
            'text_message': 1,
            'file_description': 2
        }
        self.c_files_opcodes = {
            'file_in_chat': 1,
            'profile_pic_change': 2
        }

        # Parameters of every message from the client
        self.c_opcodes_params = {

        }

    def approve(self, target_opcode):
        # Get the opcode of register
        opcode = self.general_opcodes['approve_reject']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{int(True)}{self.FIELD_SEPARATOR}{target_opcode}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def reject(self, target_opcode):
        # Get the opcode of register
        opcode = self.general_opcodes['approve_reject']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{int(False)}{self.FIELD_SEPARATOR}{target_opcode}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def friend_request_notify(self, sender_username):
        # Get the opcode of register
        opcode = self.general_opcodes['friend_request']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{sender_username}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def added_to_group(self, group_name, chat_id, key):
        # Get the opcode of register
        opcode = self.general_opcodes['friend_request']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{group_name}" \
              f"{self.FIELD_SEPARATOR}{chat_id}{self.FIELD_SEPARATOR}{key}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def voice_started(self, chat_id):
        # Get the opcode of register
        opcode = self.general_opcodes['voice_call_started']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def video_started(self, chat_id):
        # Get the opcode of register
        opcode = self.general_opcodes['video_call_started']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def voice_call_info(self, chat_id, ips, usernames):
        # Get the opcode of register
        opcode = self.general_opcodes['voice_call_info']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}{self.FIELD_SEPARATOR}"
        # Add the ips to the message
        for ip in ips:
            msg += self.LIST_SEPARATOR + ip
        # Add the usernames to the message
        for username in usernames:
            msg += self.LIST_SEPARATOR + username
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def video_call_info(self, chat_id, ips, usernames):
        # Get the opcode of register
        opcode = self.general_opcodes['video_call_info']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}{self.FIELD_SEPARATOR}"
        # Add the ips to the message
        for ip in ips:
            msg += self.LIST_SEPARATOR + ip
        # Add the usernames to the message
        for username in usernames:
            msg += self.LIST_SEPARATOR + username
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def voice_user_joined(self, chat_id, user_ip, username):
        # Get the opcode of register
        opcode = self.general_opcodes['voice_user_joined']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}" \
              f"{self.FIELD_SEPARATOR}{user_ip}{self.FIELD_SEPARATOR}{username}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def video_user_joined(self, chat_id, user_ip, username):
        # Get the opcode of register
        opcode = self.general_opcodes['video_user_joined']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}" \
              f"{self.FIELD_SEPARATOR}{user_ip}{self.FIELD_SEPARATOR}{username}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def chats_list(self, chats):
        pass

    def group_names(self, chat_id, usernames):
        # Get the opcode of register
        opcode = self.general_opcodes['group_members']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}"
        # Add the usernames list
        for username in usernames:
            msg += self.LIST_SEPARATOR + username
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def user_status(self, username, status):
        # Get the opcode of register
        opcode = self.general_opcodes['user_status']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{username}{self.FIELD_SEPARATOR}{status}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def friend_added(self, friend_username):
        # Get the opcode of register
        opcode = self.general_opcodes['friend_added']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{friend_username}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def send_file(self, chat_id, file_name, file):
        # Get the opcode of register
        kind = self.files_opcodes['send_file']
        # Construct the message
        msg = f"{kind}{self.FIELD_SEPARATOR}{len(file)}{self.FIELD_SEPARATOR}{chat_id}" \
              f"{self.FIELD_SEPARATOR}{file_name}{self.FIELD_SEPARATOR}{file}"
        # The message size
        size = len(msg) - len(file)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def profile_picture(self, profile_username, image):
        # Get the opcode of register
        kind = self.files_opcodes['send_file']
        # Construct the message
        msg = f"{kind}{self.FIELD_SEPARATOR}{len(image)}{self.FIELD_SEPARATOR}{profile_username}" \
              f"{self.FIELD_SEPARATOR}{image}"
        # The message size
        size = len(msg) - len(image)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def unprotocol_msg(self, type, raw_message):
        # Split the message into it's fields with the field separator
        values = raw_message.split(self.FIELD_SEPARATOR)

        # Get the opcode of the message
        opcode = int(values[0])
        values = values[1:]

        # The returned dict
        ret = {}

