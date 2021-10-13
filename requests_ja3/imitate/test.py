import re
import socket

import ssl as system_ssl

def test_any_ssl (ssl_module: type (system_ssl)):
    context = ssl_module.SSLContext ()
    client = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    # ssl_module.test_no_ssl (client)
    # ssl_module.test_ssl (client)
    # return

    input ("press enter to do the shit")
    wrapped_client = context.wrap_socket (client)
    print ("calling connect")
    wrapped_client.connect (("www.google.com", 443))
    print ("called connect")
    wrapped_client.write ("GET /gen_204 HTTP/1.0\r\nConnection: close\r\n\r\n".encode ())
    in_buffer: bytearray = b""
    while True:
        in_bytes = wrapped_client.read (1024)
        if len (in_bytes) == 0: break
        in_buffer += in_bytes
    in_str = in_buffer.decode ()
    assert re.match (r"HTTP/1.0 204 No Content\r\n[\s\S]+\r\n\r\n", in_str) is not None
    wrapped_client.close ()
    del wrapped_client