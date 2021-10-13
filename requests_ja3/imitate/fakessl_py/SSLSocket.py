import ctypes
libssl_handle: ctypes.CDLL = None
def initialize (_libssl_handle):
    global libssl_handle
    libssl_handle = _libssl_handle

import socket as _socket_module

class SSLSocket:
    def __init__ (self, socket: _socket_module.socket, context):
        self.socket = socket
        self.context = context
        self.fd = ctypes.c_int (socket.fileno ())

        self.ssl = libssl_handle.SSL_new (self.context.context)
        if not self.ssl: raise Exception ("failed to create ssl object")
    def connect (self, address: tuple):
        self.socket.connect (address)

        set_fd_ret = libssl_handle.SSL_set_fd (self.ssl, self.fd)
        if set_fd_ret == 0: raise Exception ("failed to set ssl file descriptor")

        connect_ret = libssl_handle.SSL_connect (self.ssl)
        if connect_ret < 1: raise Exception ("failed to connect using ssl object")
    def write (self, data: bytes):
        write_ret = libssl_handle.SSL_write (self.ssl, data, len (data))
        if write_ret <= 0: raise Exception ("failed to write to ssl object")
        if write_ret < len (data): raise Exception (f"only wrote {write_ret}/{len (data)} bytes to ssl object")
    def read (self, count: int) -> bytes:
        out = (ctypes.c_ubyte * count) ()
        read_ret = libssl_handle.SSL_read (self.ssl, ctypes.cast (out, ctypes.c_void_p), count)
        if read_ret < 0: raise Exception ("failed to read from ssl object")
        return bytes (out) [:read_ret]
    def close (self):
        shutdown_ret = libssl_handle.SSL_shutdown (self.ssl)
        if shutdown_ret < 0: raise Exception ("failed to shutdown ssl object")
    def __del__ (self):
        libssl_handle.SSL_free (self.ssl)
