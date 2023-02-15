import queue

from code.core.server_com import ServerCom
from code.core.server_protocol import Protocol

q = queue.Queue()
com = ServerCom(1000, q)

protocol = Protocol()

msg = protocol.added_to_group('iftah fans', 69, 'blablablakey')
print(msg)


while True:
    input()

    if len(list(com.open_clients.values())) > 0:
        print(list(com.open_clients.values())[0])
        com.send_data(msg.encode(), list(com.open_clients.values())[0])
