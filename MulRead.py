import threading
import httpclient


def read(i, raw_request):
    print("Client " + str(i) + " is reading!")
    httpclient.main(raw_request)


if __name__ == '__main__':
    threads = []
    for i in range(1, 6):
        thread = threading.Thread(target=read, args=(str(i),"httpc get -v 'http://localhost:8080/a.txt'"))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join(2)
    print("All read clients finish!")

