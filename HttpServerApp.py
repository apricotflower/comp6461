import socket
import argparse
import os
import mimetypes
import threading


GET = "get"
POST = "post"

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
                parameters = line.rsplit(":")[1].split(";")
                for para in parameters:
                    if "filename" in para:
                        disposition_filename = para.split("=")[1]
                        if args.verbose:
                            print("filename is " + disposition_filename)
                have_attachment = True
            elif "form-data" in line.lower():
                continue
    if args.verbose:
        print("Content-Disposition: " + str(disposition_filename))
    return have_attachment, disposition_filename


def get_operation(path, conn):
    threadLock.acquire()
    head = request[0].split()[2]
    body = ""
    r_path = args.directory.rstrip("/") + path

    if os.path.isfile(r_path):
        # request_file = path.rsplit("/", 1)[-1]
        if args.verbose:
            # print("Request ask exact file, start printing detail in file " + request_file)
            print("Found " + str(r_path))
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
            print("Request do not ask exact file, start printing a list of the current files……")
            print("Returning files name……")
        accept_key = find_accept_key()
        if os.path.exists(r_path):
            head = head + " 200 OK" + "\r\n"
            for file in os.listdir(r_path):
                if not os.path.isdir(file):
                    file_type = mimetypes.MimeTypes().guess_type(file)[0]
                    if args.verbose:
                        print("file: "+str(file) + " file_type: "+ str(file_type))
                    if str(file_type) in str(accept_key):
                        body = body + '\r\n ' + file
            if args.verbose:
                print("File list: " + str(body))
        else:
            head = head + " 404" + "\r\n"
            if args.verbose:
                print("path is not exit, return HTTP ERROR 404")

    head = head + add_headers(GET)

    response = head.strip("\r\n") + "\r\n\r\n" + body.strip("\r\n")
    conn.sendall(response.encode('utf-8'))
    conn.close()
    threadLock.release()
    # return head, body


def post_operation(path, conn):
    threadLock.acquire()
    head = request[0].split()[2]
    body = ""
    temp_head = add_headers(POST)
    r_path = args.directory.rstrip("/") + path
    if args.verbose:
        print("Path is " + r_path)
    if path[-1] != "/":
        # request_file = path.rsplit("/", 1)[-1]
        if args.verbose:
            print("Target file is " + r_path)
        # file_path = args.directory + path.rsplit("/", 1)[0].lstrip("/")
        # file_path = file_path.rstrip("/") + "/"
        if "overwrite=true" in temp_head.lower():
            if args.verbose:
                print("overwrite=true in the header, data can be overwritten……")
            head = head + " 200 OK" + "\r\n"
            fo = open(r_path, "w+")
            fo.write(request[-1]+"\n")
            body = request[-1]
            fo.close()
        else:
            if args.verbose:
                print("overwrite=true not the header, data can not be overwriten……")
            head = head + " 200 OK" + "\r\n"
            fo = open(r_path, "a+")
            fo.write(request[-1] + "\n")
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
        head = head + " 404" + "\r\n"

    head = head + temp_head

    response = head.strip("\r\n") + "\r\n\r\n" + body.strip("\r\n")
    conn.sendall(response.encode('utf-8'))
    conn.close()
    threadLock.release()
    # return head, body


def run_server():
    threads = []
    global request
    host = "localhost"
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind((host, args.port))
    listener.listen(10)
    while True:
        conn, addr = listener.accept()
        request = conn.recv(1024).decode("utf-8")
        if args.verbose:
            print("Client from addr:" + str(addr))
            print("Receive request: " + str(request))
        request = request.split('\r\n')
        line_1 = request[0].split()
        method = line_1[0]
        request_path = line_1[1]
        if args.verbose:
            print("request_path: " + request_path)
            print("method: " + method)
        if method.lower() == GET:
            # get_operation(request_path, conn)
            thread = threading.Thread(target=get_operation, args=(request_path, conn))
        elif method.lower() == POST:
            # post_operation(request_path, conn)
            thread = threading.Thread(target=post_operation, args=(request_path, conn))

        thread.start()
        threads.append(thread)
        thread.join()

    # for t in threads:
    #     t.join()
    # if args.verbose:
    #     print("All servers finish!")

        # response = head.strip("\r\n") + "\r\n\r\n" + body.strip("\r\n")
        # conn.sendall(response.encode('utf-8'))
        # conn.close()


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

    run_server()

