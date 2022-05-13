import ctypes

class BIO_method_ptr       (ctypes.c_void_p): pass
class BIO_ptr              (ctypes.c_void_p): pass
class SSL_METHOD_ptr       (ctypes.c_void_p): pass
class SSL_CTX_ptr          (ctypes.c_void_p): pass
class SSL_CIPHER_ptr       (ctypes.c_void_p): pass
class OPENSSL_STACK_ptr    (ctypes.c_void_p): pass
OPENSSL_sk_compfunc = ctypes.CFUNCTYPE (ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
OPENSSL_sk_copyfunc = ctypes.CFUNCTYPE (ctypes.c_void_p, ctypes.c_void_p)
OPENSSL_sk_freefunc = ctypes.CFUNCTYPE (None, ctypes.c_void_p)
def define_types_for_stack_of (inner_class: type (ctypes.c_void_p), class_name: str):
    stack_class_name = f"STACK_OF_{class_name}_ptr"
    class STACK_OF_cls_ptr (ctypes.c_void_p):
        inner = inner_class
        inner_name = class_name
    STACK_OF_cls_ptr.__name__ = stack_class_name
    globals () [stack_class_name] = STACK_OF_cls_ptr
    globals () [f"sk_{class_name}_compfunc"] = ctypes.CFUNCTYPE (ctypes.c_int, inner_class, inner_class)
    globals () [f"sk_{class_name}_copyfunc"] = ctypes.CFUNCTYPE (inner_class, inner_class)
    globals () [f"sk_{class_name}_freefunc"] = ctypes.CFUNCTYPE (None, inner_class)

define_types_for_stack_of (SSL_CIPHER_ptr, "SSL_CIPHER")
class SSL_ptr              (ctypes.c_void_p): pass
class X509_ptr             (ctypes.c_void_p): pass
class X509_NAME_ptr        (ctypes.c_void_p): pass
class X509_NAME_ENTRY_ptr  (ctypes.c_void_p): pass
class ASN1_OBJECT_ptr      (ctypes.c_void_p): pass
class ASN1_STRING_ptr      (ctypes.c_void_p): pass
class ASN1_TIME_ptr        (ctypes.c_void_p): pass
class ASN1_INTEGER_ptr     (ctypes.c_void_p): pass
ERR_print_errors_cb_callback = ctypes.CFUNCTYPE (ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_void_p)
SSL_CTX_keylog_cb_func = ctypes.CFUNCTYPE (None, SSL_ptr, ctypes.c_char_p)

# <OpenSSL src>/include/openssl/x509.h
X509_FILETYPE_PEM = 1
X509_FILETYPE_ASN1 = 2

# defined in <OpenSSL src>/include/openssl/x509_vfy.h.in
X509_V_OK = 0

# defined in <OpenSSL src>/include/openssl/ssl.h
SSL_CT_VALIDATION_PERMISSIVE = 0
SSL_FILETYPE_ASN1 = X509_FILETYPE_ASN1
SSL_FILETYPE_PEM = X509_FILETYPE_PEM

# defined in <OpenSSL src>/include/openssl/ssl.h.in
SSL_VERIFY_NONE = 0
SSL_VERIFY_PEER = 1 << 0
# SSL_VERIFY_
SSL_ERROR_NONE                 = 0
SSL_ERROR_SSL                  = 1
SSL_ERROR_WANT_READ            = 2
SSL_ERROR_WANT_WRITE           = 3
SSL_ERROR_WANT_X509_LOOKUP     = 4
SSL_ERROR_SYSCALL              = 5
SSL_ERROR_ZERO_RETURN          = 6
SSL_ERROR_WANT_CONNECT         = 7
SSL_ERROR_WANT_ACCEPT          = 8
SSL_ERROR_WANT_ASYNC           = 9
SSL_ERROR_WANT_ASYNC_JOB       = 10
SSL_ERROR_WANT_CLIENT_HELLO_CB = 11
SSL_ERROR_WANT_RETRY_VERIFY    = 12
ssl_error_to_str = lambda value: {_value: name for name, _value in locals ().items () if name.startswith ("SSL_ERROR_")} [value]

# SSL_CTRL_
SSL_CTRL_SET_TLSEXT_HOSTNAME = 55
SSL_CTRL_SET_TLSEXT_STATUS_REQ_TYPE = 65
SSL_CTRL_SET_GROUPS_LIST = 92

# <OpenSSL src>/include/openssl/bio.h.in
# BIO_CTRL_
BIO_CTRL_INFO = 3

# defined in <OpenSSL src>/include/openssl/tls1.h
TLSEXT_NAMETYPE_host_name = 0
TLSEXT_STATUSTYPE_ocsp = 1