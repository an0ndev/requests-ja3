import pathlib
import re
import socket
import typing
import json
import threading

import ssl as system_ssl

import requests_ja3.decoder as decoder

class FailedToReadResponseError (Exception): pass

UserAgent = str
class JA3Fetcher:
    def __init__ (self, ssl_module: type (system_ssl)):
        self.ssl_module = ssl_module

        context = ssl_module.SSLContext (self.ssl_module.PROTOCOL_TLS_SERVER)
        server_cert_dir = pathlib.Path (__file__).parent / "server_cert"
        context.load_cert_chain (str (server_cert_dir / "localhost.crt"), str (server_cert_dir / "localhost.key"))

        self.server = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind (("localhost", 8443))
        self.server.listen (5)
        self.wrapped_server = context.wrap_socket (self.server, server_side = True)

        self.cancelled_lock = threading.Lock ()
        self.cancelled = False
    def fetch (self) -> (decoder.JA3, UserAgent):
        while True:
            try:
                try:
                    print ("--> waiting for client")
                    wrapped_client, client_address = self.wrapped_server.accept ()
                    print ("--> we have the client")
                except OSError:
                    with self.cancelled_lock:
                        if self.cancelled: return

                crlf = "\r\n"
                def parse_req (req: str) -> typing.Optional [dict]:
                    regex = fr"GET /[^{crlf} ]* HTTP/1.1{crlf}" \
                            fr"(?P<headers>([^{crlf}]+: [^{crlf}]+{crlf})+)" \
                            fr"{crlf}"
                    print (f"checking against >>{req}<<")
                    match = re.fullmatch (regex, req)
                    if match is None:
                        print ("no gots")
                        return None
                    print ("aye we got it")
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
                user_agent = parsed_headers ["User-Agent"]
                resp_ja3_str = wrapped_client.get_ja3_str (remove_grease = True)
                resp_ja3 = decoder.JA3.from_string (resp_ja3_str)
                resp_bytes = json.dumps ({
                    "ja3_hash": resp_ja3.to_hash (),
                    "ja3": resp_ja3_str,
                    "User-Agent": user_agent
                }).encode ()
                response = make_resp (200, "OK", {"Content-Type": "application/json"}, resp_bytes)

                wrapped_client.write (response)
                wrapped_client.close ()

                ret = (resp_ja3, user_agent)
                break
            except FailedToReadResponseError as failed_to_read_resp_error:
                print (failed_to_read_resp_error)
            except self.ssl_module.socket_exceptions.FailedAccept as failed_accept:
                print (failed_accept)

        self.wrapped_server.close ()
        return ret
    def cancel (self):
        with self.cancelled_lock:
            self.cancelled = True
        self.wrapped_server.close ()

class AsyncJA3Fetcher:
    def __init__ (self, fakessl):
        self.resp_ja3 = None
        self.user_agent = None
        self.fetcher = JA3Fetcher (fakessl)
        self.fetch_thread = threading.Thread (target = self._fetch)
    def start (self):
        self.fetch_thread.start ()
    def fetch (self) -> (decoder.JA3, UserAgent):
        self.fetch_thread.join ()
        return self.resp_ja3, self.user_agent
    def cancel (self):
        self.fetcher.cancel ()
    def join (self):
        self.fetch_thread.join ()
    def _fetch (self):
        self.resp_ja3, self.user_agent = self.fetcher.fetch ()
