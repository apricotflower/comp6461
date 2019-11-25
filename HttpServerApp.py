import socket
import argparse
import os
import mimetypes
import threading

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

GET = "get"
POST = "post"
READ_ONLY_FOLDER = "readonly"

threadLock = threading.Lock()


def add_headers(operation):
    headers = ""
    if operation == GET:
        for header in request[1:]:
            headers = headers + "\r\n" + str(header.strip("\r\n"))
    elif operation == POST:
        for header in request[1:-1]:
            headers = headers + "\r\n" + str(header.strip("\r\n"))
    return headers.lstrip("\r\n")


def find_accept_key():
    accept_key = []
    for line in request:
        if "content-type" in line.lower():
            accept_key.append(line.rsplit(":")[1])
    if args.verbose:
        print("accept_key: "+str(accept_key))
    return accept_key


def find_disposition_name():
    disposition_filename = ""
    have_attachment = False
    for line in request:
        if "content-disposition" in line.lower():
            if args.verbose:
                print("content-disposition in headers!")
            if "inline" in line.lower():
                continue
            elif "attachment" in line.lower():
                if args.verbose:
                    print("Attachment in parameters!")
                parameters = line.rsplit(":", 1)[1].split(";")
                for para in parameters:
                    if "filename" in para:
                        disposition_filename = para.split("=")[1]
                        if args.verbose:
                            print("filename is " + disposition_filename)
                have_attachment = True
            elif "form-data" in line.lower():
                continue
    return have_attachment, disposition_filename


def get_operation(path):
    # threadLock.acquire()
    head = request[0].split()[2]
    body = ""
    r_path = args.directory.rstrip("/") + path

    if os.path.isfile(r_path):
        # request_file = path.rsplit("/", 1)[-1]
        if args.verbose:
            print("It is a file in the target! Found " + str(r_path))
        fo = open(r_path)
        lines = fo.read() + "\r\n"
        head = head + " 200 OK"+"\r\n"
        body = body + lines
        fo.close()
        if args.verbose:
            print("200 OK")
            print(lines)
        have_attachment, disposition_filename = find_disposition_name()
        if have_attachment:
            if args.verbose:
                print("Downloading in " + disposition_filename)
            wfo = open(args.directory.rstrip("/") + "/" + disposition_filename, "w+")
            wfo.write(lines)
            wfo.close()

    else:
        if args.verbose:
            print("Request do not ask exact file, try to start printing a list of the current files……")
        accept_key = find_accept_key()
        if os.path.exists(r_path):
            if args.verbose:
                print("Path is exited! Returning files name……")
            head = head + " 200 OK" + "\r\n"
            if accept_key:
                for file in os.listdir(r_path):
                    if not os.path.isdir(file):
                        file_type = mimetypes.MimeTypes().guess_type(file)[0]
                        if args.verbose:
                            print("file: "+str(file) + " file_type: " + str(file_type))
                        if str(file_type) in str(accept_key):
                            body = body + '\r\n ' + file
            else:
                for file in os.listdir(r_path):
                    if not os.path.isdir(file):
                        body = body + '\r\n ' + file
            if args.verbose:
                print("File list: " + str(body))
        else:
            head = head + " 404 not exit" + "\r\n"
            if args.verbose:
                print("path is not exited, return HTTP ERROR 404")

    head = head + add_headers(GET)

    response = head.strip("\r\n") + "\r\n\r\n" + body.strip("\r\n")
    return response
    # conn.sendall(response.encode('utf-8'))
    # conn.close()
    # threadLock.release()


def post_operation(path):
    # threadLock.acquire()
    head = request[0].split()[2]
    body = ""
    temp_head = add_headers(POST)
    r_path = args.directory.rstrip("/") + path
    if args.verbose:
        print("Path is " + r_path)
    if path[-1] != "/" and READ_ONLY_FOLDER not in r_path.lower() and os.path.isdir(r_path.rsplit("/", 1)[0] + "/"):
        # request_file = path.rsplit("/", 1)[-1]
        if args.verbose:
            print("Target file is " + r_path)
        if "overwrite=true" in temp_head.lower():
            if args.verbose:
                print("overwrite=true in the header, data can be overwritten……")
            head = head + " 200 OK" + "\r\n"
            fo = open(r_path, "w+")
            fo.write(request[-1]+"\n")
            body = request[-1]
            fo.close()
        else:
            head = head + " 200 OK" + "\r\n"
            if args.verbose:
                print("overwrite=true not the header, data can not be overwriten……")
            if not os.path.isfile(r_path):
                fo = open(r_path, "a+")
                if args.verbose:
                    print("The file is not exit! Creating a new file……")
                fo.write(request[-1])
            else:
                fo = open(r_path, "a+")
                if args.verbose:
                    print("The file exit! Appending the data……")
                fo.write("\n" + request[-1])
            body = request[-1]
            fo.close()

        have_attachment, disposition_filename = find_disposition_name()
        if have_attachment:
            if args.verbose:
                print("Downloading in " + disposition_filename)
            fo2 = open(r_path)
            lines = fo2.read() + "\r\n"
            wfo = open(args.directory.rstrip("/") + "/" + disposition_filename, "w+")
            wfo.write(lines)
            fo2.close()
            wfo.close()
    else:
        if READ_ONLY_FOLDER in r_path.lower():
            if args.verbose:
                print("Requesting for a read only file. Forbidden!")
            head = head + " 403 Forbidden" + "\r\n"
        elif not os.path.isdir(r_path.rsplit("/", 1)[0] + "/"):
            if args.verbose:
                print("Path not exit")
            head = head + " 404 not exit" + "\r\n"
        elif path[-1] == "/":
            if args.verbose:
                print("Do not have target file in the path!")
            head = head + " 404 not exit" + "\r\n"
        else:
            head = head + " 404 not exit" + "\r\n"

    head = head + temp_head

    response = head.strip("\r\n") + "\r\n\r\n" + body.strip("\r\n")
    return response
    # conn.sendall(response.encode('utf-8'))
    # conn.close()
    # threadLock.release()

# def run_server():
#     threads = []
#     global request
#     host = "localhost"
#     listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     listener.bind((host, args.port))
#     listener.listen(10)
#     while True:
#         conn, addr = listener.accept()
#         request = conn.recv(1024).decode("utf-8")
#         if args.verbose:
#             print("**"*40)
#             print("Client from addr:" + str(addr))
#             print("Receive request: " + str(request))
#         request = request.split('\r\n')
#         line_1 = request[0].split()
#         method = line_1[0]
#         request_path = line_1[1]
#         if args.verbose:
#             print("request_path: " + request_path)
#             print("method: " + method)
#         if method.lower() == GET:
#             thread = threading.Thread(target=get_operation, args=(request_path, conn))
#         elif method.lower() == POST:
#             thread = threading.Thread(target=post_operation, args=(request_path, conn))
#
#         thread.start()
#         threads.append(thread)
#         thread.join()


def run_server(port):
    global request
    buffer = {}
    record = []
    request = ""
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
                            request = request + temp_content
                            buffer.clear()
                    elif packet_response.packet_type == FIN:
                        print(request)
                        handle_client("localhost", 41830)

    finally:
        conn.close()


def check_window(buffer):
    window_complete = True
    for i in range(min(buffer, key=buffer.get), max(buffer, key=buffer.get) + 1):
        if i not in buffer.keys():
            window_complete = False
    return window_complete


def handle_client( server_addr, server_port):
    global request
    request = request.split('\r\n')
    line_1 = request[0].split()
    method = line_1[0]
    request_path = line_1[1]
    if args.verbose:
        print("request_path: " + request_path)
        print("method: " + method)
    if method.lower() == GET:
        # thread = threading.Thread(target=get_operation, args=(request_path, conn))
        msg = get_operation(request_path)
    elif method.lower() == POST:
        # thread = threading.Thread(target=post_operation, args=(request_path, conn))
        msg = post_operation(request_path)

    # thread.start()
    # thread.join()

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'httpfs is a simple file server. usage: httpfs [-v] [-p PORT] [-d PATH-TO-DIR]')
    parser.add_argument(dest='httpfs', action="store", nargs='*')
    parser.add_argument('-v', dest='verbose',action='store_true', help='Prints debugging messages.')
    parser.add_argument('-p', dest='port', action="store",type=int,default=8080, help='Specifies the port number that the server will listen and serve at.')
    parser.add_argument('-d', dest='directory', action='store', type=str, default='./', help='Specifies the directory that the server will use to read/write requested files. Default is the current directory when launching the application.')
    args = parser.parse_args()

    if args.verbose:
        # print(args.httpfs)
        print("Print debugging messages: " + str(args.verbose))
        print("Port: " + str(args.port))
        print("Directory that the server will use: " + str(args.directory))

    run_server(args.port)

# httpfs -v -p 8081 -d /Users/wangjiahui/Desktop/comp6461/testfolder

# httpc get -v 'http://localhost:8080'
# httpc get -v 'http://localhost:8080/testfolder'
# httpc get -v 'http://localhost:8080/a.txt'
# httpc get -v -h Content-Type:text/plain 'http://localhost:8080/testfolder'
# httpc get -v -h Content-Type:application/json 'http://localhost:8080'
# httpc get -v -h Content-Type:application/xml'http://localhost:8080'
# httpc get -v -h Content-Type:text/html 'http://localhost:8080'
# httpc post -v -d '{This is a modification}' 'http://localhost:8080/a.txt'
# httpc post -v -d 'This_is_a_modification' -h overwrite=true 'http://localhost:8080/a.txt'
# httpc post -v -d 'This_is_a_modification' -h overwrite=false 'http://localhost:8080/a.txt'
# httpc post -v -f 'data.txt' 'http://localhost:8080/a.txt'

# httpc get -v 'http://localhost:8080/ReadOnly/a.txt'
# httpc post -v -d 'This_is_a_modification' 'http://localhost:8080/ReadOnly/a.txt'
