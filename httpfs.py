import socket
import threading
import os

def run_server(debug, port, folder):
    host = ''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if folder == '/':
        current_path = os.path.abspath(__file__)
        folder_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
    else:
            if os.path.isdir(folder):
                folder_path = folder
            else:
                print(folder + ' is not exist!')
                return False
    try:
        sock.bind((host, int(port)))
        sock.listen(100)
        print('Server is listening at localhost ' + str(port) + ' port...')
        print('The current working directory is: ' + folder_path + '\r\n')
        while True:
            conn, addr = sock.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr, folder_path))
            t.start()
    finally:
        sock.close()


def handle_client(conn, addr, folder_path):
    print("New client from ", addr)
    try:
        request = str(conn.recv(1024), encoding="utf8")
        request_arr = request.split(" ")
        if request_arr[0] == 'GET':
            response = handle_get(request_arr, folder_path)
            response = bytes(response, encoding="utf8")
            print(response)
            conn.sendall(response)
        elif request_arr[0] == 'POST':
            response = handle_post(request_arr, folder_path)
            response = bytes(response, encoding="utf8")
            print(response)
            conn.sendall(response)
    except:
        print("Internal Server Error.")
        conn.sendall(bytes("HTTP/1.0 500 Internal Server Error\r\n\r\n", encoding="utf8"))
    finally:
        conn.close()
    print()


def handle_get(request_arr, folder_path):
    print(request_arr)
    path = request_arr[1]
    # default text/plain
    header_type = 'text/plain'
    for s in request_arr:
        if s.__contains__('localhost'):
            if s.__contains__('Content-Type'):
                sAll = s.split("\r\n")
                for type in sAll:
                    if type.__contains__('Content-Type'):
                        header_type = type[type.index(":") + 1:]
    if os.path.isdir(folder_path + path):
        files = os.listdir(folder_path + path)
        body = ' '.join(files)
        body = listdir_nohidden(body)
        format_body = body_format(body, header_type, folder_path + path)
        cl = format_body.__len__()
        response = 'HTTP/1.0 200 OK\r\n' + 'Content-Type: ' + header_type + '\r\n' + 'Content-Length: ' + str(cl) + '\r\n\r\n' + format_body
    elif os.path.isfile(folder_path + path):
        filename = folder_path + path
        f = open(filename)
        data = f.readlines()
        body = ''
        for s in data:
            body += s
        cl = body.__len__()
        response = 'HTTP/1.0 200 OK\r\n' + 'Content-Length: ' + str(cl) + '\r\n\r\n' + body
    else:
        response = 'HTTP/1.0 404 NOT FOUND\r\n\r\n' + path + ' is not exist!'
    return response

def listdir_nohidden(body):
    elements = body.split(' ')
    for f in elements:
        if f.startswith('.'):
            elements.remove(f)
    body = ' '.join(elements)
    return body

def body_format(body, header_type, root_path):
    print(root_path)
    print(body)
    elements = body.split(" ")
    if elements.__contains__(''):
        elements.remove('')
    if header_type.__eq__("application/json"):
        print(header_type)
        response = ''
        if len(elements) == 0:
            response += '{\r\n "DirectoryInfo":\r\n {\r\n  ' + '\r\n }\r\n}'
            return response
        for e in elements:
            if len(elements) == 1:
                response += '{\r\n "DirectoryInfo":\r\n {\r\n  ' + element_format(e, 'json', root_path) + '\r\n }\r\n}'
                return response
            else:
                if elements.index(e) == 0:
                    response += '{\r\n "DirectoryInfo":\r\n {\r\n  ' + element_format(e, 'json', root_path) + ',\r\n'
                elif elements.index(e) == len(elements) - 1:
                    response += '  ' + element_format(e, 'json', root_path) + '\r\n }\r\n}'
                else:
                    response += '  ' + element_format(e, 'json', root_path) + ',\r\n'
        return response
    elif header_type.__eq__("text/xml"):
        print(header_type)
        response = '<?xml version="1.0" ?>\r\n'
        if len(elements) == 0:
            response += '<DirectoryInfo>\r\n\r\n</DirectoryInfo>'
            return response
        for e in elements:
            if len(elements) == 1:
                response += '<DirectoryInfo>\r\n  ' + element_format(e, 'xml', root_path) + '\r\n</DirectoryInfo>'
                return response
            else:
                if elements.index(e) == 0:
                    response += '<DirectoryInfo>\r\n  ' + element_format(e, 'xml', root_path) + ',\r\n'
                elif elements.index(e) == len(elements) - 1:
                    response += '  ' + element_format(e, 'xml', root_path) + '\r\n</DirectoryInfo>'
                else:
                    response += '  ' + element_format(e, 'xml', root_path) + '\r\n'
        return response
    elif header_type.__eq__("text/html"):
        print(header_type)
        response = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\r\n'
        if len(elements) == 0:
            response += '<html>\r\n<head>\r\n   <title>200 OK</title>\r\n</head>\r\n<body>\r\n\r\n</body>\r\n</html>'
            return response
        for e in elements:
            if len(elements) == 1:
                response += '<html>\r\n<head>\r\n   <title>200 OK</title>\r\n</head>\r\n<body>\r\n   ' + element_format(e, 'html', root_path) + '\r\n</body>\r\n</html>'
                return response
            else:
                if elements.index(e) == 0:
                    response += '<html>\r\n<head>\r\n   <title>200 OK</title>\r\n</head>\r\n<body>\r\n   ' + element_format(e, 'html', root_path) + '\r\n\r\n'
                elif elements.index(e) == len(elements) - 1:
                    response += '   ' + element_format(e, 'html', root_path) + '\r\n</body>\r\n</html>'
                else:
                    response += '   ' + element_format(e, 'html', root_path) + '\r\n\r\n'
        return response
    elif header_type.__eq__("text/plain"):
        print(header_type)
        return body

def element_format(e, type, root_path):
    if root_path[-1] != '/':
        path = root_path + '/' + e
    else:
        path = root_path + e
    if type == 'json':
        if os.path.isdir(path):
            r = '{\r\n   "Type": "Directory"\r\n   "DirectoryName": "' + e + '"\r\n   '+'"Path": "' + path + '"\r\n  }'
            return r
        elif os.path.isfile(path):
            r = '{\r\n   "Type": "File"\r\n   "FileName": "' + e + '"\r\n   ' + '"Path": "' + path + '"\r\n  }'
            return r
    elif type == 'xml':
        if os.path.isdir(path):
            r = '<Directory>\r\n    <Type>Directory</Type>\r\n    <Name>' + e + '</Name>\r\n    '+'<Path>' + path + '</Path>\r\n  </Directory>'
            return r
        elif os.path.isfile(path):
            r = '<File>\r\n    <Type>File</Type>\r\n    <Name>' + e + '</Name>\r\n    ' + '<Path>' + path + '</Path>\r\n  </File>'
            return r
    elif type == 'html':
        if os.path.isdir(path):
            r = '<p>Type: Directory</p>\r\n   <p>Name: ' + e + '</p>\r\n   ' + '<p>Path: ' + path + '</p>'
            return r
        elif os.path.isfile(path):
            r = '<p>Type: File</p>\r\n   <p>Name: ' + e + '</p>\r\n   ' + '<p>Path: ' + path + '</p>'
            return r

def handle_post(request_arr, folder_path):
    print(request_arr)
    path = request_arr[1]
    # default overwrite=false
    overwrite = 'false'
    if path.__contains__('&'):
        path = path[:path.index('&')]
    for s in request_arr:
        if s.__contains__('overwrite'):
            overwrite_text = s[s.index('=') + 1:]
            if overwrite_text.__contains__('true'):
                overwrite = 'true'
    print(overwrite)
    file_path = folder_path + path
    print(file_path)
    content = request_arr[len(request_arr) - 2] + request_arr[len(request_arr) - 1]
    content = content.split("\r\n\r\n")[1]
    if content[0].__eq__('"') | content[0].__eq__("'"):
        content = eval(content)
    print(content)
    if os.path.isfile(file_path):
        if overwrite == 'true':
            try:
                f = open(file_path,"w")
                f.write(content)
                f.close()
            except:
                print("Errors in the file operation.")
            body =file_path + '\r\nYou successfully overwrite it.\r\n' + content
        else:
            body = 'This file is already exist.\r\nIf you want to overwrite it.\r\nYou can add overwrite=true option.'
    else:
        try:
            f = open(file_path, "w")
            f.write(content)
            f.close()
        except:
            print("Errors in the file operation.")
        body = file_path + '\r\nThis file is successfully built.\r\n' + content
    cl = body.__len__()
    response = 'HTTP/1.0 200 OK\r\n' + 'Content-Length: ' + str(cl) + '\r\n\r\n' + body
    return response

if __name__ == '__main__':
    while True:
        command = input()
        command_arr = command.split(' ')
        debug = 0
        port = 8080
        directory = '/'
        if command_arr[0].lower() == 'httpfs':
            if command_arr.__len__() == 1:
                print('usage: httpfs [-v] [-p PORT] [-d PATH-TO-DIR] \r\n')
                print('     -v   Prints debugging messages.')
                print('     -p   Specifies the port number that the server will listen '
                      'and serve at. Default is 8080.')
                print('     -d   Specifies the directory that the server will use to read/write '
                      'requested files. Default is the current directory when launching the application.')
            else:
                for s in command_arr[1:]:
                    if s == '-v':
                        debug = 1
                    if s == '-p':
                        port = command_arr[command_arr.index(s) + 1]
                    if s == '-d':
                        directory = command_arr[command_arr.index(s) + 1]
                if run_server(debug, port, directory) == False:
                    continue
# httpfs -v
# httpfs -v -p 8081 -d /Users/wangjiahui/Python

# httpc get -v 'http://localhost:8080'
# httpc get -v 'http://localhost:8080/testfolder'
# httpc get -v 'http://localhost:8080/a.txt'
# httpc get -v -h Content-Type:text/plain 'http://localhost:8080/testfolder'
# httpc get -v -h Content-Type:application/json 'http://localhost:8080'
# httpc get -v -h Content-Type:text/xml 'http://localhost:8080'
# httpc get -v -h Content-Type:text/html 'http://localhost:8080'
# httpc post -v -d 'This_is_a_modification' 'http://localhost:8080/a.txt'
# httpc post -v -d 'This_is_a_modification' -h overwrite=true 'http://localhost:8080/a.txt'
# httpc post -v -d 'This_is_a_modification' 'http://localhost:8080/a.txt&overwrite=true'
# httpc post -v -f 'data.txt' 'http://localhost:8080/c.txt'