import ctypes
from . import libssl_type_bindings as types
libssl_handle: ctypes.CDLL = None
def initialize (_libssl_handle):
    global libssl_handle
    libssl_handle = _libssl_handle
    SSLSocket_module.initialize (libssl_handle)

from . import SSLSocket as SSLSocket_module
SSLSocket = SSLSocket_module.SSLSocket

class SSLContext:
    def __init__ (self):
        self.context: types.SSL_CTX_ptr = libssl_handle.SSL_CTX_new (libssl_handle.TLS_client_method ())
        if not self.context: raise Exception ("failed to create ssl context")
    def wrap_socket (self, socket):
        return SSLSocket (socket, self)
    def __del__ (self):
        libssl_handle.SSL_CTX_free (self.context)