import json

def send_to_server(data2send, s):
    data2send = json.dumps(data2send).encode()
    s.sendall(len(data2send).to_bytes(4, "little"))
    s.sendall(data2send)


def receive_from_server(s):
    rcv_size = int.from_bytes(s.recv(4), 'little')
    msg = json.loads(s.recv(rcv_size).decode())
    return msg