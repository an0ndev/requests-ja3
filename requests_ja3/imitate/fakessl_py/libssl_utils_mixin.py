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
    @staticmethod
    def stack_iterator (libssl_handle, stack_ptr):
        inner_ptr_type = type (stack_ptr).inner
        inner_ptr_type_name = type (stack_ptr).inner_name
        for item_index in range (
            getattr (libssl_handle, f"sk_{inner_ptr_type_name}_num") (stack_ptr)
        ):
            yield getattr (libssl_handle, f"sk_{inner_ptr_type_name}_value") (stack_ptr, item_index)
    @staticmethod
    def cipher_ids_from_stack (libssl_handle, cipher_stack: types.STACK_OF_SSL_CIPHER_ptr) -> list [int]:
        cipher_ids = [
            libssl_handle.SSL_CIPHER_get_protocol_id (cipher)
            for cipher in libssl_handle.stack_iterator (cipher_stack)
        ]
        return cipher_ids