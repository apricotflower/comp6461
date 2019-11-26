import socket

from packet import Packet

TIMEOUT = 5
WINDOW_SIZE = 8

DATA_LEN = 10

SYN = 0
SYN_ACK = 1
ACK = 2
DATA = 3
FIN = 4


def receive_data(conn,packet_response, sender_seq,sender_addr,sender_port,sender,record,buffer):
    request = ""
    packet_ack = Packet(packet_type=ACK,
                        seq_num=sender_seq,
                        peer_ip_addr=sender_addr,
                        peer_port=sender_port,
                        payload=''.encode("utf-8"))

    conn.sendto(packet_ack.to_bytes(), sender)
    # receiving data
    if sender_seq in record:
        print("Receive repeat " + str(sender_seq))
    else:
        record.append(sender_seq)
        if packet_response.packet_type == DATA:
            buffer[sender_seq] = packet_response
            # if check_window(buffer):
            #     temp_content = ""
            #     for i in range(min(buffer), max(buffer)+1):
            #         temp_content += buffer[i].payload.decode("utf-8")
            #     request = request + temp_content
            #     buffer.clear()
        elif packet_response.packet_type == FIN:  # BUG，收到FIN返回ACK，ACK丢失对面等待重发FIN，这边已经进去，无法发送ACK
            print("Receive FIN!" + " The lengh of buffer is " + str(len(buffer)))
            print(buffer.keys())
            if check_window(buffer):
                temp_content = ""
                for i in range(min(buffer), max(buffer) + 1):
                    temp_content += buffer[i].payload.decode("utf-8")
                request = request + temp_content
                buffer.clear()
            print(request)
            return request


def check_window(buffer):
    window_complete = True
    for i in range(min(buffer), max(buffer) + 1):
        if i not in buffer.keys():
            window_complete = False
    return window_complete