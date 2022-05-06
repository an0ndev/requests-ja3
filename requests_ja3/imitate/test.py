import json
import socket
import re

import ssl as system_ssl

import requests_ja3.decoder as decoder

def ja3_from_any_ssl (ssl_module: type (system_ssl)) -> decoder.JA3:
    context = ssl_module.create_default_context ()
    client = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    # ssl_module.test_no_ssl (client)
    # ssl_module.test_ssl (client)
    # return

    wrapped_client = context.wrap_socket (client, server_hostname = "ja3er.com")
    wrapped_client.connect (("ja3er.com", 443))
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
        "Host": "ja3er.com",
        "Connection": "close",
        "Accept": "*/*",
        "User-Agent": "requests-ja3/HEAD"
    }))
    in_buffer: bytearray = b""
    while True:
        in_bytes = wrapped_client.read (1024)
        if len (in_bytes) == 0: break
        in_buffer += in_bytes
    in_resp = in_buffer.decode ()
    in_resp_body = parse_resp (in_resp)
    in_json = json.loads (in_resp_body)
    wrapped_client.close ()
    del wrapped_client
    del context

    return decoder.Decoder.decode (in_json ["ja3"])