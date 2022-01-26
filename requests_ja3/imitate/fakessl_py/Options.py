class Options (int):
    OP_NO_COMPRESSION = 1 << 0
    OP_NO_TICKET = 1 << 1
    OP_NO_SSLv2 = 1 << 2
    OP_NO_SSLv3 = 1 << 3
    OP_ALL = OP_NO_COMPRESSION | OP_NO_TICKET | OP_NO_SSLv2 | OP_NO_SSLv3

class VerifyMode (int):
    CERT_NONE = 0
    CERT_OPTIONAL = 1
    CERT_REQUIRED = 2