from . import libssl_type_bindings as types

class MacrosMixin:
    @staticmethod
    def SSL_set_tlsext_host_name (libssl_handle, s, name):
        return libssl_handle.SSL_ctrl (s, types.SSL_CTRL_SET_TLSEXT_HOSTNAME, types.TLSEXT_NAMETYPE_host_name, name)