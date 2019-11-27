import ipaddress
import socket
from packet import Packet
import threading


TIMEOUT = 5
WINDOW_SIZE = 8

DATA_LEN = 10

SYN = 0
SYN_ACK = 1
ACK = 2
DATA = 3
FIN = 4


def check_window(buffer):
    window_complete = True
    for i in range(min(buffer), max(buffer) + 1):
        if i not in buffer.keys():
            window_complete = False
    return window_complete


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


def send_data(msg, server_addr, server_port):
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
        #print("seq_num: " + str(sequence_num) + " Data: " + str(msg_process[:DATA_LEN]))
        send_packets.append(packet_data)
        sequence_num = sequence_num + 1
        # if sequence_num == WINDOW_SIZE:
        #     sequence_num = 1
        msg_process = msg_process[DATA_LEN:]

        # packet_fin = Packet(packet_type=FIN,
        #                     seq_num=sequence_num,
        #                     peer_ip_addr=peer_ip,
        #                     peer_port=server_port,
        #                     payload="".encode("utf-8"))
        # send_packets.append(packet_fin)

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
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_fin = Packet(packet_type=FIN,
                        seq_num=sequence_num,
                        peer_ip_addr=peer_ip,
                        peer_port=server_port,
                        payload="".encode("utf-8"))
    for i in range(0,20):
        conn.sendto(packet_fin.to_bytes(), (router_addr, router_port))

    # finished = False
    # while not finished:
    #     conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     packet_fin = Packet(packet_type=FIN,
    #                         seq_num=sequence_num,
    #                         peer_ip_addr=peer_ip,
    #                         peer_port=server_port,
    #                         payload="".encode("utf-8"))
    #     conn.sendto(packet_fin.to_bytes(), (router_addr, router_port))
    #     try:
    #         conn.settimeout(TIMEOUT)
    #         response, sender = conn.recvfrom(1024)
    #         packet_response = Packet.from_bytes(response)
    #         print("FIN: "+ str(packet_response.packet_type))
    #         if packet_response.packet_type == ACK:
    #             finished = True
    #             print("Receive ACK from Server. Client data finish !")
    #     except socket.timeout:
    #         print("Finish not ok")
    #     finally:
    #         conn.close()
