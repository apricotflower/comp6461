import httpclient
import HttpClientApp


def main():
    try:
        HttpClientApp.main()
    except BaseException:
        print("1 fail")
        input = HttpClientApp.get_raw_input()
        print("input: " + input)
        httpclient.main()
        print("2 ok")
    else:
        print("1 ok")


main()
