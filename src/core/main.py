import hashlib
import os
import queue
import threading
from pathlib import Path
import base64
import sys

# Add the project folder to PYTHONPATH
project_dir = str(Path(os.path.abspath(__file__)).parent.parent.parent)
sys.path.insert(0, project_dir)

from src.core.server_com import ServerCom
from src.core.server_protocol import Protocol
from src.handlers.db import DBHandler
from src.core.cryptions import AESCipher
from src.handlers.file_handler import FileHandler


def check_password(password):
    """
    Function to check if a password is valid

    :param password: The password to check
    :type password: str
    :return: True if the password is valid, False otherwise
    :rtype: bool
    """
    is_valid = True

    # Check if password is valid
    if not password:
        is_valid = False
    elif len(password) > 20:
        is_valid = False
    elif not password.isalnum():
        is_valid = False
    elif len(password) < 3:
        is_valid = False

    return True


def check_username(username):
    """
    Function to check if a username is valid

    :param username: The username to check
    :type username: str
    :return: True if the username is valid, False otherwise
    :rtype: bool
    """
    is_valid = True

    # Check if username is valid
    if not username:
        is_valid = False
    elif len(username) > 20:
        is_valid = False
    elif not username.isalnum():
        is_valid = False
    elif len(username) < 3:
        is_valid = False

    return True


def handle_register(com, chat_com, files_com, ip, params):
    """
    Function to handle registering to the server

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the user is already logged in
    if ip in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)

    else:
        db_handle = DBHandler('strife_db')
        username = str(params['username'])
        password = str(params['password'])

        is_valid = check_username(username) and check_password(password)

        if not is_valid:
            reject_msg = Protocol.reject(params['opcode'])
            com.send_data(reject_msg, ip)
            print(f'INFO: Register failed for {ip}')

        else:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            flag = db_handle.add_user(username, hashed_password)
            if flag:
                approve_msg = Protocol.approve(params['opcode'])
                com.send_data(approve_msg, ip)
                print(f'INFO: New user registered - "{username}", {ip}')
            else:
                reject_msg = Protocol.reject(params['opcode'])
                com.send_data(reject_msg, ip)
                print(f'INFO: Register failed for {ip}')


def handle_login(com, chat_com, files_com, ip, params):
    """
    Function to handle logging in to the server

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the user is already logged in
    if ip in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)

    else:
        db_handle = DBHandler('strife_db')
        username = str(params['username'])
        password = str(params['password'])
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if username in logged_in_users.values():
            flag = False
        else:
            flag = db_handle.check_credentials(username, hashed_password)
        if flag:
            approve_msg = Protocol.approve(params['opcode'])
            com.send_data(approve_msg, ip)
            # Add the user to the dict of logged-in users with his ip as the key and username as value
            logged_in_users[ip] = username
            logged_in_passwords[ip] = password

            # Start a thread to send the pending friend requests and messages after waiting for 2 seconds
            send_pending_friend_requests(username, com)
            send_pending_messages(username, com)
            save_pending_keys(username, password)

            # Send the user his status
            status = db_handle.get_user_status(username)
            status_msg = Protocol.user_status(username, status)
            com.send_data(status_msg, ip)

            print(f'INFO: User logged in - "{username}", {ip}')
        else:
            reject_msg = Protocol.reject(params['opcode'])
            com.send_data(reject_msg, ip)
            print(f'INFO: Login failed for {ip}')


def handle_friend_add(com, chat_com, files_com, ip, params):
    """
    Function to handle a friend request

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the user is logged in
    if ip in logged_in_users.keys():
        db_handle = DBHandler('strife_db')
        friend_username = str(params['friend_username'])
        adder_username = logged_in_users[ip]

        # Check if the user is trying to add himself
        if adder_username == friend_username:
            com.send_data(Protocol.reject(params['opcode']), ip)
            return

        # Check if the friend request is already pending
        is_already_pending = (
                                     adder_username in pending_friend_requests.keys() and
                                     pending_friend_requests[adder_username] == friend_username
                             ) or (
                                     friend_username in pending_friend_requests.keys() and
                                     pending_friend_requests[friend_username] == adder_username
                             )

        # Check if the friend request is valid
        if db_handle.can_add_friend(adder_username, friend_username) and not is_already_pending:
            friend_ip = get_ip_by_username(friend_username)
            # Send the friend request to the friend
            if friend_ip:
                msg = Protocol.friend_request_notify(adder_username, silent=False)
                com.send_data(msg, friend_ip)

            # Add the friend request to the pending requests
            pending_friend_requests[adder_username] = friend_username

        else:
            com.send_data(Protocol.reject(params['opcode']), ip)

    else:
        com.send_data(Protocol.reject(params['opcode']), ip)


def handle_friend_accept(com, chat_com, files_com, ip, params):
    """
    Function to handle a friend request accept

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    if ip in logged_in_users.keys():
        # Get the username of the sender
        username = logged_in_users[ip]
        # Get the username of the friend
        friend_username = str(params['friend_username'])

        # Check if the friend request is accepted
        if bool(params['is_accepted']):
            # Check if the friend request is pending
            if friend_username in pending_friend_requests.keys() \
                    and pending_friend_requests[friend_username] == username:
                db_handle = DBHandler('strife_db')
                # Add the friend to the database and create a chat for them
                chat_id = db_handle.add_friend(username, friend_username)
                # Create a chat folder for the chat
                FileHandler.create_chat(chat_id)
                # Generate a key for the chat
                friends_key = AESCipher.generate_key()

                # Send the friend added message to the friend
                msg = Protocol.friend_added(friend_username, friends_key, chat_id)
                com.send_data(msg, ip)

                # Add the key to the database
                db_handle.add_key(username, chat_id, friends_key, logged_in_passwords[ip])

                # Send the friend added message to the user
                msg = Protocol.friend_added(username, friends_key, chat_id)
                friend_ip = get_ip_by_username(friend_username)
                if friend_ip:
                    com.send_data(msg, get_ip_by_username(friend_username))
                    db_handle.add_key(friend_username, chat_id, friends_key, logged_in_passwords[friend_ip])

                else:
                    # If the friend is not online, add the message to his pending messages
                    add_pending_message(msg, friend_username)
                    add_pending_key(friends_key, chat_id, friend_username)

                del pending_friend_requests[friend_username]
            else:
                com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        com.send_data(Protocol.reject(params['opcode']), ip)


def handle_friend_remove(com, chat_com, files_com, ip, params):
    """
    Function to handle removing a friend

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the user is logged in
    if ip in logged_in_users.keys():
        db_handle = DBHandler('strife_db')
        friend_username = str(params['friend_username'])
        remover_username = logged_in_users[ip]

        db_handle.remove_friend(remover_username, friend_username)
    else:
        com.send_data(Protocol.reject(params['opcode']), ip)


def handle_group_creation(com, chat_com, files_com, ip, params):
    """
    Function to handle a group creation

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the user is logged in
    if ip in logged_in_users.keys():
        db_handle = DBHandler('strife_db')

        group_name = str(params['group_name'])
        group_key = AESCipher.generate_key()

        creator_username = logged_in_users[ip]
        # Create the group and save its id
        group_id = db_handle.create_group(group_name, creator_username)
        if group_id == -1:
            com.send_data(Protocol.reject(params['opcode']), ip)
        else:
            # Create a folder for the chat
            FileHandler.create_chat(group_id)
            # Create a message that indicates that the creator of the group was added to the group
            msg = Protocol.added_to_group(group_name, group_id, group_key)
            # Add the key to the database
            db_handle.add_key(creator_username, group_id, group_key, logged_in_passwords[ip])
            # Send the message to the client (creator)
            com.send_data(msg, ip)
    else:
        com.send_data(Protocol.reject(params['opcode']), ip)


def handle_add_group_member(com, chat_com, files_com, ip, params):
    """
    Function to handle adding a member to a group

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the user is logged in
    if ip in logged_in_users.keys():
        db_handle = DBHandler('strife_db')

        chat_id = params['chat_id']
        username = str(params['new_member_username'])
        group_key = str(params['group_key'])
        adder = logged_in_users[ip]

        # Add the user to the group in the database and check if the operation was successful
        flag = db_handle.add_to_group(chat_id, adder, username)

        # If the operation was successful, send the user a message that he was added to the group
        if flag:
            added_msg = Protocol.added_to_group(db_handle.get_group_name(chat_id), chat_id, group_key)
            # Add the key to the database
            db_handle.add_key(adder, chat_id, group_key, logged_in_passwords[ip])

            user_ip = get_ip_by_username(username)
            if user_ip:
                # Send the message to the user
                com.send_data(added_msg, get_ip_by_username(username))
                db_handle.add_key(username, chat_id, group_key, logged_in_passwords[user_ip])
            else:
                # If the user is not online, add the message to his pending messages
                add_pending_message(added_msg, username)
                add_pending_key(group_key, chat_id, username)

            # Send the group members to the user
            send_group_members(com, chat_id)

        # Send a message to the user that sent the request
        msg = Protocol.approve(params['opcode']) if flag else Protocol.reject(params['opcode'])
        com.send_data(msg, ip)
    else:
        com.send_data(Protocol.reject(params['opcode']), ip)


def handle_request_chats(com, chat_com, files_com, ip, params):
    """
    Function to handle a request of the user's chats list

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the user is logged in
    if ip in logged_in_users.keys():
        db_handle = DBHandler('strife_db')

        username = logged_in_users[ip]
        # Get the user's chats
        chats = db_handle.get_chats_of(username)
        # Check if the user has any chats
        if len(chats) > 0:
            # Send the chats list to the user
            msg = Protocol.chats_list(chats)
            com.send_data(msg, ip)
    else:
        com.send_data(Protocol.reject(params['opcode']), ip)


def handle_username_change(com, chat_com, files_com, ip, params):
    """
    Function to handle a username change

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    if ip not in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        new_username = str(params['new_username'])
        old_username = logged_in_users[ip]

        # Check if the new username is valid
        if not check_username(new_username):
            com.send_data(Protocol.reject(params['opcode']), ip)
        else:
            # Check if the new username is already taken
            if db_handle.change_username(old_username, new_username):
                logged_in_users[ip] = new_username
                com.send_data(Protocol.approve(params['opcode']), ip)
            else:
                com.send_data(Protocol.reject(params['opcode']), ip)


def handle_status_change(com, chat_com, files_com, ip, params):
    """
    Function to handle a status change

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    if ip in logged_in_users.keys():
        db_handle = DBHandler('strife_db')
        new_status = str(params['new_status'])

        # Check new status
        if 0 < len(new_status) < 20:
            db_handle.update_user_status(logged_in_users[ip], new_status)
            msg = Protocol.user_status(logged_in_users[ip], new_status)
            com.send_data(msg, ip)
        else:
            com.send_data(Protocol.reject(params['opcode']), ip)

    else:
        com.send_data(Protocol.reject(params['opcode']), ip)


def handle_password_change(com, chat_com, files_com, ip, params):
    """
    Function to handle a password change

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    if ip not in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        new_password = params['new_password']
        old_password = params['old_password']
        hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()

        # Check if the old password is correct
        if not db_handle.check_credentials(logged_in_users[ip], hashed_old_password):
            com.send_data(Protocol.reject(params['opcode']), ip)
            return

        # Check if the new password is valid
        is_valid = check_password(new_password)
        if not is_valid:
            com.send_data(Protocol.reject(params['opcode']), ip)
        else:
            # Hash the new password
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

            # Change the password in the database and send the response
            if db_handle.change_password(logged_in_users[ip], hashed_password):
                logged_in_passwords[ip] = new_password
                com.send_data(Protocol.approve(params['opcode']), ip)
            else:
                com.send_data(Protocol.reject(params['opcode']), ip)


def handle_text_message(com, ip, params, raw):
    """
    Handles a text message sent from a client in some chat
    :param com: The general communication object of the server
    :type com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :param raw: The raw message
    :type raw: str
    :return: None
    """
    # Check if the user is logged in
    if ip not in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)

    else:
        db_handle = DBHandler('strife_db')
        chat_id = params['chat_id']
        sender = params['sender_username']

        # Encode the message to base64
        b64_raw = base64.b64encode(raw.encode()).decode()
        # Add the encoded message to the database
        db_handle.add_message(chat_id, sender, b64_raw)
        # Get the names of the members of the chat
        group_members_names = db_handle.get_group_members(chat_id)
        # Get the IPs of the members of the chat
        connected_members_ips = [get_ip_by_username(member_name)
                                 for member_name in group_members_names
                                 if member_name in logged_in_users.values()]

        # Send the message to all the members of the chat
        com.send_data(raw, connected_members_ips)


def handle_file_description(com, ip, params, raw):
    """
    Handles a file description sent from a client in some chat
    :param com: The general communication object of the server
    :type com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :param raw: The raw message
    :type raw: str
    :return: None
    """
    # Check if the user is logged in
    if ip not in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)

    else:
        db_handle = DBHandler('strife_db')
        chat_id = params['chat_id']
        sender = params['sender']

        # Encode the message to base64
        b64_raw = base64.b64encode(raw.encode()).decode()
        # Add the encoded message to the database
        db_handle.add_message(chat_id, sender, b64_raw)
        # Get the names of the members of the chat
        group_members_names = db_handle.get_group_members(chat_id)
        # Get the IPs of the members of the chat
        connected_members_ips = [get_ip_by_username(member_name)
                                 for member_name in group_members_names
                                 if member_name in logged_in_users.values()]
        # Send the message to all the members of the chat
        com.send_data(raw, connected_members_ips)


def handle_request_picture(com, chat_com, files_com, ip, params):
    """
    Function to handle a profile picture request

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    if ip not in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        username = str(params['pfp_username'])
        # Get the path of the profile picture
        pic_path = db_handle.get_user_picture_path(username)
        # If the user has a profile picture, send it to the client
        if pic_path:
            # Load the picture and encode it to base64
            pic_contents = FileHandler.load_pfp(path=pic_path)
            str_contents = base64.b64encode(pic_contents).decode()
            # Send the profile picture to the client
            print(f'LOG: Sending profile picture of {username} to {ip}')
            msg = Protocol.profile_picture(username, str_contents)
            files_com.send_file(msg, ip)


def handle_update_pfp(com, ip, params):
    """
    Function to handle a profile picture update
    :param com: The general communication object of the server
    :type com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    if ip not in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        b64_picture = params['picture']
        # Decode the base64 picture
        pic_contents = base64.b64decode(b64_picture)
        # Save the picture and get the path
        path = FileHandler.save_pfp(pic_contents, logged_in_users[ip])
        # If the path is empty, the picture was not saved
        if not path:
            com.send_data(Protocol.reject(params['opcode']), ip)
        else:
            # Update the user's profile picture in the database
            db_handle.update_user_picture(logged_in_users[ip], path)
            # Send the profile picture to the client
            msg = Protocol.profile_picture(logged_in_users[ip], b64_picture)
            com.send_file(msg, ip)


def handle_chat_history_request(com, chat_com, files_com, ip, params):
    """
    Function to handle a request for a chat's message history

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    if ip not in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        chat_id = params['chat_id']
        # Get the chat's message history
        history = db_handle.get_chat_history(chat_id)
        # If the chat has a history, send it to the client
        if history:
            print(f'LOG: Sending chat history of chat {chat_id} to {ip}')
            msg = Protocol.chat_history(history, chat_id)
            print(f'LOG: History msg: {msg}')
            chat_com.send_data(msg, ip)


def handle_request_group_members(com, chat_com, files_com, ip, params):
    """
    Function to handle a request for the list of members in a group

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    if ip not in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        chat_id = params['chat_id']
        members = db_handle.get_group_members(chat_id)
        msg = Protocol.group_names(chat_id, members)
        com.send_data(msg, ip)


def handle_file_in_chat(com, ip, params):
    """
    Function to handle a file in a chat
    :param com: The general communication object of the server
    :type com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    if ip not in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        chat_id = params['chat_id']
        filename = params['file_name']
        file_contents = params['file']
        # Get the hash of the file
        file_hash = hashlib.sha256(file_contents.encode()).hexdigest()
        # Save the file
        try:
            FileHandler.save_file(file_contents.encode(), chat_id, filename)
        except Exception:
            com.send_data(Protocol.reject(params['opcode']), ip)
        else:
            # Add the file to the database
            db_handle.add_file(chat_id, filename, file_hash)


def handle_request_file(com, chat_com, files_com, ip, params):
    """
    Function to handle a file request from a client

    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """

    # Check if the IP address is in the logged_in_users dictionary
    if ip not in logged_in_users.keys():
        # If the IP address is not logged in, send a rejection message to the client through the com object
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        # If the IP address is logged in, create a new DBHandler object with the 'strife_db' database
        db_handle = DBHandler('strife_db')
        # Get the file hash from the parameters dictionary
        file_hash = params['file_hash']
        # Use the DBHandler object to get the file name and chat ID associated with the file hash
        ret = db_handle.get_file(file_hash)
        if ret:
            file_name, chat_id = ret
            # Check if the client is a member of the group associated with the chat ID
            if db_handle.is_in_group(chat_id, username=logged_in_users[ip]):
                # If the client is a member of the group, load the file contents and encode them in base64 format
                file_contents = FileHandler.load_file(chat_id, file_name)
                if not file_contents:
                    com.send_data(Protocol.reject(params['opcode']), ip)
                    db_handle.remove_file(file_hash)
                else:
                    # Create a message using the Protocol module's send_file() method
                    msg = Protocol.send_file(chat_id, file_name, file_contents.decode())
                    # Send the message to the files_com object to be forwarded to the file server
                    files_com.send_file(msg, ip)


def handle_request_status(com, chat_com, files_com, ip, params):
    """
    Function to handle a request for the status of a user
    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the IP address is in the logged_in_users dictionary
    if ip not in logged_in_users.keys():
        # If the IP address is not logged in, send a rejection message to the client through the com object
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        username = params['username']
        # Get the status of the user from the database
        try:
            status = db_handle.get_user_status(username)
        except Exception:
            com.send_data(Protocol.reject(params['opcode']), ip)
        else:
            print(f"LOG: Sending status of {username} to {logged_in_users[ip]}")
            com.send_data(Protocol.user_status(username, status), ip)


def handle_voice_started(com, chat_com, files_com, ip, params):
    """
    Function to handle a voice started message from a client
    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the IP address is in the logged_in_users dictionary
    if ip not in logged_in_users.keys():
        # If the IP address is not logged in, send a rejection message to the client through the com object
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        chat_id = params['chat_id']
        msg = Protocol.voice_started(chat_id)
        members = db_handle.get_group_members(chat_id)
        print(f"LOG: Sending voice started message to {members} from {logged_in_users[ip]}")
        for member in members:
            member_ip = get_ip_by_username(member)
            if member_ip and member_ip != ip:
                com.send_data(msg, member_ip)


def handle_video_started(com, chat_com, files_com, ip, params):
    """
    Function to handle a video started message from a client
    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the IP address is in the logged_in_users dictionary
    if ip not in logged_in_users.keys():
        # If the IP address is not logged in, send a rejection message to the client through the com object
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        chat_id = params['chat_id']
        msg = Protocol.video_started(chat_id)
        # Get the members of the group associated with the chat ID
        members = db_handle.get_group_members(chat_id)
        # Send the message to all members of the group except the client that sent the message
        print(f"LOG: Sending video started message to {members} from {logged_in_users[ip]}")
        for member in members:
            member_ip = get_ip_by_username(member)
            if member_ip and member_ip != ip:
                com.send_data(msg, member_ip)


def handle_voice_join(com, chat_com, files_com, ip, params):
    """
    Function to handle a voice join message from a client
    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the IP address is in the logged_in_users dictionary
    if ip not in logged_in_users.keys():
        # If the IP address is not logged in, send a rejection message to the client through the com object
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        chat_id = params['chat_id']
        online_members_ips = []
        online_members_names = []

        # TODO: is it really necessary to send the voice user joined message
        #  to the client that sent the voice join message?
        print(f"LOG: User {logged_in_users[ip]} joined voice call in chat {chat_id}")
        msg = Protocol.voice_user_joined(chat_id, ip, logged_in_users[ip])
        # Get the members of the group associated with the chat ID
        members = db_handle.get_group_members(chat_id)
        # Send the message to all members of the group except the client that sent the message
        for member in members:
            member_ip = get_ip_by_username(member)
            if member_ip and member_ip != ip:
                com.send_data(msg, member_ip)
                online_members_ips.append(member_ip)
                online_members_names.append(member)

        if len(online_members_ips) > 0:
            # Send the voice call info message to the client that sent the voice join message
            msg = Protocol.voice_call_info(chat_id, online_members_ips, online_members_names)
            com.send_data(msg, ip)


def handle_video_join(com, chat_com, files_com, ip, params):
    """
    Function to handle a video join message from a client
    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the IP address is in the logged_in_users dictionary
    if ip not in logged_in_users.keys():
        # If the IP address is not logged in, send a rejection message to the client through the com object
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        chat_id = params['chat_id']
        online_members_ips = []
        online_members_names = []

        print(f"LOG: User {logged_in_users[ip]} joined video call in chat {chat_id}")
        msg = Protocol.video_user_joined(chat_id, ip, logged_in_users[ip])
        # Get the members of the group associated with the chat ID
        members = db_handle.get_group_members(chat_id)
        # Send the message to all members of the group except the client that sent the message
        for member in members:
            member_ip = get_ip_by_username(member)
            if member_ip and member_ip != ip:
                com.send_data(msg, member_ip)
                online_members_ips.append(member_ip)
                online_members_names.append(member)

        if len(online_members_ips) > 0:
            msg = Protocol.video_call_info(chat_id, online_members_ips, online_members_names)
            # Send the video call info message to the client that sent the video join message
            com.send_data(msg, ip)


def handle_request_friend_list(com, chat_com, files_com, ip, params):
    """
    Function to handle a request friend list message from a client
    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the IP address is in the logged_in_users dictionary
    if ip not in logged_in_users.keys():
        # If the IP address is not logged in, send a rejection message to the client through the com object
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        username = logged_in_users[ip]
        friend_list = db_handle.get_friends_of(username)
        # Check if the friend list is not empty
        if True:
            msg = Protocol.friend_list(friend_list)
            com.send_data(msg, ip)


def handle_logout(com, chat_com, files_com, ip, params):
    """
    Function to handle a logout message from a client
    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the IP address is in the logged_in_users dictionary
    if ip not in logged_in_users.keys():
        # If the IP address is not logged in, send a rejection message to the client through the com object
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        print(f'INFO: User logged out - "{logged_in_users[ip]}", {ip}')
        # Remove the IP address from the logged_in_users dictionary
        del logged_in_users[ip]
        del logged_in_passwords[ip]


def handle_request_keys(com, chat_com, files_com, ip, params):
    """
    Function to handle a request keys message from a client
    :param com: The general communication object of the server
    :type com: ServerCom
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param files_com: The files communication object of the server
    :type files_com: ServerCom
    :param ip: IP address of the client
    :type ip: str
    :param params: Dictionary of parameters of the message
    :type params: dict
    :return: None
    """
    # Check if the IP address is in the logged_in_users dictionary
    if ip not in logged_in_users.keys():
        # If the IP address is not logged in, send a rejection message to the client through the com object
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        # Get the keys of the user
        username = logged_in_users[ip]
        # Get the keys of the user and the chat IDs of the chats that the keys are associated with
        keys, chat_ids = db_handle.get_user_keys(username, logged_in_passwords[ip])
        print(f'LOG: User requested keys - "{username}", {ip}', keys, chat_ids)
        # Check if the keys list is not empty
        if len(keys) > 0:
            # Send the keys to the client
            msg = Protocol.keys(keys, chat_ids)
            com.send_data(msg, ip)


def handle_request_picture_check(com, chat_com, files_com, ip, params):
    if ip not in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)
    else:
        db_handle = DBHandler('strife_db')
        username = str(params['username'])
        user_current_hash = str(params['pfp_hash'])
        # Get the path of the profile picture
        pic_path = db_handle.get_user_picture_path(username)
        # If the user has a profile picture, send it to the client
        if pic_path:
            # Load the picture and encode it to base64
            pic_contents = FileHandler.load_pfp(path=pic_path)
            # Hash the picture contents
            pic_hash = hashlib.sha256(pic_contents).hexdigest()
            # Check if the picture hash is the same as the one sent by the client
            if pic_hash == user_current_hash:
                # If the hashes are the same, do not send the picture
                return
            str_contents = base64.b64encode(pic_contents).decode()
            # Send the profile picture to the client
            print(f'LOG: Sending profile picture of {username} to {ip}')
            msg = Protocol.profile_picture(username, str_contents)
            files_com.send_file(msg, ip)


def handle_general_messages(general_com, chat_com, files_com, q):
    """
    Handle the general messages
    :param chat_com: The chats communication object of the server
    :type chat_com: ServerCom
    :param general_com: The general communication object of the server
    :param files_com: The files communication object of the server
    :param q: The queue of messages
    :return: None
    """
    while True:
        data, ip = q.get()

        # If a user has disconnected
        if data == '':
            if ip in logged_in_users.keys():
                del logged_in_users[ip]
                del logged_in_passwords[ip]

        else:
            try:
                msg = Protocol.unprotocol_msg("general", data)
            except Exception:
                pass
            else:
                if msg['opname'] in general_dict.keys():
                    general_dict[msg['opname']](general_com, chat_com, files_com, ip, msg)


def handle_chats_messages(com, q):
    """
    Handle the chats messages
    :param com: The chats communication object of the server
    :param q: The queue of messages
    :return: None
    """
    while True:
        data, ip = q.get()
        try:
            msg = Protocol.unprotocol_msg("chats", data)
        except Exception as e:
            pass
        else:
            if msg['opname'] in messages_dict.keys():
                messages_dict[msg['opname']](com, ip, msg, data)


def handle_files_messages(com, q):
    """
    Handle the files messages
    :param com: The files communication object of the server
    :param q: The queue of messages
    :return: None
    """
    while True:
        data, ip = q.get()
        try:
            msg = Protocol.unprotocol_msg("files", data)
        except Exception:
            pass
        else:
            if msg['opname'] in files_dict.keys():
                threading.Thread(target=files_dict[msg['opname']], args=(com, ip, msg,)).start()


def send_pending_friend_requests(username, com):
    """
    Send pending friend requests to a user
    :param username: The username of the user
    :param com: The general communication object of the server
    :return: None
    """
    # Check if the user is logged in
    if username in logged_in_users.values():
        ip = get_ip_by_username(username)
        pending_requests = [req_sender for req_sender, receiver in pending_friend_requests.items() if
                            receiver == username]
        for request in pending_requests:
            msg = Protocol.friend_request_notify(request, silent=True)
            if ip:
                com.send_data(msg, ip)


def add_pending_message(message, username):
    """
    Add a pending message to the pending messages dictionary
    :param message: The message to add
    :param username: The username of the user to send the message to
    :return: None
    """
    # Check if the user has pending messages
    if username in pending_messages.keys():
        # Add the message to the pending messages list
        pending_messages[username].append(message)
    else:
        # Create a new list of pending messages for the user
        pending_messages[username] = [message]


def add_pending_key(key, chat_id, username):
    """
    Add a pending key to the pending keys dictionary
    :param key: The key to add
    :param chat_id: The chat id of the chat that the key is associated with
    :param username: The username of the user to send the key to
    :return: None
    """
    # Check if the user has pending keys
    if username in pending_keys.keys():
        # Check if the user has pending keys for the chat
        if chat_id in pending_keys[username].keys():
            # Add the key to the pending keys list
            pending_keys[username][chat_id].append(key)
        else:
            # Create a new list of pending keys for the chat
            pending_keys[username][chat_id] = [key]
    else:
        # Create a new dictionary of pending keys for the user
        pending_keys[username] = {chat_id: [key]}


def save_pending_keys(username, password):
    """
    Save the pending keys of a user
    :param username: The username of the user
    :param password: The password of the user
    :return: None
    """
    # Check if the user has pending keys
    if username in pending_keys.keys():
        db_handle = DBHandler('strife_db')
        # Get the pending keys of the user
        pending = pending_keys[username]
        # Add the pending keys to the keys list
        for chat_id in pending.keys():
            for key in pending[chat_id]:
                db_handle.add_key(username, chat_id, key, password)

        del pending_keys[username]


def send_pending_messages(username, com):
    """
    Send pending messages to a user
    :param username: The username of the user
    :param com: The general communication object of the server
    :return: None
    """
    if username in logged_in_users.values():
        ip = get_ip_by_username(username)
        # Check if the user has pending messages
        if username in pending_messages.keys():
            # Send the pending messages to the user
            messages = pending_messages[username]
            for message in messages:
                com.send_data(message, ip)


def send_group_members(com, chat_id):
    """
    Send the group members to all the group members
    :param com: The chats communication object of the server
    :param chat_id: The chat id of the group
    :return: None
    """
    db_handle = DBHandler('strife_db')
    # Get the group members
    members = db_handle.get_group_members(chat_id)
    msg = Protocol.group_names(chat_id, members)
    # Send the group members to all the online group members
    for member in members:
        member_ip = get_ip_by_username(member)
        if member_ip:
            com.send_data(msg, member_ip)


def get_ip_by_username(username):
    """
    Get the ip of a user by his username
    :param username: The username of the user
    :return: The ip of the user, or None if not found
    """
    return next((target_ip for target_ip, name in logged_in_users.items() if name == username), None)


# The dictionary of the general messages
general_dict = {
    'register': handle_register,
    'sign_in': handle_login,
    'add_friend': handle_friend_add,
    'create_group': handle_group_creation,
    'add_group_member': handle_add_group_member,
    'request_chats': handle_request_chats,
    'remove_friend': handle_friend_remove,
    'change_username': handle_username_change,
    'change_status': handle_status_change,
    'change_password': handle_password_change,
    'request_user_picture': handle_request_picture,
    'accept_friend': handle_friend_accept,
    'get_chat_history': handle_chat_history_request,
    'request_group_members': handle_request_group_members,
    'request_file': handle_request_file,
    'request_user_status': handle_request_status,
    'start_voice': handle_voice_started,
    'start_video': handle_video_started,
    'join_voice': handle_voice_join,
    'join_video': handle_video_join,
    'request_friend_list': handle_request_friend_list,
    'logout': handle_logout,
    'request_keys': handle_request_keys,
    'request_user_picture_check': handle_request_picture_check,

}

# The dictionary of the chats messages
messages_dict = {
    'text_message': handle_text_message,
    'file_description': handle_file_description
}

# The dictionary of the files messages
files_dict = {
    'profile_pic_change': handle_update_pfp,
    'file_in_chat': handle_file_in_chat
}

# The dictionary of the users with the key being the ip and the value being the username
logged_in_users = {}

# The dictionary of the users with the key being the username and the value being the password
logged_in_passwords = {}

# The dictionary of the pending friend requests with the key being the sender and the value being the receiver
pending_friend_requests = {}

# The dictionary of the pending messages with the key being the username and the value being the list of messages
pending_messages = {}

pending_keys = {}


def main():
    script_path = Path(os.path.abspath(__file__))
    wd = script_path.parent.parent.parent
    os.chdir(str(wd))
    FileHandler.initialize()

    # Create the general messages queue
    general_queue = queue.Queue()
    # Create the communication object for the general messages
    general_com = ServerCom(3108, general_queue, log=True)

    # Create the chat messages queue
    chats_queue = queue.Queue()
    # Create the communication object for the chat messages
    chats_com = ServerCom(2907, chats_queue, com_type='chats')

    # Create the files messages queue
    files_queue = queue.Queue()
    # Create the communication object for the files messages
    files_com = ServerCom(3103, files_queue, com_type='files')

    # Start a thread to handle the general messages being received
    threading.Thread(target=handle_general_messages, args=(general_com, chats_com, files_com, general_queue)).start()
    # Start a thread to handle the chat messages being received
    threading.Thread(target=handle_chats_messages, args=(chats_com, chats_queue)).start()
    # Start a thread to handle the files messages being received
    threading.Thread(target=handle_files_messages, args=(files_com, files_queue)).start()

    print('###### Strife server started running ######\n')


if __name__ == '__main__':
    main()
