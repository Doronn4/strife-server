import queue
import threading
from code.core.server_com import ServerCom
from code.core.server_protocol import Protocol
from code.handlers.db import DBHandler


def handle_register(com, ip, params):
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
    db_handle = DBHandler('strife_db')
    username = params['username']
    password = params['password']
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
    pass


def handle_friend_remove(com, ip, params):
    pass


def handle_group_creation(com, ip, params):
    db_handle = DBHandler('strife_db')

    group_name = params['group_name']
    # TODO: generate a new aes key
    group_key = 'ABCD'.encode()*8

    creator_username = logged_in_users[ip]
    # Create the group and save it's id
    group_id = db_handle.create_group(group_name, creator_username)
    # Create a message that indicates that the creator of the group was added to the group
    msg = Protocol.added_to_group(group_name, group_id, group_key)
    # Send the message to the client (creator)
    com.send_data(msg, ip)


def handle_add_group_member(com, ip, params):
    db_handle = DBHandler('strife_db')

    chat_id = params['chat_id']
    username = params['new_member_username']
    group_key = params['group_key']
    adder = logged_in_users[ip]

    flag = db_handle.add_to_group(chat_id, adder, username)

    if flag:
        added_msg = Protocol.added_to_group(db_handle.get_group_name(chat_id), chat_id, group_key)
        com.send_data(added_msg)

    msg = Protocol.approve(params['opcode']) if flag else Protocol.reject(params['opcode'])
    com.send_data(msg, ip)


general_dict = {
    'register': handle_register,
    'sign_in': handle_login,
    'add_friend': handle_friend_add,
    'create_group': handle_group_creation,
    'add_group_member': handle_add_group_member,
}

logged_in_users = {}


def handle_general_messages(com, queue):
    """
    Handle the general messages
    :param com:
    :param queue:
    :return:
    """
    while True:
        data, ip = queue.get()
        msg = Protocol.unprotocol_msg("general", data)
        if msg['opname'] in general_dict.keys():
            general_dict[msg['opname']](com, ip, msg)


def handle_chats_messages(com, queue):
    while True:
        data, ip = queue.get()
        msg = Protocol.unprotocol_msg("chats", data)


def handle_files_messages(com, queue):
    while True:
        data, ip = queue.get()
        msg = Protocol.unprotocol_msg("files", data)


if __name__ == '__main__':
    # Create the general messages queue
    general_queue = queue.Queue()
    # Create the communication object for the general messages
    general_com = ServerCom(1000, general_queue)
    # Start a thread to handle the general messages being received
    threading.Thread(target=handle_general_messages, args=(general_com, general_queue)).start()

    chats_queue = queue.Queue()
    chats_com = ServerCom(2000, chats_queue)
    threading.Thread(target=handle_chats_messages, args=(chats_com, chats_queue)).start()

    files_queue = queue.Queue()
    files_com = ServerCom(3000, files_queue)
    threading.Thread(target=handle_files_messages, args=(files_com, files_queue)).start()

    print('###### Strife server v0.1 started running ######')
