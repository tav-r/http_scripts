import requests
import argparse

with open("hop-by-hop-headers.txt") as f:
    HEADERS = list(f.read().split("\n"))

def main(url: str, cookies: dict[str, str]={}, headers: dict[str, str]={}):
    ref_len = len(requests.get(url, headers=headers, cookies=cookies).content)

    print(rec_enum_headers(url, HEADERS, ref_len, headers, cookies))

def rec_enum_headers(url: str, hop_by_hop_headers: list[str], ref_len: int, headers: dict[str, str], cookies: dict[str, str]) -> list[str]:
    response = requests.get(url, headers=headers | {"connection": "close, " + ", ".join(hop_by_hop_headers)}, cookies=cookies)

    if len(hop_by_hop_headers) == 1:
        return hop_by_hop_headers

    hdrs: list[str] = []

    if response.status_code != 200 or len(response.content) != ref_len:
        hop_by_hop_headers1 = hop_by_hop_headers[:len(hop_by_hop_headers) // 2]
        hdrs += rec_enum_headers(url, hop_by_hop_headers1, ref_len, headers, cookies)

        hop_by_hop_headers2 = hop_by_hop_headers[len(hop_by_hop_headers) // 2:]
        hdrs += rec_enum_headers(url, hop_by_hop_headers2, ref_len, headers, cookies)

    return hdrs


if __name__ == "__main__":
    from sys import argv

    url = argv[1]

    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument("-H", "--headers", help="Headers to be sent with the request")
    argument_parser.add_argument("-j", "--cookies", help="Cookies to send with the request")
    argument_parser.add_argument("url", help="URL to send the request to")

    args = argument_parser.parse_args()

    if args.headers:
        hdrs = dict(h.split(":") for h in args.headers.split(","))
    else:
        hdrs = {}

    if args.cookies:
        cookies = dict(h.split(":") for h in args.cookies.split(","))
    else:
        cookies = {}

    main(args.url, cookies=cookies, headers=hdrs)