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

    _s_m ("BIO_s_mem", [], types.BIO_method_ptr)
    _s_m ("BIO_new", [types.BIO_method_ptr], types.BIO_ptr)
    # _s_m ("BIO_get_mem_data", [types.BIO_ptr, ctypes.POINTER (ctypes.c_char_p)], ctypes.c_long)
    _s_m ("BIO_ctrl", [types.BIO_ptr, ctypes.c_int, ctypes.c_long, ctypes.c_void_p], ctypes.c_long)
    _s_m ("BIO_free", [types.BIO_ptr], None)

    _s_m ("TLS_client_method", [], types.SSL_METHOD_ptr)

    _s_m ("SSL_CTX_new", [], types.SSL_CTX_ptr)
    _s_m ("SSL_CTX_set_cipher_list", [types.SSL_CTX_ptr, ctypes.c_char_p], ctypes.c_int)
    _s_m ("SSL_CTX_load_verify_locations", [types.SSL_CTX_ptr, ctypes.c_char_p, ctypes.c_char_p], ctypes.c_int)
    _s_m ("SSL_CTX_use_certificate_chain_file", [types.SSL_CTX_ptr, ctypes.c_char_p], ctypes.c_int)
    _s_m ("SSL_CTX_free", [types.SSL_CTX_ptr], None)

    _s_m ("SSL_new", [types.SSL_CTX_ptr], types.SSL_ptr)
    _s_m ("SSL_get_error", [types.SSL_ptr, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_set_fd", [types.SSL_ptr, ctypes.c_int], ctypes.c_int)
    # _s_m ("SSL_set_tlsext_host_name", [types.SSL_ptr, ctypes.c_char_p], ctypes.c_int)
    _s_m ("SSL_ctrl", [types.SSL_ptr, ctypes.c_int, ctypes.c_long, ctypes.c_void_p], ctypes.c_long)
    _s_m ("SSL_connect", [types.SSL_ptr], ctypes.c_int)
    _s_m ("SSL_get_verify_result", [types.SSL_ptr], ctypes.c_long)
    _s_m ("SSL_get_peer_certificate", [types.SSL_ptr], types.X509_ptr)
    _s_m ("SSL_write", [types.SSL_ptr, ctypes.c_void_p, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_read", [types.SSL_ptr, ctypes.c_void_p, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_shutdown", [types.SSL_ptr], ctypes.c_int)
    _s_m ("SSL_free", [types.SSL_ptr], None)

    _s_m ("i2d_X509", [types.X509_ptr, ctypes.POINTER (ctypes.POINTER (ctypes.c_ubyte))], ctypes.c_int)
    _s_m ("X509_get_subject_name", [types.X509_ptr], types.X509_NAME_ptr)
    _s_m ("X509_get_issuer_name", [types.X509_ptr], types.X509_NAME_ptr)
    _s_m ("X509_get_version", [types.X509_ptr], ctypes.c_int)
    _s_m ("X509_get0_notBefore", [types.X509_ptr], types.ASN1_TIME_ptr)
    _s_m ("X509_get0_notAfter", [types.X509_ptr], types.ASN1_TIME_ptr)
    _s_m ("X509_get_serialNumber", [types.X509_ptr], types.ASN1_INTEGER_ptr)
    _s_m ("X509_free", [types.X509_ptr], None)

    _s_m ("X509_NAME_entry_count", [types.X509_NAME_ptr], ctypes.c_int)
    _s_m ("X509_NAME_get_entry", [types.X509_NAME_ptr, ctypes.c_int], types.X509_NAME_ENTRY_ptr)

    _s_m ("X509_NAME_ENTRY_get_object", [types.X509_NAME_ENTRY_ptr], types.ASN1_OBJECT_ptr)
    _s_m ("X509_NAME_ENTRY_get_data", [types.X509_NAME_ENTRY_ptr], types.ASN1_STRING_ptr)

    _s_m ("OBJ_obj2txt", [ctypes.c_char_p, ctypes.c_int, types.ASN1_OBJECT_ptr, ctypes.c_int], ctypes.c_int)
    _s_m ("OBJ_obj2nid", [types.ASN1_OBJECT_ptr], ctypes.c_int)
    _s_m ("OBJ_nid2ln", [ctypes.c_int], ctypes.c_char_p)

    _s_m ("ASN1_STRING_length", [types.ASN1_STRING_ptr], ctypes.c_int)
    _s_m ("ASN1_STRING_data", [types.ASN1_STRING_ptr], ctypes.c_char_p)

    _s_m ("ASN1_TIME_print", [types.BIO_ptr, types.ASN1_TIME_ptr], ctypes.c_int)

    _s_m ("i2a_ASN1_INTEGER", [types.BIO_ptr, types.ASN1_INTEGER_ptr], ctypes.c_int)

    _s_m ("ERR_print_errors_cb", [types.ERR_print_errors_cb_callback, ctypes.c_void_p], None)

    return libssl_handle
