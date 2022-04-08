import typing

import ctypes

from requests_ja3.decoder import JA3

libssl_handle: ctypes.CDLL = None
target_ja3: JA3 = None

def initialize (_libssl_handle, _target_ja3: JA3):
    global libssl_handle, target_ja3
    libssl_handle = _libssl_handle
    target_ja3 = _target_ja3

from . import libssl_type_bindings as types

import socket as _socket_module

import ssl as clean_ssl

from .Options import VerifyMode

class LibSSLError (Exception):
    def __init__ (self, thread_id: int, info: str, file_name: str, file_line: str, extra_data: str):
        super ().__init__ (f"Thread ID: {thread_id}, info: {info}, file name: {file_name}, file line: {file_line}, extra data: {extra_data}")
        self.thread_id = thread_id
        self.info = info
        self.file_name = file_name
        self.file_line = file_line
        self.extra_data = extra_data

def _get_libssl_errors () -> list [LibSSLError]:
    errors: list [LibSSLError] = []
    @types.ERR_print_errors_cb_callback
    def callback (_str: ctypes.c_char_p, _len: int, user_data: ctypes.c_void_p) -> int:
        error_details = ctypes.string_at (_str, _len).decode () [:-len ("\n")].split (":")
        libssl_error = LibSSLError (int (error_details [0]), ':'.join (error_details [1:-3]), error_details [-3], error_details [-2], error_details [-1])
        errors.append (libssl_error)
        return 1 # continue outputting the error report
    libssl_handle.ERR_print_errors_cb (callback, 0)
    return errors

def _get_libssl_error_str () -> str:
    return ", ".join (map (str, _get_libssl_errors ()))

class SSLSocket:
    def __init__ (self, socket: _socket_module.socket, context, server_side = False, do_handshake_on_connect = True, server_hostname: typing.Optional [str] = None, session = None):
        self.socket = socket
        self.context = context
        self.fd = ctypes.c_int (socket.fileno ())

        self.ssl = libssl_handle.SSL_new (self.context.context)
        if not self.ssl: raise Exception ("failed to create ssl object")

        if server_side: raise NotImplemented ("server-side sockets not implemented")
        self.do_handshake_on_connect = do_handshake_on_connect
        self.handshake_complete = False

        self.server_hostname = server_hostname

        if session is not None: raise NotImplemented ("SSLSession not yet supported")

        supported_ciphers: types.STACK_OF_SSL_CIPHER_ptr = libssl_handle.SSL_get_ciphers (self.ssl)

        # Make sure all requested ciphers are available
        # (the list of supported ciphers starts as the list of all available)
        supported_ciphers_ids = libssl_handle.cipher_ids_from_stack (supported_ciphers)
        for required_cipher in target_ja3 ["accepted_ciphers"]:
            if required_cipher not in supported_ciphers_ids:
                raise Exception (f"Your build of OpenSSL does not support cipher {required_cipher}")

        ### START MODIFICATION OF ACCEPTED CIPHERS FIELD

        # need to flatten to list to be able to modify while iterating
        supported_ciphers_list: list [types.SSL_CIPHER_ptr] = list (libssl_handle.stack_iterator (supported_ciphers))
        for supported_cipher in supported_ciphers_list:
            supported_cipher_id = libssl_handle.SSL_CIPHER_get_protocol_id (supported_cipher)
            if supported_cipher_id not in target_ja3 ["accepted_ciphers"]:
                delete_ret = libssl_handle.sk_SSL_CIPHER_delete_ptr (supported_ciphers, supported_cipher)
                assert delete_ret and ctypes.cast (delete_ret, ctypes.c_void_p).value == ctypes.cast (supported_cipher, ctypes.c_void_p).value

        ### END MODIFICATION OF ACCEPTED CIPHERS FIELD

        ciphers_to_use: types.STACK_OF_SSL_CIPHER_ptr = libssl_handle.SSL_get1_supported_ciphers (self.ssl)
        try:
            ciphers_to_use_ids = libssl_handle.cipher_ids_from_stack (ciphers_to_use)
            print (f"CIPHERS TO USE: {ciphers_to_use_ids}")
            assert target_ja3 ["accepted_ciphers"] == ciphers_to_use_ids
        finally:
            libssl_handle.OPENSSL_sk_free (ctypes.cast (ciphers_to_use, types.OPENSSL_STACK_ptr))
    def connect (self, address: tuple):
        self.socket.connect (address)

        set_fd_ret = libssl_handle.SSL_set_fd (self.ssl, self.fd)
        if set_fd_ret == 0: raise Exception ("failed to set ssl file descriptor")

        if self.do_handshake_on_connect:
            self.do_handshake ()
    def do_handshake (self):
        assert self.server_hostname is not None
        set_host_name_ret = libssl_handle.SSL_set_tlsext_host_name (self.ssl, self.server_hostname)
        if set_host_name_ret != 1:
            raise Exception (f"failed to set TLS host name: {self._get_error (set_host_name_ret)}")

        connect_ret = libssl_handle.SSL_connect (self.ssl)
        if connect_ret < 1:
            raise Exception (f"failed to connect using ssl object: {self._get_error (connect_ret)}")

        if self.context.verify_mode == VerifyMode.CERT_REQUIRED:
            get_verify_result = libssl_handle.SSL_get_verify_result (self.ssl)
            if get_verify_result != types.X509_V_OK:
                raise Exception ("failed to verify certificate")

        if self.context.check_hostname:
            certificate = self.getpeercert ()
            clean_ssl.match_hostname (certificate, self.server_hostname)

        self.handshake_complete = True
    def getpeercert (self, binary_form = False) -> typing.Optional [typing.Union [dict, bytes]]:
        certificate = libssl_handle.SSL_get_peer_certificate (self.ssl)
        if certificate.value is None: return None

        try:
            if binary_form:
                certificate_bytes_ptr = ctypes.POINTER (ctypes.c_ubyte) ()
                certificate_bytes_ptr.value = 0
                certificate_encode_ret = libssl_handle.i2d_X509 (certificate, ctypes.byref (certificate_bytes_ptr))
                if certificate_encode_ret < 0: raise Exception ("encoding x509 certificate failed")
                return ctypes.string_at (certificate_bytes_ptr, certificate_encode_ret)
            else:
                if libssl_handle.SSL_get_verify_result (self.ssl) != types.X509_V_OK:
                    return {}
                else:
                    # example: https://docs.python.org/3/library/ssl.html#ssl.SSLSocket.getpeercert

                    def decode_X509_NAME (name: types.X509_NAME_ptr):
                        rdns = []
                        for entry_index in range (libssl_handle.X509_NAME_entry_count (name)):
                            entry = libssl_handle.X509_NAME_get_entry (name, entry_index)

                            asn1_obj = libssl_handle.X509_NAME_ENTRY_get_object (entry)
                            asn1_obj_nid = libssl_handle.OBJ_obj2nid (asn1_obj)
                            asn1_key = ctypes.string_at (libssl_handle.OBJ_nid2ln (asn1_obj_nid)).decode ()

                            asn1_str = libssl_handle.X509_NAME_ENTRY_get_data (entry)
                            asn1_val = ctypes.string_at (libssl_handle.ASN1_STRING_data (asn1_str), libssl_handle.ASN1_STRING_length (asn1_str)).decode ()

                            rdns.append (((asn1_key, asn1_val),))
                        return tuple (rdns)

                    decoded = {}

                    decoded ["subject"] = decode_X509_NAME (libssl_handle.X509_get_subject_name (certificate))
                    decoded ["issuer"] = decode_X509_NAME (libssl_handle.X509_get_issuer_name (certificate))

                    decoded ["version"] = libssl_handle.X509_get_version (certificate) + 1

                    def print_ASN1_TIME (time: types.ASN1_TIME_ptr):
                        time_bio = libssl_handle.MemoryBIO ()
                        try:
                            if libssl_handle.ASN1_TIME_print (time_bio.bio, time) == 0:
                                raise Exception (f"failed to print ASN1 time: {_get_libssl_error_str ()}")

                            return time_bio.get_mem_data ().decode ()
                        finally:
                            del time_bio

                    decoded ["notBefore"] = print_ASN1_TIME (libssl_handle.X509_get0_notBefore (certificate))
                    decoded ["notAfter"] = print_ASN1_TIME (libssl_handle.X509_get0_notAfter (certificate))

                    serial_number_bio = libssl_handle.MemoryBIO ()
                    try:
                        libssl_handle.i2a_ASN1_INTEGER (serial_number_bio.bio, libssl_handle.X509_get_serialNumber (certificate))
                        decoded ["serialNumber"] = serial_number_bio.get_mem_data ().decode ()
                    finally:
                        del serial_number_bio

                    return decoded
        finally:
            libssl_handle.X509_free (certificate)
    def write (self, data: bytes):
        write_ret = libssl_handle.SSL_write (self.ssl, data, len (data))
        if write_ret <= 0: raise Exception ("failed to write to ssl object")
        if write_ret < len (data): raise Exception (f"only wrote {write_ret}/{len (data)} bytes to ssl object")
    def read (self, count: int) -> bytes:
        out = (ctypes.c_ubyte * count) ()
        read_ret = libssl_handle.SSL_read (self.ssl, ctypes.cast (out, ctypes.c_void_p), count)
        if read_ret < 0: raise Exception ("failed to read from ssl object")
        return bytes (out) [:read_ret]
    def close (self):
        shutdown_ret = libssl_handle.SSL_shutdown (self.ssl)
        if shutdown_ret < 0: raise Exception ("failed to shutdown ssl object")
    def __del__ (self):
        libssl_handle.SSL_free (self.ssl)
    def _get_error (self, source_error_code: int) -> str:
        error_code = libssl_handle.SSL_get_error (self.ssl, source_error_code)
        if error_code in [types.SSL_ERROR_SSL, types.SSL_ERROR_SYSCALL]:
            return _get_libssl_error_str ()
        else:
            return types.ssl_error_to_str (error_code)