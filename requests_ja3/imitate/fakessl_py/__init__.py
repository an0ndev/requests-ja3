import pathlib
import tempfile

from . import libssl_binder
from . import SSLContext as SSLContext_module

from .shims_and_mixins import shim_module
from .libssl_macros_mixin import MacrosMixin

libssl_handle = None
SSLContext = None
_openssl_temp_dir = None

def initialize (libssl_path: pathlib.Path, openssl_temp_dir: tempfile.TemporaryDirectory):
    global libssl_handle, SSLContext, _openssl_temp_dir

    unshimmed_libssl_handle = libssl_binder.get_bound_libssl (libssl_path)
    libssl_handle = shim_module (unshimmed_libssl_handle)
    libssl_handle.shim_apply_mixin (MacrosMixin)

    SSLContext_module.initialize (libssl_handle)
    SSLContext = SSLContext_module.SSLContext

    _openssl_temp_dir = openssl_temp_dir

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
