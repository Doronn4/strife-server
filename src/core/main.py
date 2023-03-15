import queue
import threading
import subprocess
from src.core.server_com import ServerCom
from src.core.server_protocol import Protocol
from src.handlers.db import DBHandler
from src.core.cryptions import AESCipher


def handle_register(com, ip, params):
    # Check if the user is already logged in
    if ip in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)

    else:
        db_handle = DBHandler('strife_db')
        username = params['username']
        password = params['password']
        flag = db_handle.add_user(username, password)
        if flag:
            approve_msg = Protocol.approve(params['opcode'])
            com.send_data(approve_msg, ip)
            print(f'INFO: New user registered - "{username}", {ip}')
        else:
            reject_msg = Protocol.reject(params['opcode'])
            com.send_data(reject_msg, ip)
            print(f'INFO: Register failed for {ip}')


def handle_login(com, ip, params):
    # Check if the user is already logged in
    if ip in logged_in_users.keys():
        com.send_data(Protocol.reject(params['opcode']), ip)

    else:
        db_handle = DBHandler('strife_db')
        username = params['username']
        password = params['password']
        if username in logged_in_users.values():
            flag = False
        else:
            flag = db_handle.check_credentials(username, password)
        if flag:
            approve_msg = Protocol.approve(params['opcode'])
            com.send_data(approve_msg, ip)
            # Add the user to the dict of logged in users with his ip as the key and username as value
            logged_in_users[ip] = username
            print(f'INFO: User logged in - "{username}", {ip}')
        else:
            reject_msg = Protocol.reject(params['opcode'])
            com.send_data(reject_msg, ip)
            print(f'INFO: Login failed for {ip}')


def handle_friend_add(com, ip, params):
    # Check if the user is logged in
    if ip in logged_in_users.keys():
        db_handle = DBHandler('strife_db')
        friend_username = params['friend_username']
        adder_username = logged_in_users[ip]

        try:
            db_handle.add_friend(adder_username, friend_username)
        except Exception:
            com.send_data(Protocol.reject(params['opcode']), ip)

    else:
        com.send_data(Protocol.reject(params['opcode']), ip)


def handle_friend_remove(com, ip, params):
    # Check if the user is logged in
    if ip in logged_in_users.keys():
        db_handle = DBHandler('strife_db')
        friend_username = params['friend_username']
        remover_username = logged_in_users[ip]

        db_handle.remove_friend(remover_username, friend_username)
    else:
        com.send_data(Protocol.reject(params['opcode']), ip)


def handle_group_creation(com, ip, params):
    # Check if the user is logged in
    if ip in logged_in_users.keys():
        db_handle = DBHandler('strife_db')

        group_name = params['group_name']
        group_key = AESCipher.generate_key()

        creator_username = logged_in_users[ip]
        # Create the group and save it's id
        group_id = db_handle.create_group(group_name, creator_username)
        # Create a message that indicates that the creator of the group was added to the group
        msg = Protocol.added_to_group(group_name, group_id, group_key)
        # Send the message to the client (creator)
        com.send_data(msg, ip)
    else:
        com.send_data(Protocol.reject(params['opcode']), ip)


def handle_add_group_member(com, ip, params):
    # Check if the user is logged in
    if ip in logged_in_users.keys():
        db_handle = DBHandler('strife_db')

        chat_id = params['chat_id']
        username = params['new_member_username']
        group_key = params['group_key']
        adder = logged_in_users[ip]

        flag = db_handle.add_to_group(chat_id, adder, username)

        if flag:
            added_msg = Protocol.added_to_group(db_handle.get_group_name(chat_id), chat_id, group_key)
            com.send_data(added_msg, ip)

        msg = Protocol.approve(params['opcode']) if flag else Protocol.reject(params['opcode'])
        com.send_data(msg, ip)
    else:
        com.send_data(Protocol.reject(params['opcode']), ip)


def handle_request_chats(com, ip, params):
    # Check if the user is logged in
    if ip in logged_in_users.keys():
        db_handle = DBHandler('strife_db')

        username = logged_in_users[ip]
        chats = db_handle.get_chats_of(username)
        msg = Protocol.chats_list(chats)
        com.send_data(msg, ip)
    else:
        com.send_data(Protocol.reject(params['opcode']))


def handle_username_change(com, ip, params):
    pass


def handle_status_change(com, ip, params):
    pass


def handle_password_change(com, ip, params):
    pass


def handle_text_message(com, ip, params, raw):
    """
    Handles a text message sent from a client in some chat
    """
    # Check if the user is logged in
    if ip not in logged_in_users.keys():
        # do something
        pass

    else:
        db_handle = DBHandler('strife_db')
        chat_id = params['chat_id']
        sender = params['sender_username']
        message = params['message']

        db_handle.add_message(chat_id, sender, message)
        group_members_names = db_handle.get_group_members(chat_id)

        connected_members_ips = [get_ip_by_username(member_name)
                                 for member_name in group_members_names
                                 if member_name in logged_in_users.values()]

        com.send_data(raw, connected_members_ips)


def handle_file_description(com, ip, params, raw):
    # Check if the user is logged in
    if ip not in logged_in_users.keys():
        # do something
        pass

    else:
        db_handle = DBHandler('strife_db')
        chat_id = params['chat_id']
        sender = params['sender_username']


def handle_general_messages(com, q):
    """
    Handle the general messages
    :param com:
    :param q:
    :return:
    """
    while True:
        data, ip = q.get()

        # If a user has disconnected
        if data == '':
            if ip in logged_in_users.keys():
                del logged_in_users[ip]

        else:
            try:
                msg = Protocol.unprotocol_msg("general", data)
            except Exception:
                pass
            else:
                if msg['opname'] in general_dict.keys():
                    general_dict[msg['opname']](com, ip, msg)


def handle_chats_messages(com, q):
    while True:
        data, ip = q.get()
        try:
            msg = Protocol.unprotocol_msg("chats", data)
        except Exception as e:
            print(e)
        else:
            if msg['opname'] in messages_dict.keys():
                messages_dict[msg['opname']](com, ip, msg, data)


def handle_files_messages(com, q):
    while True:
        data, ip = q.get()
        try:
            msg = Protocol.unprotocol_msg("files", data)
        except Exception:
            pass
        else:
            if msg['opname'] in files_dict.keys():
                files_dict[msg['opname']](com, ip, msg)


def get_ip_by_username(username):
    return [target_ip for target_ip, name in logged_in_users.items() if name==username][0]


def install_packages():
    subprocess.call(['pip', 'install', 'pycryptodome', 'cryptography'])


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
    'change_password': handle_password_change
}

messages_dict = {
    'text_message': handle_text_message,
    'file_description': handle_file_description
}

files_dict = {

}

logged_in_users = {}


def main():
    install_packages()

    # Create the general messages queue
    general_queue = queue.Queue()
    # Create the communication object for the general messages
    general_com = ServerCom(1000, general_queue)
    # Start a thread to handle the general messages being received
    threading.Thread(target=handle_general_messages, args=(general_com, general_queue)).start()

    # Create the chat messages queue
    chats_queue = queue.Queue()
    # Create the communication object for the chat messages
    chats_com = ServerCom(2000, chats_queue, com_type='chats')
    # Start a thread to handle the chat messages being received
    threading.Thread(target=handle_chats_messages, args=(chats_com, chats_queue)).start()

    # Create the files messages queue
    files_queue = queue.Queue()
    # Create the communication object for the files messages
    files_com = ServerCom(3000, files_queue, com_type='files')
    # Start a thread to handle the files messages being received
    threading.Thread(target=handle_files_messages, args=(files_com, files_queue)).start()

    print('###### Strife server v0.1 started running ######\n')

    while True:
        input('')
        msg = Protocol.profile_picture('m')
        file_contents = open('src/core/logo.png', 'rb').read()
        files_com.send_data(msg)
        files_com.send_file(file_contents)


if __name__ == '__main__':
    main()
