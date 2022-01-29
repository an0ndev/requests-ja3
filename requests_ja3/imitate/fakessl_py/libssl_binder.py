import ctypes
import typing
import pathlib

from . import libssl_type_bindings as types

def get_bound_libssl (libssl_path: pathlib.Path) -> ctypes.CDLL:
    libssl_handle = ctypes.cdll.LoadLibrary (str (libssl_path))

    def _setup_method (method_name: str, argtypes: list, restype: typing.Any):
        method = getattr (libssl_handle, method_name)
        method.argtypes = argtypes
        method.restype = restype
    _s_m = _setup_method

    _setup_method ("TLS_client_method", [], types.SSL_METHOD_ptr)

    _s_m ("SSL_CTX_new", [], types.SSL_CTX_ptr)
    _s_m ("SSL_CTX_set_cipher_list", [types.SSL_CTX_ptr, ctypes.c_char_p], ctypes.c_int)
    _s_m ("SSL_CTX_load_verify_locations", [types.SSL_CTX_ptr, ctypes.c_char_p, ctypes.c_char_p], ctypes.c_int)
    _s_m ("SSL_CTX_use_certificate_chain_file", [types.SSL_CTX_ptr, ctypes.c_char_p], ctypes.c_int)
    _s_m ("SSL_CTX_free", [types.SSL_CTX_ptr], None)

    _s_m ("SSL_new", [types.SSL_CTX_ptr], types.SSL_ptr)
    _s_m ("SSL_get_error", [types.SSL_ptr, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_set_fd", [types.SSL_ptr, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_connect", [types.SSL_ptr], ctypes.c_int)
    _s_m ("SSL_get_verify_result", [types.SSL_ptr], ctypes.c_long)
    _s_m ("SSL_get_peer_certificate", [types.SSL_ptr], types.X509_ptr)
    _s_m ("SSL_write", [types.SSL_ptr, ctypes.c_void_p, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_read", [types.SSL_ptr, ctypes.c_void_p, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_shutdown", [types.SSL_ptr], ctypes.c_int)
    _s_m ("SSL_free", [types.SSL_ptr], None)

    _s_m ("i2d_X509", [types.X509_ptr, ctypes.c_char_p], ctypes.c_int)

    _s_m ("ERR_print_errors_cb", [ctypes.POINTER (types.ERR_print_errors_cb_callback), ctypes.c_void_p], None)

    return libssl_handle
