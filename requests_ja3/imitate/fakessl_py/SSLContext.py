import ctypes
import typing
import os

from . import libssl_type_bindings as types
libssl_handle: ctypes.CDLL = None
def initialize (_libssl_handle):
    global libssl_handle
    libssl_handle = _libssl_handle
    SSLSocket_module.initialize (libssl_handle)

from . import SSLSocket as SSLSocket_module
SSLSocket = SSLSocket_module.SSLSocket

from . import protocol_constants

from .Options import Options, VerifyMode

def stub (name): return lambda *args, **kwargs: print (f"{name} called with args {args} and kwargs {kwargs}")

class SSLContext:
    def __init__ (self, protocol = protocol_constants.PROTOCOL_TLS_CLIENT):
        if protocol != protocol_constants.PROTOCOL_TLS_CLIENT: raise Exception ("alternate protocols not supported")
        self.context: types.SSL_CTX_ptr = libssl_handle.SSL_CTX_new (libssl_handle.TLS_client_method ())
        if not self.context: raise Exception ("failed to create ssl context")
        self.options: Options = Options.OP_ALL

        self.verify_mode = VerifyMode.CERT_REQUIRED
        self.check_hostname = True

        if self.verify_mode == VerifyMode.CERT_REQUIRED:
            libssl_handle.SSL_CTX_set_verify (self.context, types.SSL_VERIFY_PEER, None)
    def set_ciphers (self, cipher_list: str):
        set_cipher_list_ret = libssl_handle.SSL_CTX_set_cipher_list (self.context, cipher_list.encode ())
        if set_cipher_list_ret == 0: raise Exception ("failed to set cipher list on ssl context")
    def load_verify_locations (self, cafile: typing.Optional [str] = None, capath: typing.Optional [str] = None, cadata: typing.Optional [typing.Union [str, bytes]] = None):
        if cafile is not None or capath is not None:
            load_verify_locations_ret = libssl_handle.SSL_CTX_load_verify_locations (self.context, cafile.encode () if cafile is not None else None, capath.encode () if capath is not None else None)
            if load_verify_locations_ret < 1: raise Exception ("failed to load verify locations")
        if cadata is not None:
            if isinstance (cadata, str): cadata = cadata.encode ()
            use_certificate_chain_file_ret = libssl_handle.SSL_CTX_use_certificate_chain_file (self.context, cadata)
            if use_certificate_chain_file_ret < 1: raise Exception ("failed to use certificate file")
    def load_default_certs (self, purpose: protocol_constants.Purpose):
        assert purpose == protocol_constants.Purpose.CLIENT_AUTH
        self.set_default_verify_paths ()
    def set_default_verify_paths (self):
        self.load_verify_locations (cafile = "/etc/ssl/certs/ca-certificates.crt", capath = "/etc/ssl/certs")
    def wrap_socket (self, socket, server_side = False, do_handshake_on_connect = True, server_hostname: typing.Optional [str] = None, session = None):
        return SSLSocket (socket, self, server_side = server_side, do_handshake_on_connect = do_handshake_on_connect, server_hostname = server_hostname, session = session)
    def __del__ (self):
        libssl_handle.SSL_CTX_free (self.context)