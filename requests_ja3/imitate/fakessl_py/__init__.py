import pathlib
import tempfile

from . import libssl_binder
from . import SSLContext as SSLContext_module

from .shims_and_mixins import shim_module
from .libssl_macros_mixin import MacrosMixin
from .libssl_utils_mixin import UtilsMixin

from requests_ja3.decoder import JA3

libssl_handle = None
SSLContext = None
_openssl_temp_dir = None
target_ja3 = None
socket_exceptions = None

def initialize (libssl_path: pathlib.Path, openssl_temp_dir: tempfile.TemporaryDirectory, _target_ja3: JA3):
    global libssl_handle, SSLContext, socket_exceptions, _openssl_temp_dir, target_ja3

    unshimmed_libssl_handle, binder_time_mixin_methods = libssl_binder.get_bound_libssl (libssl_path)
    libssl_handle = shim_module (unshimmed_libssl_handle)
    libssl_handle.shim_apply_mixin (MacrosMixin)
    libssl_handle.shim_apply_mixin (UtilsMixin)
    libssl_handle.shim_apply_list_mixin (binder_time_mixin_methods)

    SSLContext_module.initialize (libssl_handle, _target_ja3)
    SSLContext = SSLContext_module.SSLContext

    socket_exceptions = SSLContext_module.socket_exceptions

    _openssl_temp_dir = openssl_temp_dir

    target_ja3 = _target_ja3

from .Options import Options, VerifyMode
for option_name in ["OP_NO_COMPRESSION", "OP_NO_TICKET", "OP_NO_SSLv2", "OP_NO_SSLv3", "OP_ALL"]:
    globals () [option_name] = getattr (Options, option_name)
for verify_mode_name in ["CERT_NONE", "CERT_OPTIONAL", "CERT_REQUIRED"]:
    globals () [verify_mode_name] = getattr (VerifyMode, verify_mode_name)

from .protocol_constants import *

import ssl as clean_ssl

for constant_name in [
    "HAS_NEVER_CHECK_COMMON_NAME",
    "HAS_SNI",
    "OPENSSL_VERSION",
    "OPENSSL_VERSION_NUMBER",
    "TLSVersion",
]:
    globals () [constant_name] = getattr (clean_ssl, constant_name)

# noinspection PyUnresolvedReferences
def create_default_context (purpose: Purpose = Purpose.SERVER_AUTH, cafile = None, capath = None, cadata = None) -> SSLContext:
    assert purpose in (Purpose.SERVER_AUTH, Purpose.CLIENT_AUTH)
    # noinspection PyCallingNonCallable
    context = SSLContext (PROTOCOL_TLS_CLIENT if purpose == Purpose.SERVER_AUTH else PROTOCOL_TLS_SERVER)
    if cafile is None and capath is None and cadata is None:
        context.load_default_certs (purpose = purpose)
    else:
        context.load_verify_locations (cafile, capath, cadata)
    return context
