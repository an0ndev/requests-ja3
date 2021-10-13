import ctypes
import typing

from . import libssl_type_bindings as types

def get_bound_libssl () -> ctypes.CDLL:
    libssl_handle = ctypes.cdll.LoadLibrary ("libssl.so")

    def _setup_method (method_name: str, argtypes: list, restype: typing.Any):
        method = getattr (libssl_handle, method_name)
        method.argtypes = argtypes
        method.restype = restype
    _s_m = _setup_method

    _setup_method ("TLS_client_method", [], types.SSL_METHOD_ptr)

    _s_m ("SSL_CTX_new", [], types.SSL_CTX_ptr)
    _s_m ("SSL_CTX_free", [types.SSL_CTX_ptr], None)

    _s_m ("SSL_new", [types.SSL_CTX_ptr], types.SSL_ptr)
    _s_m ("SSL_set_fd", [types.SSL_ptr, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_connect", [types.SSL_ptr], ctypes.c_int)
    _s_m ("SSL_write", [types.SSL_ptr, ctypes.c_void_p, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_read", [types.SSL_ptr, ctypes.c_void_p, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_shutdown", [types.SSL_ptr], ctypes.c_int)
    _s_m ("SSL_free", [types.SSL_ptr], None)

    return libssl_handle
