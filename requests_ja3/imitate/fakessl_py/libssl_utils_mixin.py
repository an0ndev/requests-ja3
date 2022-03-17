import ctypes
from . import libssl_type_bindings as types

class MemoryBIO:
    def __init__ (self, libssl_handle):
        self.libssl_handle = libssl_handle
        self.bio = self.libssl_handle.BIO_new (self.libssl_handle.BIO_s_mem ())
        assert self.bio is not None
    def get_mem_data (self) -> bytes:
        data_pointer = ctypes.POINTER (ctypes.c_ubyte) ()
        data_len = self.libssl_handle.BIO_get_mem_data (self.bio, ctypes.byref (data_pointer))
        return ctypes.string_at (data_pointer, data_len)
    def __del__ (self):
        self.libssl_handle.BIO_free (self.bio)

class UtilsMixin:
    @staticmethod
    def MemoryBIO (libssl_handle) -> MemoryBIO: return MemoryBIO (libssl_handle)
