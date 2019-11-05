import threading
import httpclient


def read(i, raw_request):
    print("Client " + str(i) + " is reading!")
    httpclient.main(raw_request)


def write(i, raw_request):
    print("Client " + str(i) + " is writing!")
    httpclient.main(raw_request)


if __name__ == '__main__':
    for i in range(1, 6):
        if i == 1 or i == 3 or i == 5:
            thread = threading.Thread(target=write, args=(str(i), "httpc post -v -h overwrite=false -d '{This_is_a_modification "+ str(i) + " }' 'http://localhost:8080/a.txt'"))
        else:
            thread = threading.Thread(target=read, args=(str(i), "httpc get -v 'http://localhost:8080/a.txt'"))
        thread.start()
        thread.join(0.1)