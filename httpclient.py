import socket
from urllib.parse import urlparse

def doGet(url, cmd, headtype, filename = None):
    _url = urlparse(url)
    host = _url.hostname
    port = _url.port
    redirect = 0
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
    request_line = 'GET ' + path + ' HTTP/1.1\r\n'
    request_headers = 'Host: ' + host + ':' + str(port) + '\r\n'
    if headtype.__len__() == 0:
        request_data = request_line + request_headers + '\r\n'
    else:
        head = ''
        for h in headtype:
            head += h
        request_data = request_line + request_headers + head + '\r\n'
        # request_data = request_line + request_headers + 'Connection: Keep-Alive\r\n' + headtype + '; charset=utf-8 \r\n' + '\r\n'
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
    location = ''
    if mes_status.__contains__("301") or mes_status.__contains__("302"):
        redirect = 1
        for mes in rec_mes:
            if 'location' in mes.lower():
                location = mes.split(' ')[1]
    else:
        redirect = 0
    if location.__contains__("http") or location.__contains__("https"):
        pass
    else:
        location = _url.scheme + "://" + _url.netloc + location
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
            if redirect == 1:
                doGet(location, None, headtype, filename)
        elif cmd == "-v":
            print(mes_status + '\r\n'+ mes_header + '\r\n' + mes_body + '\r\n')
            if redirect == 1:
                doGet(location, cmd, headtype, filename)
    else:
        file = open(filename, "a")
        if cmd == 'query':
            wstr =  urlQuery + '\r\n'
            print(wstr)
            file.write(wstr + '\r\n')
        elif cmd == 'header':
            wstr = request_headers + '\r\n'
            print(wstr)
            file.write(wstr + '\r\n')
        elif cmd == 'body':
            wstr = request_data + '\r\n'
            print(wstr)
            file.write(wstr + '\r\n')
        elif cmd == None:
            wstr =  mes_body + '\r\n'
            print(wstr)
            file.write(wstr + '\r\n')
            if redirect == 1:
                doGet(location, None, headtype, filename)
        elif cmd == "-v":
            wstr =  mes_status + '\r\n' + mes_header + '\r\n' + mes_body + '\r\n'
            print(wstr)
            file.write(wstr + '\r\n')
            if redirect == 1:
                doGet(location, cmd, headtype, filename)
        file.close()
    tcp_socket.close()

def doPost(type, url, headtype, attach, filename=None,detail=None):
    if type == '-d':
        inline = attach
    elif type == '-f':
        if attach.__contains__("'"):
            attach = eval(attach)
        with open(attach) as f:
            inline = f.read()
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
    # request_data = request_line + request_headers + 'Connection: Keep-Alive\r\n' + headtype +'\r\n'
    head = ''
    for h in headtype:
        head += h
    request_data = request_line + request_headers + head
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
    location = ''
    if mes_status.__contains__("301") or mes_status.__contains__("302"):
        redirect = 1
        for mes in rec_mes:
            if 'location' in mes.lower():
                location = mes.split(' ')[1]
    else:
        redirect = 0
    if location.__contains__("http") or location.__contains__("https"):
        pass
    elif location != '':
        location = _url.scheme + "://" + _url.netloc + location
    if filename == None:
        if detail == None:
            print(mes_body)
        else:
            print(mes_status + '\r\n'+ mes_header + '\r\n' + mes_body + '\r\n')
        if redirect == 1:
            doPost(type, location, headtype, inline, filename)
    else:
        if(filename.__contains__("'")):
            filename = eval(filename)
        file = open(filename, "a")
        if detail == None:
            wstr = mes_body
        else:
            wstr = mes_status + '\r\n'+ mes_header + '\r\n' + mes_body + '\r\n'
        print(wstr)
        file.write(wstr + '\r\n')
        file.close()
        if redirect == 1:
            doPost(type, location, headtype, inline, filename)
    tcp_socket.close()

# if __name__ == '__main__':
def main(raw_input):
    exit = 0
    while (exit == 0):
        # command = input()
        command = raw_input

        if raw_input != "":
            command = raw_input
            raw_input = ""
        else:
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
                headtype = []
                count = 0
                for gets in command_arr:
                    if '://' in gets:
                        url = gets
                    elif '-' in gets:
                        cmd += gets + " "
                    elif '.txt' in gets:
                        filename = gets
                    if gets == '-h':
                        headtype.append(command_arr[count + 1] + '\r\n')
                    count += 1
                if '-v' not in cmd:
                    if '-o' in cmd:
                        doGet(eval(url), None, headtype, filename)
                        filename = None
                    else:
                        doGet(eval(url),None, headtype)
                else:
                    cmdArr = cmd.split(" ")
                    for cmds in cmdArr:
                        doGet(eval(url), cmds, headtype, filename)
                        filename = None
            elif command_arr[1].lower() == 'query':
                filename = None
                headtype = []
                for gets in command_arr:
                    if '://' in gets:
                        url = gets
                    elif '.txt' in gets:
                        filename = gets
                cmd = 'query'
                doGet(eval(url), cmd, headtype, filename)
                filename = None
            elif command_arr[1].lower() == 'header':
                filename = None
                headtype = []
                for gets in command_arr:
                    if '://' in gets:
                        url = gets
                    elif '.txt' in gets:
                        filename = gets
                cmd = 'header'
                doGet(eval(url), cmd, headtype, filename)
                filename = None
            elif command_arr[1].lower() == 'body':
                filename = None
                headtype = []
                for gets in command_arr:
                    if '://' in gets:
                        url = gets
                    if gets == '-h':
                        headtype.append(command_arr[command_arr.index(gets) + 1])
                    elif '.txt' in gets:
                        filename = gets
                cmd = 'body'
                doGet(eval(url), cmd, headtype, filename)
                filename = None
            elif command_arr[1].lower() == 'post':
                filename = None
                for posts in command_arr:
                    if '://' in posts:
                        url = posts
                        if url.__contains__("'"):
                            url = eval(url)
                headtype = []
                inline = ''
                type = ''
                for index, value in enumerate(command_arr):
                    if value == '-h':
                        headtype.append(command_arr[index + 1] + '\r\n')
                    elif value == '-o':
                        filename = command_arr[index + 1]
                    elif value == '-d' or value == '--d':
                        type = '-d'
                        start = command.find('{')
                        fin = command.find('}') + 1
                        inline = command[start:fin]
                    elif value == '-f' or value == '--f':
                        type = '-f'
                        inline = command_arr[index + 1]
                    elif value == '-v':
                        detail = 1
                doPost(type, url, headtype, inline, filename, detail)
                detail = None
                filename = None
            else:
                print()
        else:
            print()

# main("")
# httpc get 'http://httpbin.org/get?course=networking&assignment=1'
# httpc get -v -h Content-Type:application/json 'http://httpbin.org/get?course=networking&assignment=1'
# httpc get -v -h Content-Type:application/json -h Accept-Language:en -h Accept-Ranges:bytes 'http://httpbin.org/get?course=networking&assignment=1'
# httpc post -h Content-Type:application/json -h Accept-Language:en -d '{"Assignment": 1}' 'http://httpbin.org/post'
# httpc query 'http://httpbin.org/get?course=networking&assignment=1' -o 'hello.txt'
# httpc header 'http://httpbin.org/get?course=networking&assignment=1' -o 'hello.txt'
# httpc body 'http://httpbin.org/get?course=networking&assignment=1' -o 'hello.txt'
# httpc post -h Content-Type:application/json -d '{"Assignment": 1}' 'http://httpbin.org/post'
# httpc post -h Content-Type:application/json -f 'data.txt' 'http://httpbin.org/post'
# httpc get -v 'http://httpbin.org/status/302'
# httpc post -h Content-Type:application/json -d '{"123": 123}' 'http://http://localhost/HW5_ajax/Login.php'