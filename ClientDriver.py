import httpclient
import HttpClientApp


def main():
    try:
        HttpClientApp.main()
    except BaseException:
        # print("1 fail")
        raw_input = HttpClientApp.get_raw_input()
        # print("input: " + raw_input)
        httpclient.main(raw_input)
        # print("2 ok")
    # else:
        # print("1 ok")


main()
