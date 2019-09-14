import socket

GET = "get"
POST = "post"
DETAIL = "-v"
HEAD = "-h"

def send_receive_data(host,request_url):
    # print("host: " + host)
    # print("request_url:" + request_url)
    result_list = {}
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((host, 80))
    request_line = "GET /"+ request_url +" HTTP/1.0\r\n"
    request_data = request_line + "\r\n"
    my_socket.send(request_data.encode('utf-8'))

    data = my_socket.recv(1024)
    data = data.decode('utf-8')
    result_head,result_body = data.split('\r\n\r\n',1)
    result_list[0] = result_head
    result_list[1] = result_body

    my_socket.close()
    return  result_list

def deal_url(url):
    url = url.replace("'http://","")
    url = url.replace("'","")
    url_list = url.split("/")
    return url_list

def get_operation():
    if request_list[2] == DETAIL:
        url_list = deal_url(request_list[3])
        result_list = send_receive_data(url_list[0], url_list[1])

        result_head = result_list[0]
        result_body = result_list[1]

        print(result_head + "\r\n")
        print(result_body)
    elif request_list[2] == HEAD:
        url_list = deal_url(request_list[4])
        result_list = send_receive_data(url_list[0], url_list[1])

        result_head = result_list[0]
        print(result_head + "\r\n")
    else:
        url_list = deal_url(request_list[2])
        result_list = send_receive_data(url_list[0], url_list[1])

        result_body = result_list[1]
        print(result_body)

    # with open('web.html', 'wb') as f:
    #     f.write(result_body.encode('utf-8'))


def post_operation():
    return

def choose_operation():
    request_operation = request_list[1]
    if request_operation == GET:
        get_operation()
    elif request_operation == POST:
        post_operation()
    else:
        print("wrong operation!")


def deal_input():
    global request_list
    raw_request = input().lower().split()
    print("request: " + str(raw_request))
    while raw_request[0] != "httpc":
        print("Shit! Input again!")
        raw_request = input().lower().split()
    request_list = raw_request

def main():
    deal_input()
    choose_operation()
main()

