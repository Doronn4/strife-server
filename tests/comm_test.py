import queue

from code.core.server_com import ServerCom
from code.core.server_protocol import Protocol

q = queue.Queue()
com = ServerCom(1000, q)

msg = Protocol.added_to_group('iftah fans', 69, 'blablablakey')


while True:
    msg, addr = q.get()
    msg = Protocol.unprotocol_msg('general', msg)
    print('msg received', msg)
    if msg['opname'] == 'sign_in':
        print('yo')
        username = msg['username']
        password = msg['password']
        if username == 'm' and password == 'm':
            print('approved')
            m = Protocol.approve(msg['opcode'])
            print(m)
            com.send_data(m, addr)
