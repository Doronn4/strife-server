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
        'approve_reject': 1,
        'friend_request': 2,
        'added_to_group': 3,
        'voice_call_started': 4,
        'video_call_started': 5,
        'voice_call_info': 6,
        'video_call_info': 7,
        'voice_user_joined': 8,
        'video_user_joined': 9,
        'chats_list': 10,
        'group_members': 11,
        'user_status': 12,
        'friend_added': 13
    }
    chat_opcodes = {
        'text_message': 1,
        'file_description': 2,
        'chat_history': 3
    }
    files_opcodes = {
        'file_in_chat': 1,
        'user_profile_picture': 2
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
        19: 'request_chats',
        20: 'accept_friend'
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
        'add_group_member': ('chat_id', 'new_member_username', 'group_key',),
        'request_group_members': ('chat_id',),
        'request_user_picture': ('pfp_username',),
        'request_user_status': ('username',),
        'request_chats': (),
        'text_message': ('chat_id', 'sender_username', 'message'),
        'accept_friend': ('friend_username', 'is_accepted',),
        'profile_pic_change': ('picture',),
        'file_in_chat': ('chat_id', 'file_name', 'file'),
        'file_description': ('chat_id', 'sender', 'file_name', 'file_size', 'file_hash',)
    }

    @staticmethod
    def approve(target_opcode):
        """
        Constructs an approval msg with the protocol
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
    def friend_request_notify(sender_username, silent=False):
        """
        Constructs a message to indicate that the user has received a friend request
        :param sender_username: The username of the requester
        :param silent: whether the client should be notified for the request
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['friend_request']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}" \
              f"{sender_username}{Protocol.FIELD_SEPARATOR}{int(silent)}"
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
        This method constructs a message with opcode 'voice_call_started'
        and chat_id parameter.

        :param chat_id: ID of the chat
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
        This method constructs a message with opcode 'video_call_started'
        and chat_id parameter.

        :param chat_id: ID of the chat
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
        This method constructs a message with opcode 'voice_call_info'
        and chat_id, ips, usernames parameters.

        :param chat_id: ID of the chat
        :param ips: IP addresses of the users
        :param usernames: usernames of the users
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
        Constructs a message containing video call information.

        :param chat_id: (int) The ID of the chat where the video call is taking place.
        :param ips: (list of str) The IP addresses of the users participating in the video call.
        :param usernames: (list of str) The usernames of the users participating in the video call.
        :return: (str) The constructed message.
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
        Constructs a message indicating that a user joined a voice chat.

        :param chat_id: (int) The ID of the chat where the user joined.
        :param user_ip: (str) The IP address of the user who joined.
        :param username: (str) The username of the user who joined.
        :return: (str) The constructed message.
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
        Constructs a message indicating that a user joined a video chat.

        :param chat_id: (int) The ID of the chat where the user joined.
        :param user_ip: (str) The IP address of the user who joined.
        :param username: (str) The username of the user who joined.
        :return: (str) The constructed message.
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
        """
        Construct a message for sending the list of chats to the server.

        :param chats: a list of chats, where each chat is a tuple of (chat_id, chat_name).
        :type chats: list
        :return: the constructed message
        :rtype: str
        """
        opcode = Protocol.general_opcodes['chats_list']
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}"

        # Add the first chat name
        msg += chats[0][1]
        if len(chats) > 1:
            # Add all the chats names
            for chat in chats[1:]:
                chat_name = chat[1]
                msg += Protocol.LIST_SEPARATOR + chat_name

        msg += Protocol.FIELD_SEPARATOR
        # Add the first chat id
        msg += str(chats[0][0])
        if len(chats) > 1:
            # Add all the chats ids
            for chat in chats[1:]:
                chat_id = str(chat[0])
                msg += Protocol.LIST_SEPARATOR + chat_id

        return msg

    @staticmethod
    def group_names(chat_id, usernames):
        """
        Construct a message for sending the list of group members to the server.

        :param chat_id: the id of the group chat
        :param usernames: a list of usernames, where each username is a string.
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
        Construct a message for updating the status of a user.

        :param username: the username of the user
        :param status: the new status of the user
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['user_status']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{username}{Protocol.FIELD_SEPARATOR}{status}"
        # Return the message after protocol
        return msg

    @staticmethod
    def friend_added(friend_username, friends_key, chat_id):
        """
        Construct a message for notifying the server about adding a friend.

        :param chat_id:
        :type chat_id:
        :param friends_key:
        :type friends_key:
        :param friend_username: the username of the new friend
        :return: the constructed message
        """
        # Get the opcode of register
        opcode = Protocol.general_opcodes['friend_added']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{friend_username}" \
              f"{Protocol.FIELD_SEPARATOR}{friends_key}{Protocol.FIELD_SEPARATOR}{chat_id} "
        # Return the message after protocol
        return msg

    @staticmethod
    def send_file(chat_id, file_name, file):
        """
        Construct a message with a file to be sent.

        :param chat_id: (str) the id of the chat the file will be sent to
        :param file_name: (str) the name of the file to be sent
        :param file: (bytes) the contents of the file to be sent
        :return: (str) the constructed message
        """
        # Get the opcode of the send_file
        kind = Protocol.files_opcodes['file_in_chat']
        # Construct the message with opcode, length of file and other information
        msg = f"{kind}{Protocol.FIELD_SEPARATOR}{chat_id}" \
              f"{Protocol.FIELD_SEPARATOR}{file_name}{Protocol.FIELD_SEPARATOR}{file}"
        # Return the constructed message
        return msg

    @staticmethod
    def profile_picture(profile_username, picture_contents):
        """
        Construct a message to request the profile picture of a user.

        :param picture_contents: The picture's contents as a base64 encoded string
        :type picture_contents: str
        :param profile_username: (str) the username of the user to request the profile picture for
        :return: (str) the constructed message
        """
        # Get the opcode of the user_profile_picture
        kind = Protocol.files_opcodes['user_profile_picture']
        # Construct the message with opcode and username
        msg = f"{kind}{Protocol.FIELD_SEPARATOR}{profile_username}{Protocol.FIELD_SEPARATOR}{picture_contents}"
        # Return the constructed message
        return msg

    @staticmethod
    def chat_history(messages):
        """
        Construct a message with a list of chat history messages.

        :param messages: (list) a list of messages representing the chat history
        :return: (str) the constructed message
        """
        # Get the opcode of the chat_history
        kind = Protocol.chat_opcodes['chat_history']
        # Construct the message with opcode and the first message from the list
        msg = f"{kind}{Protocol.FIELD_SEPARATOR}"
        msg += messages[0]

        # Add the rest of the messages to the message
        if len(messages) > 1:
            for message in messages[1:]:
                msg += Protocol.LIST_SEPARATOR + message

        # Return the constructed message
        return msg

    @staticmethod
    def unprotocol_msg(msg_type: str, raw_message: str):
        """
        Deconstructs a message received from the client with the client-server's protocol
        :param msg_type: The type of the message (general / chats / files)
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
        if msg_type == 'general':
            if opcode in Protocol.c_general_opcodes.keys():
                # The first value in the dict is the opcode's name (opname)
                opcode_name = Protocol.c_general_opcodes[opcode]
                ret['opname'] = opcode_name
                ret['opcode'] = opcode

        # If the message was received in the chat messages channel
        elif msg_type == 'chats':
            if opcode in Protocol.c_chat_opcodes.keys():
                # The first value in the dict is the opcode's name (opname)
                opcode_name = Protocol.c_chat_opcodes[opcode]
                ret['opname'] = opcode_name
                ret['opcode'] = opcode
                ret['chat_id'] = chat_id

        # If the message was received in the files messages channel
        elif msg_type == 'files':
            if opcode in Protocol.c_files_opcodes.keys():
                # The first value in the dict is the opcode's name (opname)
                opcode_name = Protocol.c_files_opcodes[opcode]
                ret['opname'] = opcode_name
                ret['opcode'] = opcode

        # Get the parameters names of the message
        params_names = Protocol.c_opcodes_params[opcode_name]

        # Assign a value for each parameter in a dict
        for i in range(len(params_names)):
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
