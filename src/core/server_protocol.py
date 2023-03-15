class Protocol:
    """
    A class for creating and deconstructing messages (server side) according to the protocol
    """
    # A char for separating fields in the message
    FIELD_SEPARATOR = '@'
    # A chat for separating items in a list of items in a field
    LIST_SEPARATOR = '#'

    # Opcodes to construct messages (server -> client)
    general_opcodes = {
        'approve_reject': 1,  # All
        'friend_request': 2,  # Friendlist
        'added_to_group': 3,  # Chats
        'voice_call_started': 4,  # Call
        'video_call_started': 5,  # Call
        'voice_call_info': 6,  # Call
        'video_call_info': 7,  # Call
        'voice_user_joined': 8,  # Call
        'video_user_joined': 9,  # Call
        'chats_list': 10,  # Chats
        'group_members': 11,  # Chats
        'user_status': 12,  # Chats
        'friend_added': 13  # Friendlst
    }
    chat_opcodes = {
        'text_message': 1,  # Chats
        'file_description': 2  # Chats
    }
    files_opcodes = {
        'file_in_chat': 1,  # Chats
        'user_profile_picture': 2  # Chats
    }

    # Opcodes to read messages (client -> server)
    c_general_opcodes = {
        1: 'register',
        2: 'sign_in',
        3: 'add_friend',
        4: 'create_group',
        5: 'start_voice',
        6: 'start_video',
        7: 'change_username',
        8: 'change_status',
        9: 'change_password',
        10: 'get_chat_history',
        11: 'request_file',
        12: 'remove_friend',
        13: 'join_voice',
        14: 'join_video',
        15: 'add_group_member',
        16: 'request_group_members',
        17: 'request_user_picture',
        18: 'request_user_status',
        19: 'request_chats'
    }
    c_chat_opcodes = {
        1: 'text_message',
        2: 'file_description'
    }
    c_files_opcodes = {
        1: 'file_in_chat',
        2: 'profile_pic_change'
    }

    # Parameters of every message from the client
    c_opcodes_params = {
        'register': ('username', 'password'),
        'sign_in': ('username', 'password'),
        'add_friend': ('friend_username',),
        'create_group': ('group_name',),
        'start_voice': ('chat_id',),
        'start_video': ('chat_id',),
        'change_username': ('new_username',),
        'change_status': ('new_status',),
        'change_password': ('old_password', 'new_password'),
        'get_chat_history': ('chat_id',),
        'request_file': ('file_hash',),
        'remove_friend': ('friend_username',),
        'join_voice': ('chat_id',),
        'join_video': ('chat_id',),
        'add_group_member': ('chat_id', 'new_member_username'),
        'request_group_members': ('chat_id',),
        'request_user_picture': ('pfp_username',),
        'request_user_status': ('username',),
        'request_chats': (),
        'text_message': ('chat_id', 'sender_username', 'message')
    }

    @staticmethod
    def approve(target_opcode):
        """
        Constructs an approve msg with the protocol
        :param target_opcode: the opcode of the operation that was approved
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['approve_reject']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{int(True)}{Protocol.FIELD_SEPARATOR}{target_opcode}"
        # Return the message after protocol
        return msg

    @staticmethod
    def reject(target_opcode):
        """
        Constructs a reject msg with the protocol
        :param target_opcode: the opcode of the operation that was rejected
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['approve_reject']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{int(False)}{Protocol.FIELD_SEPARATOR}{target_opcode}"
        return msg

    @staticmethod
    def friend_request_notify(sender_username):
        """
        Constructs a message to indicate that the user has received a friend request
        :param sender_username: The username of the requester
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['friend_request']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{sender_username}"
        # Return the message after protocol
        return msg

    @staticmethod
    def added_to_group(group_name, chat_id, key):
        """
        Constructs a message to indicate that the user has been added to a group
        :param group_name: The name of the group
        :param chat_id: The chat id of the group
        :param key: The group's aes key
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['added_to_group']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{group_name}" \
              f"{Protocol.FIELD_SEPARATOR}{chat_id}{Protocol.FIELD_SEPARATOR}{key}"
        # Return the message after protocol
        return msg

    @staticmethod
    def voice_started(chat_id):
        """

        :param chat_id:
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['voice_call_started']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}"
        # Return the message after protocol
        return msg

    @staticmethod
    def video_started(chat_id):
        """

        :param chat_id:
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['video_call_started']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}"
        # Return the message after protocol
        return msg

    @staticmethod
    def voice_call_info(chat_id, ips, usernames):
        """

        :param chat_id:
        :param ips:
        :param usernames:
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['voice_call_info']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}{Protocol.FIELD_SEPARATOR}"
        # Add the first ip
        msg += ips[0]
        # Add the ips to the message
        for ip in ips[1:]:
            msg += Protocol.LIST_SEPARATOR + ip
        # Separate the fields
        msg += Protocol.FIELD_SEPARATOR
        # Add the first username
        msg += usernames[0]
        # Add the usernames to the message
        for username in usernames[1:]:
            msg += Protocol.LIST_SEPARATOR + username
        # Return the message after protocol
        return msg

    @staticmethod
    def video_call_info(chat_id, ips, usernames):
        """

        :param chat_id:
        :param ips:
        :param usernames:
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['video_call_info']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}{Protocol.FIELD_SEPARATOR}"
        # Add the first ip
        msg += ips[0]
        # Add the ips to the message
        for ip in ips[1:]:
            msg += Protocol.LIST_SEPARATOR + ip
        # Separate the fields
        msg += Protocol.FIELD_SEPARATOR
        # Add the first username
        msg += usernames[0]
        # Add the usernames to the message
        for username in usernames[1:]:
            msg += Protocol.LIST_SEPARATOR + username
        # Return the message after protocol
        return msg

    @staticmethod
    def voice_user_joined(chat_id, user_ip, username):
        """

        :param chat_id:
        :param user_ip:
        :param username:
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['voice_user_joined']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}" \
              f"{Protocol.FIELD_SEPARATOR}{user_ip}{Protocol.FIELD_SEPARATOR}{username}"
        # Return the message after protocol
        return msg

    @staticmethod
    def video_user_joined(chat_id, user_ip, username):
        """

        :param chat_id:
        :param user_ip:
        :param username:
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['video_user_joined']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}" \
              f"{Protocol.FIELD_SEPARATOR}{user_ip}{Protocol.FIELD_SEPARATOR}{username}"
        # Return the message after protocol
        return msg

    @staticmethod
    def chats_list(chats):
        pass

    @staticmethod
    def group_names(chat_id, usernames):
        """

        :param chat_id:
        :param usernames:
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['group_members']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}{Protocol.FIELD_SEPARATOR}"
        # Add the first username
        msg += usernames[0]
        # Add the usernames list
        for username in usernames[1:]:
            msg += Protocol.LIST_SEPARATOR + username
        # Return the message after protocol
        return msg

    @staticmethod
    def user_status(username, status):
        """

        :param username:
        :param status:
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['user_status']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{username}{Protocol.FIELD_SEPARATOR}{status}"
        # Return the message after protocol
        return msg

    @staticmethod
    def friend_added(friend_username):
        """

        :param friend_username:
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['friend_added']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{friend_username}"
        # Return the message after protocol
        return msg

    @staticmethod
    def send_file(chat_id, file_name, file):
        """

        :param chat_id:
        :param file_name:
        :param file:
        :return: the constructed message
        """
        # Get the opcode of register
        kind = Protocol.files_opcodes['send_file']
        # Construct the message
        msg = f"{kind}{Protocol.FIELD_SEPARATOR}{len(file)}{Protocol.FIELD_SEPARATOR}{chat_id}" \
              f"{Protocol.FIELD_SEPARATOR}{file_name}{Protocol.FIELD_SEPARATOR}{file}"
        # Return the message after protocol
        return msg

    @staticmethod
    def profile_picture(profile_username):
        """

        :param profile_username:
        :param image:
        :return: the constructed message
        """
        # Get the opcode of register
        kind = Protocol.files_opcodes['user_profile_picture']
        # Construct the message
        msg = f"{kind}{Protocol.FIELD_SEPARATOR}{profile_username}"
        # Return the message after protocol
        return msg

    @staticmethod
    def unprotocol_msg(type: str, raw_message: str):
        """
        Deconstructs a message received from the client with the client-server's protocol
        :param type: The type of the message (general / chats / files)
        :param raw_message: The raw message string that was sent
        :return: a dict of the parameters' names as the keys and their values as the values
        """
        chat_id = None
        opcode_name = ''

        # Split the message into it's fields with the field separator
        values = raw_message.split(Protocol.FIELD_SEPARATOR)
        # Get the opcode of the message
        opcode = int(values[0])
        values = values[1:]

        # The returned dict
        ret = {}

        # If the message was received in the general messages channel
        if type == 'general':
            if opcode in Protocol.c_general_opcodes.keys():
                # The first value in the dict is the opcode's name (opname)
                opcode_name = Protocol.c_general_opcodes[opcode]
                ret['opname'] = opcode_name
                ret['opcode'] = opcode

        # If the message was received in the chat messages channel
        elif type == 'chats':
            if opcode in Protocol.c_chat_opcodes.keys():
                # The first value in the dict is the opcode's name (opname)
                opcode_name = Protocol.c_chat_opcodes[opcode]
                ret['opname'] = opcode_name
                ret['opcode'] = opcode
                ret['chat_id'] = chat_id

        # If the message was received in the files messages channel
        elif type == 'files':
            if opcode in Protocol.c_files_opcodes.keys():
                # The first value in the dict is the opcode's name (opname)
                opcode_name = Protocol.c_files_opcodes[opcode]
                ret['opname'] = opcode_name
                ret['opcode'] = opcode

        # Get the parameters names of the message
        params_names = Protocol.c_opcodes_params[opcode_name]

        # Assign a value for each parameter in a dict
        for i in range(len(values)):
            value = values[i]
            param_name = params_names[i]

            # If the value is a list
            if len(value.split(Protocol.LIST_SEPARATOR)) > 1:
                # Check if the list is of integers
                if value.split(Protocol.LIST_SEPARATOR)[0].isnumeric():
                    ret[param_name] = [int(v) for v in value.split(Protocol.LIST_SEPARATOR)]
                else:
                    ret[param_name] = value.split(Protocol.LIST_SEPARATOR)

            # If the value isn't a list
            else:
                # Check if the value is an integer
                if value.isnumeric():
                    ret[param_name] = int(value)
                else:
                    ret[param_name] = value
        return ret


if __name__ == '__main__':
    data = "01@doron@12323k"
    ret = Protocol.unprotocol_msg("general", data)
    print(ret)



