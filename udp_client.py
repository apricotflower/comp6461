import argparse
import ipaddress
import socket

from packet import Packet

TIMEOUT = 5

MIN_LEN = 11
MAX_LEN = 1024

SYN = 0
SYN_ACK = 1
ACK = 2
DATA = 3


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
    print("Established！")


def run_client(router_addr, router_port, server_addr, server_port):
    handshake(router_addr, router_port, server_addr, server_port)

    # peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    # conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # timeout = 5
    # try:
    #     msg = "Hello World"
    #     p = Packet(packet_type=0,
    #                seq_num=1,
    #                peer_ip_addr=peer_ip,
    #                peer_port=server_port,
    #                payload=msg.encode("utf-8"))
    #     conn.sendto(p.to_bytes(), (router_addr, router_port))
    #     print('Send "{}" to router'.format(msg))
    #
    #     # Try to receive a response within timeout
    #     conn.settimeout(timeout)
    #     print('Waiting for a response')
    #     response, sender = conn.recvfrom(1024)
    #     p = Packet.from_bytes(response)
    #     print('Router: ', sender)
    #     print('Packet: ', p)
    #     print('Payload: ' + p.payload.decode("utf-8"))
    #
    # except socket.timeout:
    #     print('No response after {}s'.format(timeout))
    # finally:
    #     conn.close()


# Usage:
# python echoclient.py --routerhost localhost --routerport 3000 --serverhost localhost --serverport 8007

parser = argparse.ArgumentParser()
parser.add_argument("--routerhost", help="router host", default="localhost")
parser.add_argument("--routerport", help="router port", type=int, default=3000)

parser.add_argument("--serverhost", help="server host", default="localhost")
parser.add_argument("--serverport", help="server port", type=int, default=8007)
args = parser.parse_args()

run_client(args.routerhost, args.routerport, args.serverhost, args.serverport)
