import argparse
import socket
import ipaddress

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
    buffer = {}
    record = []
    request_content = ""
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    established = False

    try:
        conn.bind((SERVER_ADDRESS, port))
        print('Echo server is listening at', port)
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
                        if check_window(buffer):
                            temp_content = ""
                            for i in range(min(buffer, key=buffer.get), max(buffer, key=buffer.get)+1):
                                temp_content += buffer[i].payload.decode("utf-8")
                            request_content = request_content + temp_content
                            buffer.clear()
                    elif packet_response.packet_type == FIN:
                        print(request_content)
                        handle_client(request_content,"localhost", 41830)
    finally:
        conn.close()


def check_window(buffer):
    window_complete = True
    for i in range(min(buffer, key=buffer.get), max(buffer, key=buffer.get) + 1):
        if i not in buffer.keys():
            window_complete = False
    return window_complete


def handle_client(request_content, server_addr, server_port):
    msg = "small shit " + request_content + " big shit "

    router_addr = "localhost"
    router_port = 3000
    sequence_num = 1
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
        for packet in send_packets[:WINDOW_SIZE]:
            print("Packet " + str(packet.seq_num) + " is sending ……")
            send_data_packet_in_window(packet, router_addr, router_port)
        send_packets = send_packets[WINDOW_SIZE:]

    send_packets.clear()

    print("Finishing server data ……")
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
                print("Receive ACK from Client.Server data finish !")
        except socket.timeout:
            print("Finish not ok")
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


# Usage python udp_server.py [--port port-number]
# parser = argparse.ArgumentParser()
# parser.add_argument("--port", help="echo server port", type=int, default=8007)
# args = parser.parse_args()
# run_server(args.port)


run_server(SERVER_PORT)