import socket
from urllib.parse import urlparse
import ssl

def doGet(url, cmd, filename = None):
    _url = urlparse(url)
    host = _url.hostname
    port = _url.port
    if port == None:
        port = 80
    urlQuery = _url.query
    path = _url.path
    if path == "":
        path = '/'
    if urlQuery != "":
        path += "?" + urlQuery
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((host, port))

    # tcp_socket = ssl.wrap_socket(tcp_socket, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE,
    #                             ssl_version=ssl.PROTOCOL_SSLv23)

    request_line = 'GET ' + path + ' HTTP/1.1\r\n'
    #header is as a option in command
    request_headers = 'Host: ' + host + ':' + str(port) + '\r\n'
    request_data = request_line + request_headers + 'Connection: Keep-Alive\r\n' + 'Content-Type: application/x-www-form-urlencoded; charset=utf-8 \r\n' + '\r\n'
    msg = bytes(request_data, encoding = "utf8")
    tcp_socket.send(msg)
    rec = str(tcp_socket.recv(5000), encoding= "utf8")
    rec_mes = rec.splitlines()
    if rec_mes.__len__ != None:
        mes_status = rec_mes[0]
    count = 0
    for s in rec_mes:
        count += 1
        if s == '':
            break
    mes_header = '\n'.join(rec_mes[1:count - 1])
    mes_body = '\n'.join(rec_mes[count:])
    if filename != None and filename.__contains__("'"):
        filename = eval(filename)
    if filename == None:
        if cmd == 'query':
            print(urlQuery + '\r\n')
        elif cmd == 'header':
            print(request_headers + '\r\n')
        elif cmd == 'body':
            print(request_data + '\r\n')
        elif cmd == None:
            print(mes_body + '\r\n')
        elif cmd == "-v":
            print(mes_status + '\r\n'+ mes_header + '\r\n' + mes_body + '\r\n')
        elif cmd == '-h':
            print('-h')
    else:
        file = open(filename, "a")
        if cmd == 'query':
            wstr =  urlQuery + '\r\n'
            file.write(wstr)
        elif cmd == 'header':
            wstr = request_headers + '\r\n'
            file.write(wstr)
        elif cmd == 'body':
            wstr = request_data + '\r\n'
            file.write(wstr)
        elif cmd == None:
            wstr =  mes_body + '\r\n'
            file.write(wstr)
        elif cmd == "-v":
            wstr =  mes_status + '\r\n' + mes_header + '\r\n' + mes_body + '\r\n'
            file.write(wstr)
        file.close()
    tcp_socket.close()


def doPost(type, url, headtype, attach, filename=None):
    if type == '-d':
        inline = attach
        _url = urlparse(url)
        host = _url.hostname
        port = _url.port
        if port == None:
            port = 80
        path = _url.path
        if path == "":
            path = '/'
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((host, port))
        request_line = 'POST ' + path + ' HTTP/1.1\r\n'
        request_headers = 'Host: ' + host + ':' + str(port) + '\r\n'
        request_data = request_line + request_headers + 'Connection: Keep-Alive\r\n' + headtype +'; charset=utf-8 \r\n'
        contentLength = 'Content-Length: ' + str(len(inline)) + '\r\n'
        # there is a blank in front of data request is the whole request message of json
        request = request_data + contentLength + '\r\n' + inline
        msg = bytes(request, encoding="utf8")
        tcp_socket.send(msg)
        rec = str(tcp_socket.recv(5000), encoding = "utf-8")
        rec_mes = rec.splitlines()
        if rec_mes.__len__ != None:
            mes_status = rec_mes[0]
        count = 0
        for s in rec_mes:
            count += 1
            if s == '':
                break
        mes_header = '\n'.join(rec_mes[1:count - 1])
        mes_body = '\n'.join(rec_mes[count:])
        if filename == None:
            print(mes_body)
        else:
            file = open(filename, "a")
            wstr = mes_body
            file.write(wstr + '\r\n')
            file.close()
        tcp_socket.close()
    elif type == '-f':
        pass
    else:
        print('Bad instruction try again')


def doRedirect(url):
    _url = urlparse(url)
    host = _url.hostname
    port = _url.port
    if port == None:
        port = 80
    urlQuery = _url.query
    path = _url.path
    if path == "":
        path = '/'
    if urlQuery != "":
        path += "?" + urlQuery
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((host, port))
    request_line = 'HEAD ' + path + ' HTTP/1.1\r\n'
    request_headers = 'Host: ' + host + ':' + str(port) + '\r\n'
    request_data = request_line + request_headers + 'Connection: Keep-Alive\r\n' + 'Content-Type: application/x-www-form-urlencoded; charset=utf-8 \r\n' + '\r\n'
    msg = bytes(request_data, encoding = "utf8")
    tcp_socket.send(msg)
    rec = str(tcp_socket.recv(5000), encoding = "utf-8")
    rec_mes = rec.splitlines()
    mes_status = ''
    location = ''
    if rec_mes.__len__ != None:
        mes_status = rec_mes[0]
    if '302' in mes_status or '301' in mes_status:
        for mes in rec_mes:
            if 'Location' in mes:
                location = mes.split(' ')[1]
    doGet(location, "-v")
    tcp_socket.close()


if __name__ == '__main__':
    exit = 0
    while(exit == 0):
        command = input()
        if command == 'exit':
            exit = 1
        command_arr = command.split(' ')
        if command_arr[0].lower() == 'httpc':
            if command_arr.__len__() == 1:
                print('Bad instruction try again')
            elif command_arr[1].lower() == 'help':
                if command_arr.__len__() == 2:
                    print('httpc is a curl-like application but supports HTTP protocol only.\nUsage:\n    httpc command [arguments]\nThe commands are:\n    get executes a HTTP GET request and prints the response.\n    post executes a HTTP POST request and prints the response.\n    help prints this screen.\n\nUse "httpc help [command]" for more information about a command.')
                else:
                    if command_arr[2].lower() == 'get':
                        print('usage: httpc get [-v] [-h key:value] URL\n\nGet executes a HTTP GET request for a given URL.\n\n   -v             Prints the detail of the response such as protocol, status,and headers.\n   -h key:value   Associates headers to HTTP Request with the format\'key:value\'.')
                    elif command_arr[2].lower() == 'post':
                        print('usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL\n\nPost executes a HTTP POST request for a given URL with inline data or from file.\n\n   -v            Prints the detail of the response such as protocol, status,and headers.\n   -h key:value  Associates headers to HTTP Request with the format\'key:value\'\n   -d string     Associates an inline data to the body HTTP POST request.\n   -f file       Associates the content of a file to the body HTTP POST request.\n\nEither [-d] or [-f] can be used but not both..')
                    else:
                        print('Bad instruction try again')
            elif command_arr[1].lower() == 'get':
                cmd = ''
                filename = None
                url = ''
                for gets in command_arr:
                    if '://' in gets:
                        url = gets
                    elif '-' in gets:
                        cmd += gets + " "
                    elif '.txt' in gets:
                        filename = gets
                if '-v' not in cmd:
                    if '-o' in cmd:
                        doGet(eval(url), None, filename)
                        filename = None
                    else:
                        doGet(eval(url), None)
                else:
                    cmdArr = cmd.split(" ")
                    for cmds in cmdArr:
                        doGet(eval(url), cmds, filename)
                        filename = None
            elif command_arr[1].lower() == 'query':
                filename = None
                for gets in command_arr:
                    if '://' in gets:
                        url = gets
                    elif '.txt' in gets:
                        filename = gets
                cmd = 'query'
                doGet(eval(url), cmd, filename)
                filename = None
            elif command_arr[1].lower() == 'header':
                filename = None
                for gets in command_arr:
                    if '://' in gets:
                        url = gets
                    elif '.txt' in gets:
                        filename = gets
                cmd = 'header'
                doGet(eval(url), cmd, filename)
                filename = None
            elif command_arr[1].lower() == 'body':
                filename = None
                for gets in command_arr:
                    if '://' in gets:
                        url = gets
                    elif '.txt' in gets:
                        filename = gets
                cmd = 'body'
                doGet(eval(url), cmd, filename)
                filename = None
            elif command_arr[1].lower() == 'post':
                filename = None
                for posts in command_arr:
                    if '://' in posts:
                        url = posts
                        if url.__contains__("'"):
                            url = eval(url)
                    if '.txt' in posts:
                        filename = posts
                headtype = ''
                inline = ''
                for index, value in enumerate(command_arr):
                    if value == '-h':
                        headtype = command_arr[index + 1]
                    elif value == '-d' or value == '--d':
                        type = '-d'
                        start = command.find('{')
                        fin = command.find('}') + 1
                        inline = command[start:fin]
                        doPost(type, url, headtype, inline, filename)
                        filename = None
                    elif value == '-f' or value == '--f':
                        pass
            elif command_arr[1].lower() == 'redirect':
                for redirects in command_arr:
                    if '://' in redirects:
                        url = redirects
                        if url.__contains__("'"):
                            url = eval(url)
                doRedirect(url)
            else:
                print('Bad instruction try again')
        else:
            print('Bad instruction try again')

# httpc get 'http://httpbin.org/get?course=networking&assignment=1'
# httpc post -h Content-Type:application/json --d '{"Assignment": 1}' http://httpbin.org/post