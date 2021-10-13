import ctypes

from . import libssl_binder
libssl_handle = libssl_binder.get_bound_libssl ()

from . import SSLContext as SSLContext_module
SSLContext_module.initialize (libssl_handle)
SSLContext = SSLContext_module.SSLContext
