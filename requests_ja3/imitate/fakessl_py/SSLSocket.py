import typing

import ctypes
libssl_handle: ctypes.CDLL = None
def initialize (_libssl_handle):
    global libssl_handle
    libssl_handle = _libssl_handle

from . import libssl_type_bindings

import socket as _socket_module

import ssl as clean_ssl

from .Options import VerifyMode

def _get_libssl_errors () -> str:
    errors = []
    @libssl_type_bindings.ERR_print_errors_cb_callback
    def callback (_str: ctypes.c_char_p, _len: ctypes.c_size_t, user_data: ctypes.c_void_p) -> int:
        print ("callback called")
        errors.append (_str [:_len])
        return 0
    print ("calling ERR_print_errors_cb")
    libssl_handle.ERR_print_errors_cb (callback, None)
    return "".join (errors)

class SSLSocket:
    def __init__ (self, socket: _socket_module.socket, context, server_side = False, do_handshake_on_connect = True, server_hostname: typing.Optional [str] = None, session = None):
        self.socket = socket
        self.context = context
        self.fd = ctypes.c_int (socket.fileno ())

        self.ssl = libssl_handle.SSL_new (self.context.context)
        if not self.ssl: raise Exception ("failed to create ssl object")

        if server_side: raise NotImplemented ("server-side sockets not implemented")
        self.do_handshake_on_connect = do_handshake_on_connect
        self.handshake_complete = False

        self.server_hostname = server_hostname

        if session is not None: raise NotImplemented ("SSLSession not yet supported")
    def connect (self, address: tuple):
        self.socket.connect (address)

        set_fd_ret = libssl_handle.SSL_set_fd (self.ssl, self.fd)
        if set_fd_ret == 0: raise Exception ("failed to set ssl file descriptor")

        if self.do_handshake_on_connect:
            self.do_handshake ()
    def do_handshake (self):
        connect_ret = libssl_handle.SSL_connect (self.ssl)
        if connect_ret < 1:
            raise Exception (f"failed to connect using ssl object: {self._get_error (connect_ret)}")

        if self.context.verify_mode == VerifyMode.CERT_REQUIRED:
            get_verify_result = libssl_handle.SSL_get_verify_result (self.ssl)
            print (get_verify_result)
            if get_verify_result != libssl_type_bindings.X509_V_OK:
                raise Exception ("failed to verify certificate")

        if self.context.check_hostname:
            certificate = self.getpeercert ()
            clean_ssl.match_hostname (certificate, self.server_hostname)
            raise Exception ("failed to check hostname")

        self.handshake_complete = True
    def getpeercert (self, binary_form = False) -> typing.Optional [typing.Union [dict, bytes]]:
        certificate = libssl_handle.SSL_get_peer_certificate (self.ssl)
        print (certificate)
        if binary_form:
            if certificate is None: return None
            certificate_bytes_ptr = (ctypes.c_void_p * 1) ()
            certificate_encode_ret = libssl_handle.i2d_X509 (certificate, ctypes.cast (certificate_bytes_ptr, ctypes.c_void_p))
            if certificate_encode_ret < 0: raise Exception ("encoding x509 certificate failed")
            return bytes (ctypes.cast (certificate_bytes_ptr, ctypes.c_char * certificate_encode_ret))
        else:
            raise Exception (f"non-binary form not supported")
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
    def _get_error (self, source_error_code: int) -> str:
        print ("starting _get_error")
        error_code = libssl_handle.SSL_get_error (self.ssl, source_error_code)
        print (f"got error_code {error_code}")
        if error_code in [libssl_type_bindings.SSL_ERROR_SSL, libssl_type_bindings.SSL_ERROR_SYSCALL]:
            print (f"calling _get_libssl_errors")
            return _get_libssl_errors ()
        else:
            return libssl_type_bindings.ssl_error_to_str (error_code)