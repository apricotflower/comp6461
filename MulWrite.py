import threading
import httpclient


def write(i, raw_request):
    print("Client " + str(i) + " is writing!")
    httpclient.main(raw_request)


if __name__ == '__main__':
    threads = []
    i = 1
    thread_1 = threading.Thread(target=write, args=(str(i), "httpc post -v -h overwrite=true -d '{This_is_a_modification 1}' 'http://localhost:8080/a.txt'"))
    thread_1.start()
    threads.append(thread_1)

    i = i + 1
    thread_2 = threading.Thread(target = write, args=(str(i), "httpc post -v -h overwrite=true -d '{This_is_a_modification 2}' 'http://localhost:8080/a.txt'"))
    thread_2.start()
    threads.append(thread_2)

    i = i + 1
    thread_3 = threading.Thread(target=write, args=(str(i), "httpc post -v -h overwrite=true -d '{This_is_a_modification 3}' 'http://localhost:8080/a.txt'"))
    thread_3.start()
    threads.append(thread_3)

    i = i + 1
    thread_4 = threading.Thread(target=write, args=(str(i), "httpc post -v -h overwrite=true -d '{This_is_a_modification 4}' 'http://localhost:8080/a.txt'"))
    thread_4.start()
    threads.append(thread_4)

    i = i + 1
    thread_5 = threading.Thread(target=write, args=(str(i), "httpc post -v -h overwrite=true -d '{This_is_a_modification 5}' 'http://localhost:8080/a.txt'"))
    thread_5.start()
    threads.append(thread_5)

    for t in threads:
        t.join()
    print("All write clients finish!")