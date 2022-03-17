import ctypes

class BIO_method_ptr       (ctypes.c_void_p): pass
class BIO_ptr              (ctypes.c_void_p): pass
class SSL_METHOD_ptr       (ctypes.c_void_p): pass
class SSL_CTX_ptr          (ctypes.c_void_p): pass
class SSL_ptr              (ctypes.c_void_p): pass
class X509_ptr             (ctypes.c_void_p): pass
class X509_NAME_ptr        (ctypes.c_void_p): pass
class X509_NAME_ENTRY_ptr  (ctypes.c_void_p): pass
class ASN1_OBJECT_ptr      (ctypes.c_void_p): pass
class ASN1_STRING_ptr      (ctypes.c_void_p): pass
class ASN1_TIME_ptr        (ctypes.c_void_p): pass
class ASN1_INTEGER_ptr     (ctypes.c_void_p): pass
ERR_print_errors_cb_callback = ctypes.CFUNCTYPE (ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_void_p)

# defined in <OpenSSL src>/include/openssl/x509_vfy.h.in
X509_V_OK = 0

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

# <OpenSSL src>/include/openssl/bio.h.in
# BIO_CTRL_
BIO_CTRL_INFO = 3

# defined in <OpenSSL src>/include/openssl/tls1.h
TLSEXT_NAMETYPE_host_name = 0