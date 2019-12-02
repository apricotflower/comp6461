import argparse
import socket
import ipaddress
import threading
import send_data_helper

from packet import Packet

TIMEOUT = 5
WINDOW_SIZE = 8

DATA_LEN = 10

SYN = 0
SYN_ACK = 1
ACK = 2
DATA = 3
FIN = 4

SERVER_ADDRESS = "localhost"
SERVER_PORT = 8007
CLIENT_ADDRESS = "localhost"
CLIENT_PORT = 41830


def run_server(port):
    global request
    buffer = {}
    record = []
    request = ""
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    established = False
    pre_seq = 0

    try:
        conn.bind((SERVER_ADDRESS, port))
        print('Server is listening at', port)
        while True:
            data, sender = conn.recvfrom(1024)
            packet_response = Packet.from_bytes(data)
            sender_addr = packet_response.peer_ip_addr
            sender_port = packet_response.peer_port
            sender_seq = packet_response.seq_num

            if not established:
                # handshake step
                if packet_response.packet_type == SYN:
                    print("Receive handshake SYN from " + str(sender_addr) + " : " + str(sender_port))
                    packet_syn_ack = Packet(packet_type=SYN_ACK,
                                            seq_num=0,
                                            peer_ip_addr=sender_addr,
                                            peer_port=sender_port,
                                            payload=''.encode("utf-8"))
                    conn.sendto(packet_syn_ack.to_bytes(), sender)
                    print("Sending response SYN_ACK ……")
                elif packet_response.packet_type == ACK:
                    print("Receive ACK ! Established !")
                    established = True

            else:
                # request = receive_data_helper.receive_data(2,conn,request,record,buffer,pre_seq)
                packet_ack = Packet(packet_type=ACK,
                                    seq_num=sender_seq,
                                    peer_ip_addr=sender_addr,
                                    peer_port=sender_port,
                                    payload=''.encode("utf-8"))

                conn.sendto(packet_ack.to_bytes(), sender)
                # receiving data
                if sender_seq in record:
                    if packet_response.packet_type != FIN and sender_seq != 0:
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
                                for i in range(min(buffer), max(buffer)+1):
                                    temp_content += buffer[i].payload.decode("utf-8")
                                request = request + temp_content
                                pre_seq = pre_seq + len(buffer)
                                buffer.clear()

                    elif packet_response.packet_type == FIN: #BUG，收到FIN返回ACK，ACK丢失对面等待重发FIN，这边已经进去handle_client不在监听，无法发送ACK
                        # print("Receive FIN!" + " The lengh of buffer is " + str(len(buffer)))
                        # print(buffer.keys())
                        print(request)
                        # time.sleep(5)
                        handle_client(request,"localhost", 41830)

    finally:
        conn.close()


def check_window(buffer):
    window_complete = True
    for i in range(min(buffer), max(buffer) + 1):
        if i not in buffer.keys():
            window_complete = False
    return window_complete


def handle_client(request_content, server_addr, server_port):
    msg = "small" + request_content + " big "

    send_data_helper.send_data(msg, server_addr, server_port)


# Usage python udp_server.py [--port port-number]
# parser = argparse.ArgumentParser()
# parser.add_argument("--port", help="echo server port", type=int, default=8007)
# args = parser.parse_args()
# run_server(args.port)


run_server(SERVER_PORT)