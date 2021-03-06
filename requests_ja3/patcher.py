import ssl
from typing import Callable

# for type annotations
import requests as _clean_requests
import requests.sessions as _clean_requests_sessions
import requests.adapters as _clean_requests_adapters
import urllib3.poolmanager as _clean_urllib3_poolmanager
import urllib3.connectionpool as _clean_urllib3_connectionpool
import urllib3.connection as _clean_urllib3_connection
import urllib3.util.ssl_ as _clean_urllib3_util_ssl
import urllib3.util.ssltransport as _clean_urllib3_util_ssltransport

from requests_ja3.decoder import JA3
from requests_ja3.imitate.test_server import AsyncJA3Fetcher
from requests_ja3.patcher_utils import _module_from_class, _wrap
from requests_ja3.ssl_utils import SSLUtils
from requests_ja3.imitate.imitate import generate_imitation_libssl

class Patcher:
    @staticmethod
    def patch (src_requests_module: type (_clean_requests), target_ja3: JA3):
        # def ssl_wrap_socket_hook (*args, **kwargs):
        #     print (f"ssl_wrap_socket called with args {args} kwargs {kwargs}")
        #     return args, kwargs
        # Patcher._inner_patch (src_requests_module, ssl_wrap_socket_hook)
        fakessl = generate_imitation_libssl (target_ja3)
        Patcher._inner_patch (src_requests_module, fakessl)
    @staticmethod
    def check (requests_module: type (_clean_requests), target_ja3: JA3):
        fetcher_ja3 = generate_imitation_libssl(None)
        ja3_fetcher = AsyncJA3Fetcher (fetcher_ja3)
        ja3_fetcher.start ()

        try:
            real_ja3 = JA3.from_string (requests_module.get ("https://localhost:8443/json").json () ["ja3"])
        except:
            ja3_fetcher.cancel ()
            raise

        ja3_fetcher.join ()
        ja3_fetcher.fetch ()

        assert real_ja3.print_comparison_with(target_ja3)
    @staticmethod
    def _inner_patch (src_requests_module: type (_clean_requests), fakessl: type (ssl)):
        src_session_class = src_requests_module.Session
        # src_session_class.request = _wrap (src_session_class.request, "Session.request")
        src_sessions_module: type (_clean_requests_sessions) = _module_from_class (src_session_class)
        src_adapters_module: type (_clean_requests_adapters) = _module_from_class (src_sessions_module.HTTPAdapter)
        src_poolmanager_module: type (_clean_urllib3_poolmanager) = _module_from_class (src_adapters_module.PoolManager)
        src_connectionpool_module: type (_clean_urllib3_connectionpool) = _module_from_class (src_poolmanager_module.HTTPSConnectionPool)
        src_connection_module: type (_clean_urllib3_connection) = _module_from_class (src_connectionpool_module.HTTPSConnection)
        src_util_ssl_module: type (_clean_urllib3_util_ssl) = _module_from_class (src_connection_module.create_urllib3_context)
        print (src_util_ssl_module)

        src_util_ssl_module.ssl = fakessl

        # https://github.com/urllib3/urllib3/blob/main/src/urllib3/util/ssl_.py#L99
        direct_import_object_names_from_native_ssl = [
            "CERT_REQUIRED",
            "HAS_NEVER_CHECK_COMMON_NAME",
            "HAS_SNI",
            "OP_NO_COMPRESSION",
            "OP_NO_TICKET",
            "OPENSSL_VERSION",
            "OPENSSL_VERSION_NUMBER",
            "PROTOCOL_TLS",
            "PROTOCOL_TLS_CLIENT",
            "OP_NO_SSLv2",
            "OP_NO_SSLv3",
            "SSLContext",
            "TLSVersion",
        ]
        for object_name in direct_import_object_names_from_native_ssl: setattr (
            src_util_ssl_module,
            object_name,
            getattr (fakessl, object_name)
        )

        if src_util_ssl_module.SSLTransport is not None:
            src_util_ssltransport_module: type (_clean_urllib3_util_ssltransport) = _module_from_class (src_util_ssl_module.SSLTransport)
            src_util_ssltransport_module.ssl = fakessl

        """
        src_httpadapter_class: _clean_requests_sessions.HTTPAdapter = src_sessions_module.HTTPAdapter
        def get_connection_hook (connection_pool: _clean_HTTPSConnectionPool):
            def _make_request_hook (connection: _clean_VerifiedHTTPSConnection, *args, **kwargs):
                src_connection_module: type (_clean_urllib3_connection) = _module_from_class (connection.__class__)
                src_connection_module.ssl_wrap_socket = _wrap (src_connection_module.ssl_wrap_socket, "urllib3.util.ssl_.ssl_wrap_socket", pre_hook = ssl_wrap_socket_hook)
                return (connection, *args), kwargs
            connection_pool._make_request = _wrap (connection_pool._make_request, "HTTPSConnectionPool._make_request", pre_hook = _make_request_hook)
            return connection_pool
        src_httpadapter_class.get_connection = _wrap (src_httpadapter_class.get_connection, "HTTPAdapter.get_connection", post_hook = get_connection_hook)
        """