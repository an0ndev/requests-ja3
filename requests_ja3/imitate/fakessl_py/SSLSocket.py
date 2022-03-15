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

class LibSSLError (Exception):
    def __init__ (self, thread_id: int, info: str, file_name: str, file_line: str, extra_data: str):
        super ().__init__ (f"Thread ID: {thread_id}, info: {info}, file name: {file_name}, file line: {file_line}, extra data: {extra_data}")
        self.thread_id = thread_id
        self.info = info
        self.file_name = file_name
        self.file_line = file_line
        self.extra_data = extra_data

def _get_libssl_errors () -> list [LibSSLError]:
    errors: list [LibSSLError] = []
    @libssl_type_bindings.ERR_print_errors_cb_callback
    def callback (_str: ctypes.c_char_p, _len: int, user_data: ctypes.c_void_p) -> int:
        error_details = ctypes.string_at (_str, _len).decode () [:-len ("\n")].split (":")
        libssl_error = LibSSLError (int (error_details [0]), ':'.join (error_details [1:-3]), error_details [-3], error_details [-2], error_details [-1])
        errors.append (libssl_error)
        return 1 # continue outputting the error report
    libssl_handle.ERR_print_errors_cb (callback, 0)
    return errors

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
        assert self.server_hostname is not None
        set_host_name_ret = libssl_handle.SSL_set_tlsext_host_name (self.ssl, self.server_hostname)
        if set_host_name_ret != 1:
            raise Exception (f"failed to set TLS host name: {self._get_error (set_host_name_ret)}")

        connect_ret = libssl_handle.SSL_connect (self.ssl)
        if connect_ret < 1:
            raise Exception (f"failed to connect using ssl object: {self._get_error (connect_ret)}")

        if self.context.verify_mode == VerifyMode.CERT_REQUIRED:
            get_verify_result = libssl_handle.SSL_get_verify_result (self.ssl)
            if get_verify_result != libssl_type_bindings.X509_V_OK:
                raise Exception ("failed to verify certificate")

        if self.context.check_hostname:
            certificate = self.getpeercert ()
            clean_ssl.match_hostname (certificate, self.server_hostname)
            raise Exception ("failed to check hostname")

        self.handshake_complete = True
    def getpeercert (self, binary_form = False) -> typing.Optional [typing.Union [dict, bytes]]:
        certificate = libssl_handle.SSL_get_peer_certificate (self.ssl)

        if binary_form:
            if certificate.value is None: return None
            certificate_bytes_ptr = ctypes.POINTER (ctypes.c_ubyte) ()
            certificate_bytes_ptr.value = 0
            certificate_encode_ret = libssl_handle.i2d_X509 (certificate, ctypes.byref (certificate_bytes_ptr))
            if certificate_encode_ret < 0: raise Exception ("encoding x509 certificate failed")
            return ctypes.string_at (certificate_bytes_ptr, certificate_encode_ret)
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
        error_code = libssl_handle.SSL_get_error (self.ssl, source_error_code)
        if error_code in [libssl_type_bindings.SSL_ERROR_SSL, libssl_type_bindings.SSL_ERROR_SYSCALL]:
            return ", ".join (map (str, _get_libssl_errors ()))
        else:
            return libssl_type_bindings.ssl_error_to_str (error_code)