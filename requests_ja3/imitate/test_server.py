import pathlib
import re
import socket
import typing
import json

import ssl as system_ssl

import requests_ja3.decoder as decoder
import requests_ja3.hasher as hasher

class FailedToReadResponseError (Exception): pass

def ja3_server_from_any_ssl (ssl_module: type (system_ssl)) -> (decoder.JA3, str, str, str): # JA3, JA3 str, hash, user agent
    context = ssl_module.SSLContext (ssl_module.PROTOCOL_TLS_SERVER)
    server_cert_dir = pathlib.Path (__file__).parent / "server_cert"
    context.load_cert_chain (str (server_cert_dir / "localhost.crt"), str (server_cert_dir / "localhost.key"))

    server = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind (("localhost", 8443))
    server.listen (5)
    wrapped_server = context.wrap_socket (server, server_side = True)

    ret = None

    while True:
        try:
            wrapped_client, client_address = wrapped_server.accept ()

            crlf = "\r\n"
            def parse_req (req: str) -> typing.Optional [dict]:
                regex = fr"GET / HTTP/1.1{crlf}" \
                        fr"(?P<headers>([^{crlf}]+: [^{crlf}]+{crlf})+)" \
                        fr"{crlf}"
                match = re.fullmatch (regex, req)
                if match is None: return None
                raw_headers = match.group ("headers")
                headers = {key: value for key, value in map (lambda raw_header: raw_header.split (": "), raw_headers.split (crlf) [:-1])}
                return headers
            def make_resp (status_code: int, status_text: str, headers: dict, response_data: bytes) -> bytes:
                headers.setdefault ("Content-Length", str (len (response_data)))
                headers_str = crlf.join (name + ': ' + value for name, value in headers.items ()) + crlf
                return (f"HTTP/1.1 {status_code} {status_text}{crlf}"
                       f"{headers_str}{crlf}").encode () + response_data

            in_buffer: bytearray = b""
            while True:
                in_bytes = wrapped_client.read (1024)
                if len (in_bytes) == 0:
                    wrapped_client.close ()
                    raise FailedToReadResponseError ("failed to read resp")
                in_buffer += in_bytes
                try:
                    req_str = in_bytes.decode ()
                except UnicodeDecodeError:
                    continue
                parsed_headers = parse_req (req_str)
                if parsed_headers is not None: break
            print (f"headers {parsed_headers}")
            user_agent = parsed_headers ["User-Agent"]
            resp_ja3_str = wrapped_client.get_ja3_str ()
            resp_ja3 = decoder.Decoder.decode (resp_ja3_str)
            ja3_hash = hasher.Hasher.hash (resp_ja3)
            print (f"hey our ja3 is {resp_ja3_str}")
            resp_bytes = json.dumps ({
                "ja3_hash": ja3_hash,
                "ja3": resp_ja3_str,
                "User-Agent": user_agent
            }).encode ()
            response = make_resp (200, "OK", {"Content-Type": "application/json"}, resp_bytes)

            wrapped_client.write (response)
            wrapped_client.close ()

            ret = (resp_ja3, resp_ja3_str, ja3_hash, user_agent)
            break
        except FailedToReadResponseError as failed_to_read_resp_error:
            print (failed_to_read_resp_error)
        except ssl_module.socket_exceptions.FailedAccept as failed_accept:
            print (failed_accept)

    wrapped_server.close ()
    return ret