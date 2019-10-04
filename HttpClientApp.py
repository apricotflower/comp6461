import socket
import urllib.parse
import os

GET = "get"
POST = "post"
DETAIL = "-v"
HEAD = "-h"
QUERY = "query"
HEADER = "header"
BODY = "body"
POST_DATA = "-d"
POST_FILE = "-f"
OUTPUT = "-o"
HELP = "help"
EXIT = "exit"

def send_receive_data(host, abs_path, port, operation, headers, request_data):
    # print("host: " + host)
    # print("abs_url:" + abs_path)
    # print("headers: " + headers)
    # print("request_data: " + request_data)
    # print("**"*20)
    request = ""

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((host, port))
    scheme_version_header = " HTTP/1.0\r\n"
    if headers != "":
        headers = headers + "\r\n"
    if "Host:" not in headers:
        headers = headers + "Host: " + host + ":" + str(port) + "\r\n"

    if operation == GET:
        do = "GET "
        if abs_path == "":
            do = "GET /"
        request_line = do + abs_path + scheme_version_header + headers + "\r\n"
        request = request_line + "\r\n"
    elif operation == POST:
        do = "POST "
        if abs_path == "":
            do = "POST /"
        if "Content-Length:" not in headers:
            headers = headers + "Content-Length: " + str(len(request_data)) + "\r\n"
        request = do + abs_path + scheme_version_header + headers + "\r\n" + request_data

    # print(request)
    my_socket.send(request.encode('utf-8'))
    # my_socket.send(request.encode('ISO-8859-1'))
    data = ""
    while True:
        buf_data = my_socket.recv(1024).decode('ISO-8859-1')
        # buf_data = my_socket.recv(1024).decode('utf-8')
        data = data + buf_data
        if not buf_data:
            break
    result_head, result_body = data.split('\r\n\r\n', 1)
    my_socket.close()
    return result_head, result_body


def deal_url(url):
    p_url = urllib.parse.urlparse(url)

    global p_scheme
    p_scheme = p_url.scheme

    host = p_url.netloc

    path = p_url.path

    query = p_url.query
    if query != "":
        query = "?" + query

    port = p_url.port

    if port is None:
        port = 80

    abs_path = path + query

    return host, abs_path, port,query


def redirect_analyse_url(host, re_location):
    if "://" in re_location:
        target_url = re_location
    else:
        target_url = p_scheme + "://" + host + re_location
    return target_url


def start_redirect(host, result_head, url_index):
    re_location = ""
    result_head_list = result_head.split("\r\n")

    for line in result_head_list:
        if "location:" in line.lower():
            re_location = line.split(" ")[1].strip()
            # print("re_location: " + re_location)

    if re_location == "":
        print("No new location in response…Redirection fail! ")
        return

    target_url = redirect_analyse_url(host, re_location)
    request_list[url_index] = target_url
    # print("Redirect url to: " + target_url)
    choose_operation()


def decide_redirection(host, result_head, url_index):
    if "301" in result_head.split("\r\n")[0] or "302" in result_head.split("\r\n")[0] or "303" in result_head.split("\r\n")[0] or "307" in result_head.split("\r\n")[0] or "308" in result_head.split("\r\n")[0]:
        print("\r\n" + "**"*80 + "\r\n" + "Start redirecting……")
        start_redirect(host, result_head, url_index)


def output(print_detail, print_in_file, result_head, result_body, file_name):
    if print_detail:
        output_content = result_head + "\r\n" + result_body
    else:
        output_content = result_body
    print(output_content)

    if print_in_file:
        with open(file_name, 'ab') as f:
            output_content = output_content + "\r\n\r\n"
            f.write(output_content.encode('utf-8'))


def get_operation():
    print_detail = False
    key_value = ""
    print_in_file = False
    file_name = ""
    url_index = -1

    for index, element in enumerate(request_list):
        if element.lower() == DETAIL:
            print_detail = True
        if element.lower() == HEAD:
            key_value = key_value + "\r\n" + request_list[index+1]
        if element.lower() == OUTPUT:
            print_in_file = True
            file_name = request_list[index+1]

        if "://" in element:
            host, abs_path, port, query = deal_url(element)
            url_index = index

    key_value = key_value.lstrip("\r\n")
    result_head, result_body = send_receive_data(host, abs_path, port, GET, key_value, "")

    # if "400" in result_head or "401" in result_head or "403" in result_head or "404" in result_head :
    #     exit()

    output(print_detail, print_in_file, result_head, result_body, file_name)

    decide_redirection(host, result_head, url_index)

    request_list.clear()
    main()


def post_operation():
    print_detail = False
    key_value = ""
    print_in_file = False
    file_name = ""
    request_data = ""
    url_index = -1

    for index, element in enumerate(request_list):
        if element.lower() == DETAIL:
            print_detail = True
        if element.lower() == HEAD:
            key_value = key_value + "\r\n" + request_list[index + 1]
        if element.lower() == OUTPUT:
            print_in_file = True
            file_name = request_list[index+1]
        if element.lower() == POST_DATA:
            request_data = request_list[index+1]
        if element.lower() == POST_FILE:
            f = open(request_list[index+1], 'r')
            request_data = f.read()
        if "://" in element:
            host, abs_path, port, query = deal_url(element)
            url_index = index

    key_value = key_value.lstrip("\r\n")
    result_head, result_body = send_receive_data(host, abs_path, port, POST, key_value, request_data)

    # if "400" in result_head or "401" in result_head or "403" in result_head or "404" in result_head :
    #     exit()

    output(print_detail, print_in_file, result_head, result_body, file_name)

    decide_redirection(host, result_head, url_index)

    request_list.clear()
    main()


def query_operation():
    file_name = ""
    print_in_file = False
    print_detail = False
    result_head = ""
    result_body = ""
    for index, element in enumerate(request_list):
        if "://" in element:
            host, abs_path, port, query = deal_url(element)
            result_body = query.strip("?")
        if element.lower() == OUTPUT:
            print_in_file = True
            file_name = request_list[index+1]

    output(print_detail, print_in_file, result_head, result_body, file_name)

    request_list.clear()
    main()


def body_operation():
    file_name = ""
    print_in_file = False
    print_detail = False
    result_head = ""
    result_body = ""
    key_value = ""

    scheme_version_header = " HTTP/1.0\r\n"

    for index, element in enumerate(request_list):
        if element.lower() == HEAD:
            key_value = key_value + "\r\n" + request_list[index+1]
        if "://" in element:
            host, abs_path, port, query = deal_url(element)
            result_head = abs_path + scheme_version_header
            result_body = "Host: " + host + ":" + str(port) + "\r\n" + key_value.lstrip("\r\n") + "\r\n"
            print_detail = True
        if element.lower() == OUTPUT:
            print_in_file = True
            file_name = request_list[index+1]

    output(print_detail, print_in_file, result_head, result_body, file_name)

    request_list.clear()
    main()


def header_operation():
    file_name = ""
    print_in_file = False
    print_detail = False
    result_head = ""
    result_body = ""
    for index, element in enumerate(request_list):
        if "://" in element:
            host, abs_path, port, query = deal_url(element)
            result_head = "Host: " + host
            result_body = "Port: " + str(port)
            print_detail = True
        if element.lower() == OUTPUT:
            print_in_file = True
            file_name = request_list[index+1]

    output(print_detail, print_in_file, result_head, result_body, file_name)

    request_list.clear()
    main()


def help_operation():
    if len(request_list) == 2:
        print('httpc is a curl-like application but supports HTTP protocol only.\nUsage:\n    httpc command [arguments]\nThe commands are:\n    get executes a HTTP GET request and prints the response.\n    post executes a HTTP POST request and prints the response.\n    help prints this screen.\n\nUse "httpc help [command]" for more information about a command.')
    elif request_list[2].lower() == GET:
        print('usage: httpc get [-v] [-h key:value] URL\n\nGet executes a HTTP GET request for a given URL.\n\n   -v             Prints the detail of the response such as protocol, status,and headers.\n   -h key:value   Associates headers to HTTP Request with the format\'key:value\'.')
    elif request_list[2].lower() == POST:
        print('usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL\n\nPost executes a HTTP POST request for a given URL with inline data or from file.\n\n   -v            Prints the detail of the response such as protocol, status,and headers.\n   -h key:value  Associates headers to HTTP Request with the format\'key:value\'\n   -d string     Associates an inline data to the body HTTP POST request.\n   -f file       Associates the content of a file to the body HTTP POST request.\n\nEither [-d] or [-f] can be used but not both..')
    request_list.clear()
    return main()


def choose_operation():
    request_operation = request_list[1]
    if request_operation.lower() == GET:
        get_operation()
    elif request_operation.lower() == POST:
        post_operation()
    elif request_operation.lower() == QUERY:
        query_operation()
    elif request_operation.lower() == HEADER:
        header_operation()
    elif request_operation.lower() == BODY:
        body_operation()
    elif request_operation.lower() == HELP:
        help_operation()
    else:
        print("Wrong operation!")
        request_list.clear()
        main()


def my_split(data):
    separator = " "
    left = "{"
    right = "}"

    flag = 0
    data = data.strip(separator)

    separator_index = [0]
    for index, character in enumerate(data):
        if character == left:
            flag += 1
        elif character == right:
            flag -= 1
        elif character == separator and flag == 0:
            separator_index.append(index)

        if flag < 0:
            print("Data syntax error! Input again!")
            return -1

    separator_index.append(len(data))
    # print("len: " + str(len((data))))

    if flag > 0:
        print("Data syntax error! Input again!")
        return -1
    raw_request = [data[i:j].strip(separator) for i, j in zip(separator_index, separator_index[1:])]
    return raw_request


def deal_input():
    global request_list
    global raw
    raw = input()
    if raw == EXIT:
        os._exit(0)
    raw_request = my_split(raw.strip().replace("'", ""))
    while raw_request == -1:
        raw_request.clear()
        raw = input()
        if raw == EXIT:
            os._exit(0)
        raw_request = my_split(raw.strip().replace("'", ""))
    while raw_request[0] != "httpc":
        print("Not start with httpc! Input again!")
        raw_request.clear()
        raw = input()
        if raw == EXIT:
            os._exit(0)
        raw_request = my_split(raw.strip().replace("'", ""))
    request_list = raw_request.copy()
    raw_request.clear()


def get_raw_input():
    return raw


def main():
    deal_input()
    choose_operation()


# main()

