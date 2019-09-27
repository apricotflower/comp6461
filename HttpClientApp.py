import socket
import urllib.parse
import ssl

GET = "get"
POST = "post"
DETAIL = "-v"
HEAD = "-h"
POST_DATA = "-d"
POST_FILE = "-f"
OUTPUT = "-o"


def send_receive_data(host, abs_path, port, operation, request_content_type, request_data):
    # print("host: " + host)
    # print("abs_url:" + abs_path)
    # print("request_content_type: " + request_content_type)
    # print("request_data: " + request_data)
    # print("**"*20)
    request = ""

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # my_socket.connect((host, 443))
    my_socket.connect((host, port))
    # my_socket = ssl.wrap_socket(my_socket, keyfile=None, certfile = None, server_side = False, cert_reqs = ssl.CERT_NONE,
    #                            ssl_version = ssl.PROTOCOL_SSLv23)
    if operation == GET:
        request_line = "GET /" + abs_path + " HTTP/1.0\r\n" + request_content_type + "\r\n"
        request = request_line + "\r\n"
    elif operation == POST:
        request_content_length = "Content-Length: " + str(len(request_data))
        request = 'POST /' + abs_path + ' HTTP/1.0\r\n' + request_content_type + "\r\n" + request_content_length + "\r\n\r\n" + request_data

    my_socket.send(request.encode('utf-8'))
    # my_socket.send(request.encode('ISO-8859-1'))
    data = ""
    while True:
        # buf_data = my_socket.recv(1024).decode('ISO-8859-1')
        buf_data = my_socket.recv(1024).decode('utf-8')
        data = data + buf_data
        if buf_data == "":
            break
    result_head, result_body = data.split('\r\n\r\n', 1)
    my_socket.close()
    return result_head, result_body


def deal_url(url):
    p_url = urllib.parse.urlparse(url)

    global p_scheme
    p_scheme = p_url.scheme
    # print("k_schedule: " + p_scheme)

    host = p_url.netloc
    # print("k_host: " + host)

    path = p_url.path
    # print("k_path: " + path)

    params = p_url.params
    if params != "":
        params = ";" + params
    # print("k_params: " + params)

    query = p_url.query
    if query != "":
        query = "?" + query
    # print("k_query: " + query)

    fragment = p_url.fragment
    if fragment != "":
        fragment = "#" + fragment
    # print("k_fragment: " + fragment)

    port = p_url.port
    # print("k_port: " + str(port))
    if port is None:
        port = 80

    abs_path = path + params + query + fragment

    return host, abs_path, port


def redirect_analyse_url(host, re_location):
    if "://" in re_location:
        target_url = re_location
    else:
        target_url = p_scheme + "://" + host + re_location
    return target_url


def start_redirect(host, result_head, url_index):
    re_location = ""
    result_head_list = result_head.split("\r\n")
    # print(result_head_list)
    for line in result_head_list:
        if "Location:" in line:
            re_location = line.split(" ")[1].strip()
            # print("re_location: " + re_location)

    if re_location == "":
        print("No new location in response…Redirection fail! ")

    target_url = redirect_analyse_url(host, re_location)
    request_list[url_index] = target_url
    choose_operation()


def decide_redirection(host, result_head, url_index):
    if "302" in result_head.split("\r\n")[0] or "301" in result_head.split("\r\n")[0]:
        print("\r\n" + "**"*80 + "\r\n" + "Start redirect……")
        start_redirect(host, result_head, url_index)


def output(print_detail, print_in_file, result_head, result_body, file_name):
    if print_detail:
        output_content = result_head + "\r\n" + result_body
    else:
        output_content = result_body
    print(output_content)

    if print_in_file:
        with open(file_name, 'wb') as f:
            output_content = output_content + "\r\n\r\n"
            f.write(output_content.encode('utf-8'))


def get_operation():
    print_detail = False
    key_value = ""
    print_in_file = False
    file_name = ""
    url_index = -1

    for index, element in enumerate(request_list):
        if element == DETAIL:
            print_detail = True
        if element == HEAD:
            key_value = request_list[index+1]
        if element == OUTPUT:
            print_in_file = True
            file_name = request_list[index+1]

        if "://" in element:
            host, abs_path, port = deal_url(element)
            url_index = index

    result_head, result_body = send_receive_data(host, abs_path, port, GET, key_value, "")

    output(print_detail, print_in_file, result_head, result_body, file_name)

    decide_redirection(host, result_head, url_index)


def post_operation():
    print_detail = False
    key_value = ""
    print_in_file = False
    file_name = ""
    request_data = ""
    url_index = -1

    for index, element in enumerate(request_list):
        if element == DETAIL:
            print_detail = True
        if element == HEAD:
            key_value = request_list[index+1]
        if element == OUTPUT:
            print_in_file = True
            file_name = request_list[index+1]
        if element == POST_DATA:
            request_data = request_list[index+1]
        if element == POST_FILE:
            f = open(request_list[index+1], 'r')
            request_data = f.read()
        if "://" in element:
            host, abs_path, port = deal_url(element)
            url_index = index

    result_head, result_body = send_receive_data(host, abs_path, port, POST, key_value, request_data)

    output(print_detail, print_in_file, result_head, result_body, file_name)

    decide_redirection(host, result_head, url_index)


def choose_operation():
    request_operation = request_list[1]
    if request_operation == GET:
        get_operation()
    elif request_operation == POST:
        post_operation()
    else:
        print("wrong operation!")


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
    raw_request = my_split(input().strip().replace("'", ""))
    # print("request: " + str(raw_request))
    while raw_request == -1:
        raw_request = my_split(input().strip().replace("'", ""))
        print("request: " + str(raw_request))
    while raw_request[0] != "httpc":
        print("Input again!")
        raw_request = my_split(input().strip().replace("'", ""))
    request_list = raw_request


def main():
    deal_input()
    choose_operation()


main()

