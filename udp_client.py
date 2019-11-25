import argparse
import ipaddress
import socket
import threading

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


def send_data_packet_in_window(packet, router_addr, router_port):
    while packet.packet_type != ACK:
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn.sendto(packet.to_bytes(), (router_addr, router_port))
        try:
            conn.settimeout(TIMEOUT)
            response, sender = conn.recvfrom(1024)
            packet = Packet.from_bytes(response)
            if packet.packet_type == ACK:
                conn.close()
                break
        except socket.timeout:
            print("Response timeout ! Resend packet " + str(packet.seq_num))
        finally:
            conn.close()


def receive():
    port = 41830
    buffer = {}
    record = []
    request_content = ""
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
                    # if check_window(buffer):
                    #     temp_content = ""
                    #     for i in range(min(buffer, key=buffer.get), max(buffer, key=buffer.get)+1):
                    #         temp_content += buffer[i].payload.decode("utf-8")
                    #     request_content = request_content + temp_content
                    #     buffer.clear()
                elif packet_response.packet_type == FIN:
                    if check_window(buffer):
                        temp_content = ""
                        for i in range(min(buffer), max(buffer) + 1):
                            temp_content += buffer[i].payload.decode("utf-8")
                        request_content = request_content + temp_content
                        buffer.clear()
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
    sequence_num = 1

    print("Start handshaking ……")
    handshake(router_addr, router_port, server_addr, server_port)
    print("Established！")

    print("Start sending data ……")
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))

    # separate the data into packet
    print("Separating the data into packet ……")
    send_packets = []
    msg_process = msg
    while len(msg_process) != 0:
        packet_data = Packet(packet_type=DATA,
                             seq_num=sequence_num,
                             peer_ip_addr=peer_ip,
                             peer_port=server_port,
                             payload=msg_process[:DATA_LEN].encode("utf-8")
                             )
        print("seq_num: " + str(sequence_num) + " Data: " + str(msg_process[:DATA_LEN]))
        send_packets.append(packet_data)
        sequence_num = sequence_num + 1
        # if sequence_num == WINDOW_SIZE:
        #     sequence_num = 1
        msg_process = msg_process[DATA_LEN:]

    print("Start sending windows ……")
    while len(send_packets) != 0:
        threads = []
        for packet in send_packets[:WINDOW_SIZE]:
            print("Packet " + str(packet.seq_num) + " is sending ……")
            # send_data_packet_in_window(packet, router_addr, router_port)
            thread = threading.Thread(target=send_data_packet_in_window, args=(packet, router_addr, router_port))
            thread.start()
            # thread.join()
            threads.append(thread)
        for t in threads:
            t.join()
        send_packets = send_packets[WINDOW_SIZE:]

    send_packets.clear()

    print("Finishing client data ……")
    finished = False
    while not finished:
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        packet_syn = Packet(packet_type=FIN,
                            seq_num=sequence_num,
                            peer_ip_addr=peer_ip,
                            peer_port=server_port,
                            payload="".encode("utf-8"))
        conn.sendto(packet_syn.to_bytes(), (router_addr, router_port))
        try:
            conn.settimeout(TIMEOUT)
            response, sender = conn.recvfrom(1024)
            packet_response = Packet.from_bytes(response)
            if packet_response.packet_type == ACK:
                finished = True
                print("Receive ACK from Server. Client data finish !")
        except socket.timeout:
            print("Finish not ok")
        finally:
            conn.close()


# Usage:
# python echoclient.py --routerhost localhost --routerport 3000 --serverhost localhost --serverport 8007
# router_x64.exe --port=3000 --drop-rate=0.2 --max-delay=10ms --seed=1


msg = "The peer address of a packet also has two meanings. When you send a packet, the peer address is the address of the destination that you want to send. "
#msg = "hello"
serverhost = "localhost"
serverport = 8007

# run_client(msg, serverhost, serverport)
# print(receive())
