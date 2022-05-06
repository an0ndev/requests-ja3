import ctypes
from . import libssl_type_bindings as types

class MacrosMixin:
    @staticmethod
    def SSL_set_tlsext_host_name (libssl_handle, s, name):
        return libssl_handle.SSL_ctrl (s, types.SSL_CTRL_SET_TLSEXT_HOSTNAME, types.TLSEXT_NAMETYPE_host_name, name)
    @staticmethod
    def BIO_get_mem_data (libssl_handle, b, pp):
        return libssl_handle.BIO_ctrl (b, types.BIO_CTRL_INFO, 0, pp)
    @staticmethod
    def SSL_CTX_set_tlsext_status_type (libssl_handle, ssl, _type):
        return libssl_handle.SSL_CTX_ctrl (ssl, types.SSL_CTRL_SET_TLSEXT_STATUS_REQ_TYPE, _type, 0)
    @staticmethod
    def SSL_CTX_set1_groups_list (libssl_handle, ctx, s):
        return libssl_handle.SSL_CTX_ctrl (ctx, types.SSL_CTRL_SET_GROUPS_LIST, 0, ctypes.cast (s, ctypes.c_char_p))
    @staticmethod
    def OPENSSL_free (libssl_handle, addr):
        string_buf = ctypes.create_string_buffer (1)
        return libssl_handle.CRYPTO_free (addr, string_buf, 0)
