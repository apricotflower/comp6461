import socket
from urllib.parse import urlparse
import ssl

GET = "get"
POST = "post"
DETAIL = "-v"
HEAD = "-h"
POST_DATA = "-d"
POST_FILE = "-f"
OUTPUT = "-o"


def send_receive_data(host, path, query, port, operation, request_content_type, request_data):
    if path == "" and query == "":
        request_url = ""
    elif query == "":
        request_url = path
    else:
        request_url = path + "?" +query
    print("host: " + host)
    print("request_url:" + request_url)
    print("request_content_type: " + request_content_type)
    print("request_data: " + request_data)
    print("**"*20)
    request = ""

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # my_socket.connect((host, 443))
    my_socket.connect((host, port))
    # my_socket = ssl.wrap_socket(my_socket, keyfile=None, certfile = None, server_side = False, cert_reqs = ssl.CERT_NONE,
    #                            ssl_version = ssl.PROTOCOL_SSLv23)
    if operation == GET:
        request_line = "GET /" + request_url + " HTTP/1.0\r\n" + request_content_type + "\r\n"
        request = request_line + "\r\n"
    elif operation == POST:
        request_content_length = "Content-Length: " + str(len(request_data))
        request = 'POST /' + request_url + ' HTTP/1.0\r\n' + request_content_type + "\r\n" + request_content_length + "\r\n\r\n" + request_data

    my_socket.send(request.encode('utf-8'))
    # my_socket.send(request.encode('ISO-8859-1'))

    data = my_socket.recv(1024000)
    # print(data.decode('ISO-8859-1'))
    # result_head, result_body = data.decode('ISO-8859-1').split('\r\n\r\n', 1)
    result_head, result_body = data.decode('utf-8').split('\r\n\r\n', 1)
    my_socket.close()
    return result_head, result_body


def deal_url(url):
    p_url = urlparse(url)
    host = p_url.hostname
    # print("k_host: " + host)
    port = p_url.port
    print("k_port: " + str(port))
    query = p_url.query
    print("k_query: " + query)
    path = p_url.path
    print("k_path: " + path)
    global p_scheme
    p_scheme = p_url.scheme
    print("k_schedule: " + p_scheme)

    if port is None:
        port = 80

    return host, path, query, port


def analyse_url(host, re_location):
    if "://" in re_location:
        target_url = re_location
    else:
        target_url = p_scheme + "://" + host + re_location
    return target_url


def start_redirect(host, result_head, url_index):
    re_location = ""
    result_head_list = result_head.split("\r\n")
    print(result_head_list)
    for line in result_head_list:
        if "Location:" in line:
            re_location = line.split(" ")[1].strip()
            print("re_location: " + re_location)

    if re_location == "":
        print("No new locaion in response…Redirection fail! ")

    target_url = analyse_url(host, re_location)
    request_list[url_index] = target_url
    choose_operation()


def get_operation():
    print_detail = False
    key_value = ""
    print_in_file = False
    file_name = ""
    # host, path, query, port = ""
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
            host, path, query, port = deal_url(element)
            url_index = index

    result_head, result_body = send_receive_data(host, path, query, port, GET, key_value, "")

    if print_detail:
        output_content = result_head + "\r\n" + result_body
    else:
        output_content = result_body
    print(output_content)

    if print_in_file:
        with open(file_name, 'wb') as f:
            f.write(output_content.encode('utf-8'))

    if "302" in result_head.split("\r\n")[0]:
        print("\r\n" + "Start redirect……")
        start_redirect(host, result_head, url_index)


# def test_post():
#     host = "httpbin.org"
#     request_url = "post"
#     request_content_type = "Content-Type: application/json\r\n"
#     # request_d = '{"capabilities": {}, "desiredCapabilities": {}}'
#     request_d = '{"Assignment": 1}'
#     request_content_length = "Content-Length: "+ str(len(request_d)) +"\r\n\r\n"
#     print(len(request_d))
#     request_data = 'POST /' + request_url + ' HTTP/1.0\r\n' + request_content_type + request_content_length + request_d
#     # print(request_data)
#     s = socket.socket(
#         socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((host, 80))
#     s.send(request_data.encode('utf-8'))
#     response = s.recv(10240)
#     data = response.decode('utf-8')
#     result_head, result_body = data.split('\r\n\r\n', 1)
#     print(result_head)
#     print(result_body)


def post_operation():
    print_detail = False
    key_value = ""
    print_in_file = False
    file_name = ""
    request_data = ""
    # host, path, query, port = ""

    for index, element in enumerate(request_list):
        if element == DETAIL:
            print_detail = True
        if element == HEAD:
            print_head = True
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
            host, path, query, port = deal_url(element)

    result_head, result_body = send_receive_data(host, path, query, port, POST, key_value, request_data)

    if print_detail:
        output_content = result_head + "\r\n" + result_body
    else:
        output_content = result_body
    print(output_content)

    if print_in_file:
        with open(file_name, 'wb') as f:
            f.write(output_content.encode('utf-8'))


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
    print("request: " + str(raw_request))
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

