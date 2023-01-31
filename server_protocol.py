class Protocol:
    """
    A class for creating and deconstructing messages (server side) according to the protocol
    """

    def __init__(self):
        # A char for separating fields in the message
        self.FIELD_SEPARATOR = '@'
        # A chat for separating items in a list of items in a field
        self.LIST_SEPARATOR = '#'

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
        """
        Constructs an approve msg with the protocol
        :param target_opcode:
        :return:
        """
        # Get the opcode of register
        opcode = self.general_opcodes['approve_reject']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{int(True)}{self.FIELD_SEPARATOR}{target_opcode}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def reject(self, target_opcode):
        """
        Constructs an approve msg with the protocol
        :param target_opcode:
        :return:
        """
        # Get the opcode of register
        opcode = self.general_opcodes['approve_reject']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{int(False)}{self.FIELD_SEPARATOR}{target_opcode}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def friend_request_notify(self, sender_username):
        """
        Constructs an approve msg with the protocol
        :param sender_username:
        :return:
        """
        # Get the opcode of register
        opcode = self.general_opcodes['friend_request']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{sender_username}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def added_to_group(self, group_name, chat_id, key):
        """
        Constructs an approve msg with the protocol
        :param group_name:
        :param chat_id:
        :param key:
        :return:
        """
        # Get the opcode of register
        opcode = self.general_opcodes['added_to_group']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{group_name}" \
              f"{self.FIELD_SEPARATOR}{chat_id}{self.FIELD_SEPARATOR}{key}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def voice_started(self, chat_id):
        """
        Constructs an approve msg with the protocol
        :param chat_id:
        :return:
        """
        # Get the opcode of register
        opcode = self.general_opcodes['voice_call_started']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def video_started(self, chat_id):
        """
        Constructs an approve msg with the protocol
        :param chat_id:
        :return:
        """
        # Get the opcode of register
        opcode = self.general_opcodes['video_call_started']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def voice_call_info(self, chat_id, ips, usernames):
        """

        :param chat_id:
        :param ips:
        :param usernames:
        :return:
        """
        # Get the opcode of register
        opcode = self.general_opcodes['voice_call_info']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}{self.FIELD_SEPARATOR}"
        # Add the first ip
        msg += ips[0]
        # Add the ips to the message
        for ip in ips[1:]:
            msg += self.LIST_SEPARATOR + ip
        # Separate the fields
        msg += self.FIELD_SEPARATOR
        # Add the first username
        msg += usernames[0]
        # Add the usernames to the message
        for username in usernames[1:]:
            msg += self.LIST_SEPARATOR + username
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def video_call_info(self, chat_id, ips, usernames):
        """

        :param chat_id:
        :param ips:
        :param usernames:
        :return:
        """
        # Get the opcode of register
        opcode = self.general_opcodes['video_call_info']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}{self.FIELD_SEPARATOR}"
        # Add the first ip
        msg += ips[0]
        # Add the ips to the message
        for ip in ips[1:]:
            msg += self.LIST_SEPARATOR + ip
        # Separate the fields
        msg += self.FIELD_SEPARATOR
        # Add the first username
        msg += usernames[0]
        # Add the usernames to the message
        for username in usernames[1:]:
            msg += self.LIST_SEPARATOR + username
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def voice_user_joined(self, chat_id, user_ip, username):
        """

        :param chat_id:
        :param user_ip:
        :param username:
        :return:
        """
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
        """

        :param chat_id:
        :param user_ip:
        :param username:
        :return:
        """
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
        """

        :param chat_id:
        :param usernames:
        :return:
        """
        # Get the opcode of register
        opcode = self.general_opcodes['group_members']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}{self.FIELD_SEPARATOR}"
        # Add the first username
        msg += usernames[0]
        # Add the usernames list
        for username in usernames[1:]:
            msg += self.LIST_SEPARATOR + username
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def user_status(self, username, status):
        """

        :param username:
        :param status:
        :return:
        """
        # Get the opcode of register
        opcode = self.general_opcodes['user_status']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{username}{self.FIELD_SEPARATOR}{status}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def friend_added(self, friend_username):
        """

        :param friend_username:
        :return:
        """
        # Get the opcode of register
        opcode = self.general_opcodes['friend_added']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{friend_username}"
        # The message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def send_file(self, chat_id, file_name, file):
        """

        :param chat_id:
        :param file_name:
        :param file:
        :return:
        """
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
        """

        :param profile_username:
        :param image:
        :return:
        """
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
        """
        Deconstructs a message received from the client with the client-server's protocol
        :param type:
        :param raw_message:
        :return:
        """
        # Split the message into it's fields with the field separator
        values = raw_message.split(self.FIELD_SEPARATOR)

        # Get the opcode of the message
        opcode = int(values[0])
        values = values[1:]

        # The returned dict
        ret = {}

        # If the message was received in the general messages channel
        if type == 'general':
            # The first value in the dict is the opcode's name (opname)
            opcode_name = self.c_general_opcodes[opcode]
            ret['opname'] = opcode_name

        # If the message was received in the chat messages channel
        elif type == 'chat':
            # The first value in the dict is the opcode's name (opname)
            opcode_name = self.c_chat_opcodes[opcode]
            ret['opname'] = opcode_name

        # If the message was received in the files messages channel
        elif type == 'files':
            # The first value in the dict is the opcode's name (opname)
            opcode_name = self.c_files_opcodes[opcode]
            ret['opname'] = opcode_name

        # Get the parameters names of the message
        params_names = self.c_opcodes_params[self.c_general_opcodes[opcode]]

        # Assign a value for each parameter in a dict
        for i in range(len(values)):
            value = values[i]
            param_name = params_names[i]

            # If the value is a list
            if len(value.split(self.LIST_SEPARATOR)) > 1:
                # Check if the list is of integers
                if value.split(self.LIST_SEPARATOR)[0].isnumeric():
                    ret[param_name] = [int(v) for v in value.split(self.LIST_SEPARATOR)]
                else:
                    ret[param_name] = value.split(self.LIST_SEPARATOR)

            # If the value isn't a list
            else:
                # Check if the value is an integer
                if value.isnumeric():
                    ret[param_name] = int(value)
                else:
                    ret[param_name] = value
        return ret

