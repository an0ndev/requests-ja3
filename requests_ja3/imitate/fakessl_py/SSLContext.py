import ctypes
import typing
import os

from . import libssl_type_bindings as types

from requests_ja3.decoder import JA3

libssl_handle: ctypes.CDLL = None
target_ja3: JA3 = None

def initialize (_libssl_handle, _target_ja3):
    global libssl_handle, target_ja3
    libssl_handle = _libssl_handle
    SSLSocket_module.initialize (libssl_handle, _target_ja3)
    target_ja3 = _target_ja3

from . import SSLSocket as SSLSocket_module
SSLSocket = SSLSocket_module.SSLSocket
socket_exceptions = SSLSocket_module.socket_exceptions

from . import protocol_constants

from .Options import Options, VerifyMode

def stub (name): return lambda *args, **kwargs: print (f"{name} called with args {args} and kwargs {kwargs}")

class SSLContext:
    def __init__ (self, protocol = None):
        if protocol is None: raise Exception ("protocol must be PROTOCOL_TLS_CLIENT or PROTOCOL_TLS_SERVER")
        if protocol not in (protocol_constants.PROTOCOL_TLS_CLIENT, protocol_constants.PROTOCOL_TLS_SERVER): raise Exception ("alternate protocols not supported")
        self._is_client = protocol == protocol_constants.PROTOCOL_TLS_CLIENT

        method: types.SSL_METHOD_ptr = libssl_handle.TLS_client_method () if self._is_client else libssl_handle.TLS_server_method ()
        self.context: types.SSL_CTX_ptr = libssl_handle.SSL_CTX_new (method)
        if not self.context: raise Exception ("failed to create ssl context")
        self.options: Options = Options.OP_ALL

        if self._is_client:
            self.check_hostname = True
            self.verify_mode = VerifyMode.CERT_REQUIRED
        else:
            self.check_hostname = False
            self.verify_mode = VerifyMode.CERT_NONE

        if self.verify_mode == VerifyMode.CERT_REQUIRED:
            libssl_handle.SSL_CTX_set_verify (self.context, types.SSL_VERIFY_PEER, None)

        if self._is_client:
            self._do_client_setup ()
    def _do_client_setup (self):
        if 5 in target_ja3 ["list_of_extensions"]:
            set_tlsext_status_type_ret = libssl_handle.SSL_CTX_set_tlsext_status_type (self.context, types.TLSEXT_STATUSTYPE_ocsp)
            if set_tlsext_status_type_ret == 0: raise Exception ("failed to enable extension #5")

        if 16 in target_ja3 ["list_of_extensions"]:
            proto_name = "http/1.1".encode ()
            proto_name_bytes = bytes ([len (proto_name)]) + proto_name
            set_alpn_protos_ret = libssl_handle.SSL_CTX_set_alpn_protos (self.context, proto_name_bytes, len (proto_name_bytes))
            if set_alpn_protos_ret != 0: raise Exception ("failed to enable extension #16 (ALPN)")

        if 18 in target_ja3 ["list_of_extensions"]:
            enable_ct_ret = libssl_handle.SSL_CTX_enable_ct (self.context, types.SSL_CT_VALIDATION_PERMISSIVE)
            if enable_ct_ret != 1: raise Exception ("failed to enable extension #18 (certificate transparency)")

        if 21 not in target_ja3 ["list_of_extensions"]:
            self.options ^= Options.OP_TLSEXT_PADDING

        if 22 not in target_ja3 ["list_of_extensions"]:
            self.options |= Options.OP_NO_ENCRYPT_THEN_MAC

        libssl_handle.SSL_CTX_set_options (self.context, self.options)

        if 10 in target_ja3 ["list_of_extensions"] and False: # supported_groups
            groups_list = ':'.join (str (supported_group) for supported_group in target_ja3 ["elliptic_curve"])
            groups = target_ja3 ["elliptic_curve"]
            groups_array = (ctypes.c_int * len (groups)) (*groups)
            set1_groups_list_ret = libssl_handle.SSL_CTX_set1_groups_list (self.context, groups_list)
            if set1_groups_list_ret != 1: raise Exception ("failed to set supported groups")
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
        self.set_default_verify_paths ()
    def load_cert_chain (self, certfile: str, keyfile: str = None, password: typing.Optional [typing.Union [typing.Callable [[], typing.Union [str, bytes, bytearray]], str, bytes, bytearray]] = None):
        if password is not None: raise Exception ("encrypted cert chain not implemented")


        use_certificate_chain_file_ret = libssl_handle.SSL_CTX_use_certificate_chain_file (self.context, certfile.encode ())
        if use_certificate_chain_file_ret < 1: raise Exception ("failed to use certificate file")

        if keyfile is not None:
            use_private_key_file_ret = libssl_handle.SSL_CTX_use_PrivateKey_file (self.context, keyfile.encode (), types.X509_FILETYPE_PEM)
            if use_private_key_file_ret < 1: raise Exception ("failed to use private key")
    def set_default_verify_paths (self):
        self.load_verify_locations (cafile = "/etc/ssl/certs/ca-certificates.crt", capath = "/etc/ssl/certs")
    def wrap_socket (self, socket, server_side = False, do_handshake_on_connect = True, server_hostname: typing.Optional [str] = None, session = None):
        return SSLSocket (socket, self, server_side = server_side, do_handshake_on_connect = do_handshake_on_connect, server_hostname = server_hostname, session = session)
    def __del__ (self):
        libssl_handle.SSL_CTX_free (self.context)