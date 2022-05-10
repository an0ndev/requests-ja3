import json
import socket
import re
import pathlib

import ssl as system_ssl

import requests_ja3.decoder as decoder
from requests_ja3.imitate.test_server import AsyncJA3Fetcher, UserAgent

def ja3_from_any_ssl (ssl_module: type (system_ssl)) -> (decoder.JA3, UserAgent):
    # ssl_module.test_no_ssl (client)
    # ssl_module.test_ssl (client)
    # return


    ja3_fetcher = AsyncJA3Fetcher (ssl_module)
    ja3_fetcher.start ()

    try:
        print ("making req")
        make_req_to_local_server (ssl_module)
        print ("done making req")
    except:
        print ("caught exception")
        ja3_fetcher.cancel ()
        raise

    ja3_fetcher.join ()

    return ja3_fetcher.fetch ()

def make_req_to_local_server (ssl_module: type (system_ssl)):
    context = ssl_module.create_default_context ()
    server_cert_dir = pathlib.Path (__file__).parent / "server_cert"
    context.load_verify_locations (cafile = str (server_cert_dir / "localhost.crt"))

    client = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

    wrapped_client = context.wrap_socket (client, server_hostname = "localhost")
    print ("connecting")
    wrapped_client.connect (("localhost", 8443))
    print ("connected, writing")
    def make_req (meth: str, url: str, headers: dict):
        crlf = "\r\n"
        return f"{meth} {url} HTTP/1.1{crlf}" \
               f"{''.join (f'{header_name}: {header_value}{crlf}' for header_name, header_value in headers.items ())}" \
               f"{crlf}".encode ()
    def parse_resp (resp: str):
        regex = r"HTTP/1.1 (?P<status_code>[0-9]+) (?P<status_text>[A-Za-z0-9 ]+)\r\n" \
                r"([^\r\n]+: [^\r\n]+\r\n)+\r\n" \
                r"(?P<response_data>[\s\S]*)"
        match = re.fullmatch (regex, resp)
        assert int (match.group ("status_code")) == 200
        return match.group ("response_data")
    wrapped_client.write (make_req ("GET", "/json", {
        "Host": "localhost",
        "Connection": "close",
        "Accept": "*/*",
        "User-Agent": "requests-ja3/HEAD"
    }))
    print ("done writing, reading response")
    in_buffer: bytearray = b""
    while True:
        in_bytes = wrapped_client.read (1024)
        if len (in_bytes) == 0: break
        in_buffer += in_bytes
    in_resp = in_buffer.decode ()
    print ("got the resp")
    in_resp_body = parse_resp (in_resp)
    in_json = json.loads (in_resp_body)
    wrapped_client.close ()
    del wrapped_client
    del context
