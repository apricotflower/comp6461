import HttpServerApp

from packet import Packet

TIMEOUT = 5
WINDOW_SIZE = 8

DATA_LEN = 10

SYN = 0
SYN_ACK = 1
ACK = 2
DATA = 3
FIN = 4

CLIENT = 1
SERVER =2


def receive_data(client_server,conn,request,record,buffer,pre_seq):
    data, sender = conn.recvfrom(1024)
    packet_response = Packet.from_bytes(data)
    sender_addr = packet_response.peer_ip_addr
    sender_port = packet_response.peer_port
    sender_seq = packet_response.seq_num

    packet_ack = Packet(packet_type=ACK,
                        seq_num=sender_seq,
                        peer_ip_addr=sender_addr,
                        peer_port=sender_port,
                        payload=''.encode("utf-8"))

    conn.sendto(packet_ack.to_bytes(), sender)
    # receiving data
    if sender_seq in record:
        if packet_response.packet_type != FIN:
            print("Receive repeat " + str(sender_seq))
    else:
        record.append(sender_seq)
        if packet_response.packet_type == DATA:
            if packet_response.seq_num == pre_seq + 1:
                request = request + packet_response.payload.decode("utf-8")
                pre_seq = pre_seq + 1
            else:
                buffer[sender_seq] = packet_response
            if len(buffer) != 0:
                if check_window(buffer) and min(buffer) == pre_seq + 1:
                    temp_content = ""
                    for i in range(min(buffer), max(buffer) + 1):
                        temp_content += buffer[i].payload.decode("utf-8")
                    request = request + temp_content
                    pre_seq = pre_seq + len(buffer)
                    buffer.clear()
        elif packet_response.packet_type == FIN:
            conn.close()
            # print(request)
            if client_server == CLIENT:
                return request
            elif client_server == SERVER:
                return request
                HttpServerApp.handle_client("localhost", 41830)
            # print(request_content)


def check_window(buffer):
    window_complete = True
    for i in range(min(buffer), max(buffer) + 1):
        if i not in buffer.keys():
            window_complete = False
    return window_complete