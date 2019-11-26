import argparse
import ipaddress
import socket
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


def handshake(router_addr, router_port, server_addr, server_port):
    established = False
    while not established:
        ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("First handshake SYN is sending ……")
        packet_syn = Packet(packet_type=SYN,
                        seq_num=0,
                        peer_ip_addr=ip,
                        peer_port=server_port,
                        payload="".encode("utf-8"))
        conn.sendto(packet_syn.to_bytes(), (router_addr, router_port))
        print("Waiting for response SYN_ACK ……")
        try:
            conn.settimeout(TIMEOUT)
            response, sender = conn.recvfrom(1024)
            packet_response = Packet.from_bytes(response)
            if packet_response.packet_type == SYN_ACK:
                print("Receive response SYN_ACK from " + str(packet_response.peer_ip_addr) + " : " + str(packet_response.peer_port))
                established = True
                packet_ack = Packet(packet_type=ACK,
                                seq_num=1,
                                peer_ip_addr=ip,
                                peer_port=server_port,
                                payload="".encode("utf-8"))
                conn.sendto(packet_ack.to_bytes(), (router_addr, router_port))
        except socket.timeout:
            print("Handshake fail, handshake again……")
        finally:
            conn.close()


def receive():
    port = 41830
    buffer = {}
    record = []
    request_content = ""
    # first_fin = True
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.bind(('', port))
        # print('Echo server is listening at', port)
        while True:
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
                print("Receive repeat " + str(sender_seq))
            else:
                record.append(sender_seq)
                if packet_response.packet_type == DATA:
                    buffer[sender_seq] = packet_response
                    if check_window(buffer) and len(buffer) == WINDOW_SIZE:
                        temp_content = ""
                        for i in range(min(buffer), max(buffer)+1):
                            temp_content += buffer[i].payload.decode("utf-8")
                        request_content = request_content + temp_content
                        buffer.clear()
                elif packet_response.packet_type == FIN:
                    # first_fin = False
                    if check_window(buffer):
                        temp_content = ""
                        for i in range(min(buffer), max(buffer) + 1):
                            temp_content += buffer[i].payload.decode("utf-8")
                        request_content = request_content + temp_content
                        buffer.clear()
                    conn.close()
                    return request_content
                    # print(request_content)
    finally:
        conn.close()


def check_window(buffer):
    window_complete = True
    for i in range(min(buffer), max(buffer) + 1):
        if i not in buffer.keys():
            window_complete = False
    return window_complete


def run_client(msg, server_addr, server_port):
    router_addr = "localhost"
    router_port = 3000
    # sequence_num = 1

    print("Start handshaking ……")
    handshake(router_addr, router_port, server_addr, server_port)
    print("Established！")

    send_data_helper.send_data(msg, server_addr, server_port)



# Usage:
# python echoclient.py --routerhost localhost --routerport 3000 --serverhost localhost --serverport 8007
# router_x64.exe --port=3000 --drop-rate=0.2 --max-delay=10ms --seed=1


msg = "The peer address of a packet also has two meanings. When you send a packet, the peer address is the address of the destination that you want to send. "
#msg = "hello"
serverhost = "localhost"
serverport = 8007

# run_client(msg, serverhost, serverport)
# print(receive())
