import socket
import json


GET = "get"
POST = "post"
DETAIL = "-v"
HEAD = "-h"
POST_DATA = "-d"
POST_FILE = "-f"
OUTPUT = "-o"


def send_receive_data(host, request_url, operation, request_content_type, request_data):
    print("host: " + host)
    print("request_url:" + request_url)
    print("request_content_type: " + request_content_type)
    print("request_data: " + request_data)
    print("**"*20)
    request = ""
    result_list = {}
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((host, 80))
    if operation == GET:
        request_line = "GET /"+ request_url + " HTTP/1.0\r\n"
        request = request_line + "\r\n"
    elif operation == POST:
        # host = "httpbin.org"
        # request_url = "post"
        # request_content_type = "Content-Type: application/json\r\n"
        # request_content_length = "Content-Length: 47\r\n\r\n"
        # request_data = '{"capabilities": {}, "desiredCapabilities": {}}'

        request_content_length = "Content-Length: " + str(len(request_data))
        request = 'POST /' + request_url + ' HTTP/1.0\r\n' + request_content_type + "\r\n" + request_content_length + "\r\n\r\n" + request_data

    my_socket.send(request.encode('utf-8'))

    data = my_socket.recv(10240)
    data = data.decode('utf-8')
    result_head, result_body = data.split('\r\n\r\n', 1)
    result_list[0] = result_head
    result_list[1] = result_body

    my_socket.close()
    return result_list


def deal_url(url):
    url = url.replace("http://", "")
    url = url.replace("https://", "")
    url_list = url.split("/")
    if len(url_list) == 1:
        url_list.append("")
    return url_list


def get_operation():
    result_head = ""
    result_body = ""

    if request_list[2] == DETAIL:
        url_list = deal_url(request_list[3])
        result_list = send_receive_data(url_list[0], url_list[1], GET, "", "")

        result_head = result_list[0]
        result_body = result_list[1]

        print(result_head + "\r\n")
        print(result_body)
    elif request_list[2] == HEAD:
        url_list = deal_url(request_list[4])
        result_list = send_receive_data(url_list[0], url_list[1], GET, "", "")

        result_head = result_list[0]
        print(result_head + "\r\n")
    else:
        url_list = deal_url(request_list[2])
        result_list = send_receive_data(url_list[0], url_list[1], GET, "", "")

        result_body = result_list[1]
        print(result_body)

    # print(result_head + "\r\n")
    # print(result_body)


    if request_list[-2] == OUTPUT:
        with open(request_list[-1], 'wb') as f:
            o = result_head + "\r\n" + result_body
            f.write(o.encode('utf-8'))


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
    result_head = ""
    result_body = ""

    if request_list[2] == DETAIL:
        url_list = deal_url(request_list[7])
        if request_list[5] == POST_DATA:
            result_list = send_receive_data(url_list[0], url_list[1], POST, request_list[4],
                                            request_list[6])
        elif request_list[5] == POST_FILE:
            result_list = send_receive_data(url_list[0], url_list[1], POST, request_list[4],
                                            request_list[6])
        result_head = result_list[0]
        result_body = result_list[1]

        print(result_head + "\r\n")
        print(result_body)

    elif request_list[2] == HEAD:
        url_list = deal_url(request_list[6])
        if request_list[4] == POST_DATA:
            result_list = send_receive_data(url_list[0], url_list[1], POST, request_list[3],request_list[5])
        elif request_list[4] == POST_FILE:
            result_list = send_receive_data(url_list[0], url_list[1], POST, request_list[3],
                                            request_list[5])
        result_body = result_list[1]
        print(result_body)

    if request_list[-2] == OUTPUT:
        with open(request_list[-1], 'wb') as f:
            o = result_head + "\r\n" + result_body
            f.write(o.encode('utf-8'))


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
        # print("separator_index: " + str(separator_index))
        # print("character:" + character)
        # print("index: " + str(index))
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
    # raw_request.append("")
    # raw_request.append("")
    return raw_request


def deal_input():
    global request_list
    raw_request = my_split(input().replace("'", ""))
    print("request: " + str(raw_request))
    while raw_request == -1:
        raw_request = my_split(input().replace("'", ""))
        print("request: " + str(raw_request))
    while raw_request[0] != "httpc":
        print("Input again!")
        raw_request = my_split(input().replace("'", ""))
    request_list = raw_request


def main():
    deal_input()
    choose_operation()
    # test_post()


main()

