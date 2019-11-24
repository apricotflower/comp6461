import argparse
import socket

from packet import Packet


SYN = 0
SYN_ACK = 1
ACK = 2
DATA = 3


def run_server(port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    established = False
    try:
        conn.bind(('', port))
        print('Echo server is listening at', port)
        while True:
            data, sender = conn.recvfrom(1024)
            # print(data)
            # print(sender)
            packet_response = Packet.from_bytes(data)
            sender_addr = packet_response.peer_ip_addr
            sender_port = packet_response.peer_port
            sender_seq = packet_response.seq_num

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

            if established:
                print()



            # handle_client(conn, data, sender)

    finally:
        conn.close()


def handle_client(conn, data, sender):
    try:
        p = Packet.from_bytes(data)
        print("Router: ", sender)
        print("Packet: ", p)
        print("Payload: ", p.payload.decode("utf-8"))

        # How to send a reply.
        # The peer address of the packet p is the address of the client already.
        # We will send the same payload of p. Thus we can re-use either `data` or `p`.
        conn.sendto(p.to_bytes(), sender)

    except Exception as e:
        print("Error: ", e)


# Usage python udp_server.py [--port port-number]
parser = argparse.ArgumentParser()
parser.add_argument("--port", help="echo server port", type=int, default=8007)
args = parser.parse_args()
run_server(args.port)
