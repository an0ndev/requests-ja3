import ctypes
import typing
import pathlib

from . import libssl_type_bindings as types

def get_bound_libssl (libssl_path: pathlib.Path) -> (ctypes.CDLL, list [typing.Callable]):
    libssl_handle = ctypes.cdll.LoadLibrary (str (libssl_path))
    binder_time_mixin_methods = []

    def _setup_method (method_name: str, argtypes: list, restype: typing.Any):
        method = getattr (libssl_handle, method_name)
        method.argtypes = argtypes
        method.restype = restype
    _s_m = _setup_method

    _s_m ("BIO_s_mem", [], types.BIO_method_ptr)
    _s_m ("BIO_new", [types.BIO_method_ptr], types.BIO_ptr)
    # _s_m ("BIO_get_mem_data", [types.BIO_ptr, ctypes.POINTER (ctypes.c_char_p)], ctypes.c_long)
    _s_m ("BIO_ctrl", [types.BIO_ptr, ctypes.c_int, ctypes.c_long, ctypes.c_void_p], ctypes.c_long)
    _s_m ("BIO_free", [types.BIO_ptr], None)

    _s_m ("TLS_client_method", [], types.SSL_METHOD_ptr)
    _s_m ("TLS_server_method", [], types.SSL_METHOD_ptr)

    _s_m ("SSL_CTX_new", [], types.SSL_CTX_ptr)
    _s_m ("SSL_CTX_set_cipher_list", [types.SSL_CTX_ptr, ctypes.c_char_p], ctypes.c_int)
    _s_m ("SSL_CTX_load_verify_locations", [types.SSL_CTX_ptr, ctypes.c_char_p, ctypes.c_char_p], ctypes.c_int)
    _s_m ("SSL_CTX_use_certificate_chain_file", [types.SSL_CTX_ptr, ctypes.c_char_p], ctypes.c_int)
    _s_m ("SSL_CTX_use_PrivateKey_file", [types.SSL_CTX_ptr, ctypes.c_char_p, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_CTX_ctrl", [types.SSL_CTX_ptr, ctypes.c_int, ctypes.c_long, ctypes.c_void_p], ctypes.c_long)
    _s_m ("SSL_CTX_set_alpn_protos", [types.SSL_CTX_ptr, ctypes.c_char_p, ctypes.c_uint], ctypes.c_int)
    _s_m ("SSL_CTX_enable_ct", [types.SSL_CTX_ptr, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_CTX_set_options", [types.SSL_CTX_ptr, ctypes.c_ulong], ctypes.c_ulong)
    _s_m ("SSL_CTX_free", [types.SSL_CTX_ptr], None)

    _s_m ("SSL_CIPHER_find", [types.SSL_ptr, ctypes.POINTER (ctypes.c_ubyte)], types.SSL_CIPHER_ptr)
    _s_m ("SSL_CIPHER_get_protocol_id", [types.SSL_CIPHER_ptr], ctypes.c_int32)

    def define_cast_mixin_method (target_name: str, method_name: str, dest_arg_types, dest_ret_type):
        def cast_mixin_method (_libssl_handle, *src_args):
            assert len (src_args) == len (dest_arg_types)
            dest_args = []
            for src_arg, dest_arg_type in zip (src_args, dest_arg_types):
                if type (src_arg) == dest_arg_type:
                    dest_args.append (src_arg)
                else:
                    dest_args.append (
                        ctypes.cast (src_arg, dest_arg_type)
                    )
            src_ret = getattr (_libssl_handle, target_name) (*dest_args)
            if type (src_ret) == dest_ret_type:
                return src_ret
            else:
                return ctypes.cast (src_ret, dest_ret_type)
        cast_mixin_method.__name__ = method_name
        binder_time_mixin_methods.append (cast_mixin_method)
    d_c_m_m = define_cast_mixin_method

    generic_stack_class = types.OPENSSL_STACK_ptr
    generic_inner_class = ctypes.c_void_p
    def define_stack_funcs (specific_stack_class: type (ctypes.c_void_p), specific_inner_class: type (ctypes.c_void_p), class_name: str):
        compare_function_class = getattr (types, f"sk_{class_name}_compfunc")
        copy_function_class = getattr (types, f"sk_{class_name}_copyfunc")
        free_function_class = getattr (types, f"sk_{class_name}_freefunc")

        d_c_m_m ("OPENSSL_sk_num", f"sk_{class_name}_num", [generic_stack_class], int)
        d_c_m_m ("OPENSSL_sk_value", f"sk_{class_name}_value", [generic_stack_class, int], specific_inner_class)
        d_c_m_m ("OPENSSL_sk_delete_ptr", f"sk_{class_name}_delete_ptr", [generic_stack_class, generic_inner_class], specific_inner_class)
        return
        _s_m (f"sk_{class_name}_new", [compare_function_class], generic_stack_class)
        _s_m (f"sk_{class_name}_new_null", [], generic_stack_class)
        _s_m (f"sk_{class_name}_reserve", [generic_stack_class, ctypes.c_int], ctypes.c_int)
        _s_m (f"sk_{class_name}_free", [generic_stack_class], None)
        _s_m (f"sk_{class_name}_zero", [generic_stack_class], None)
        _s_m (f"sk_{class_name}_delete", [generic_stack_class, ctypes.c_int], generic_inner_class)
        _s_m (f"sk_{class_name}_push", [generic_stack_class, generic_inner_class], ctypes.c_int)
        _s_m (f"sk_{class_name}_unshift", [generic_stack_class, generic_inner_class], ctypes.c_int)
        _s_m (f"sk_{class_name}_pop", [generic_stack_class], generic_inner_class)
        _s_m (f"sk_{class_name}_shift", [generic_stack_class], generic_inner_class)
        _s_m (f"sk_{class_name}_pop_free", [generic_stack_class, free_function_class], None)
        _s_m (f"sk_{class_name}_insert", [generic_stack_class, generic_inner_class, ctypes.c_int], ctypes.c_int)
        _s_m (f"sk_{class_name}_set", [generic_stack_class, ctypes.c_int, generic_inner_class], generic_inner_class)
        _s_m (f"sk_{class_name}_find", [generic_stack_class, generic_inner_class], ctypes.c_int)
        _s_m (f"sk_{class_name}_find_ex", [generic_stack_class, generic_inner_class], ctypes.c_int)
        _s_m (f"sk_{class_name}_sort", [generic_stack_class], None)
        _s_m (f"sk_{class_name}_is_sorted", [generic_stack_class], ctypes.c_int)
        _s_m (f"sk_{class_name}_dup", [generic_stack_class], generic_stack_class)
        _s_m (f"sk_{class_name}_deep_copy", [generic_stack_class, copy_function_class, free_function_class], generic_stack_class)
        _s_m (f"sk_{class_name}_set_cmp_func", [generic_stack_class, compare_function_class], compare_function_class)
        _s_m (f"sk_{class_name}_new_reserve", [compare_function_class, ctypes.c_int], generic_stack_class)
    define_stack_funcs (types.STACK_OF_SSL_CIPHER_ptr, types.SSL_CIPHER_ptr, "SSL_CIPHER")
    _s_m (f"OPENSSL_sk_num", [generic_stack_class], ctypes.c_int)
    _s_m (f"OPENSSL_sk_value", [generic_stack_class, ctypes.c_int], generic_inner_class)
    _s_m (f"OPENSSL_sk_new", [types.OPENSSL_sk_compfunc], generic_stack_class)
    _s_m (f"OPENSSL_sk_new_null", [], generic_stack_class)
    _s_m (f"OPENSSL_sk_reserve", [generic_stack_class, ctypes.c_int], ctypes.c_int)
    _s_m (f"OPENSSL_sk_free", [generic_stack_class], None)
    _s_m (f"OPENSSL_sk_zero", [generic_stack_class], None)
    _s_m (f"OPENSSL_sk_delete", [generic_stack_class, ctypes.c_int], generic_inner_class)
    _s_m (f"OPENSSL_sk_delete_ptr", [generic_stack_class, generic_inner_class], generic_inner_class)
    _s_m (f"OPENSSL_sk_push", [generic_stack_class, generic_inner_class], ctypes.c_int)
    _s_m (f"OPENSSL_sk_unshift", [generic_stack_class, generic_inner_class], ctypes.c_int)
    _s_m (f"OPENSSL_sk_pop", [generic_stack_class], generic_inner_class)
    _s_m (f"OPENSSL_sk_shift", [generic_stack_class], generic_inner_class)
    _s_m (f"OPENSSL_sk_pop_free", [generic_stack_class, types.OPENSSL_sk_freefunc], None)
    _s_m (f"OPENSSL_sk_insert", [generic_stack_class, generic_inner_class, ctypes.c_int], ctypes.c_int)
    _s_m (f"OPENSSL_sk_set", [generic_stack_class, ctypes.c_int, generic_inner_class], generic_inner_class)
    _s_m (f"OPENSSL_sk_find", [generic_stack_class, generic_inner_class], ctypes.c_int)
    _s_m (f"OPENSSL_sk_find_ex", [generic_stack_class, generic_inner_class], ctypes.c_int)
    _s_m (f"OPENSSL_sk_sort", [generic_stack_class], None)
    _s_m (f"OPENSSL_sk_is_sorted", [generic_stack_class], ctypes.c_int)
    _s_m (f"OPENSSL_sk_dup", [generic_stack_class], generic_stack_class)
    _s_m (f"OPENSSL_sk_deep_copy", [generic_stack_class, types.OPENSSL_sk_copyfunc, types.OPENSSL_sk_freefunc], generic_stack_class)
    _s_m (f"OPENSSL_sk_set_cmp_func", [generic_stack_class, types.OPENSSL_sk_compfunc], types.OPENSSL_sk_compfunc)
    _s_m (f"OPENSSL_sk_new_reserve", [types.OPENSSL_sk_compfunc, ctypes.c_int], generic_stack_class)

    _s_m ("SSL_new", [types.SSL_CTX_ptr], types.SSL_ptr)
    _s_m ("SSL_get_error", [types.SSL_ptr, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_set_fd", [types.SSL_ptr, ctypes.c_int], ctypes.c_int)
    # _s_m ("SSL_set_tlsext_host_name", [types.SSL_ptr, ctypes.c_char_p], ctypes.c_int)
    _s_m ("SSL_ctrl", [types.SSL_ptr, ctypes.c_int, ctypes.c_long, ctypes.c_void_p], ctypes.c_long)
    _s_m ("SSL_connect", [types.SSL_ptr], ctypes.c_int)
    _s_m ("SSL_get_ciphers", [types.SSL_ptr], types.STACK_OF_SSL_CIPHER_ptr)
    _s_m ("SSL_get1_supported_ciphers", [types.SSL_ptr], types.STACK_OF_SSL_CIPHER_ptr)
    _s_m ("SSL_get_verify_result", [types.SSL_ptr], ctypes.c_long)
    _s_m ("SSL_get_peer_certificate", [types.SSL_ptr], types.X509_ptr)
    _s_m ("SSL_write", [types.SSL_ptr, ctypes.c_void_p, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_read", [types.SSL_ptr, ctypes.c_void_p, ctypes.c_int], ctypes.c_int)
    _s_m ("SSL_shutdown", [types.SSL_ptr], ctypes.c_int)
    _s_m ("FAKESSL_SSL_get_ja3", [types.SSL_ptr], ctypes.c_void_p)
    _s_m ("SSL_free", [types.SSL_ptr], None)

    _s_m ("i2d_X509", [types.X509_ptr, ctypes.POINTER (ctypes.POINTER (ctypes.c_ubyte))], ctypes.c_int)
    _s_m ("X509_get_subject_name", [types.X509_ptr], types.X509_NAME_ptr)
    _s_m ("X509_get_issuer_name", [types.X509_ptr], types.X509_NAME_ptr)
    _s_m ("X509_get_version", [types.X509_ptr], ctypes.c_int)
    _s_m ("X509_get0_notBefore", [types.X509_ptr], types.ASN1_TIME_ptr)
    _s_m ("X509_get0_notAfter", [types.X509_ptr], types.ASN1_TIME_ptr)
    _s_m ("X509_get_serialNumber", [types.X509_ptr], types.ASN1_INTEGER_ptr)
    _s_m ("X509_free", [types.X509_ptr], None)

    _s_m ("X509_NAME_entry_count", [types.X509_NAME_ptr], ctypes.c_int)
    _s_m ("X509_NAME_get_entry", [types.X509_NAME_ptr, ctypes.c_int], types.X509_NAME_ENTRY_ptr)

    _s_m ("X509_NAME_ENTRY_get_object", [types.X509_NAME_ENTRY_ptr], types.ASN1_OBJECT_ptr)
    _s_m ("X509_NAME_ENTRY_get_data", [types.X509_NAME_ENTRY_ptr], types.ASN1_STRING_ptr)

    _s_m ("OBJ_obj2txt", [ctypes.c_char_p, ctypes.c_int, types.ASN1_OBJECT_ptr, ctypes.c_int], ctypes.c_int)
    _s_m ("OBJ_obj2nid", [types.ASN1_OBJECT_ptr], ctypes.c_int)
    _s_m ("OBJ_nid2ln", [ctypes.c_int], ctypes.c_char_p)

    _s_m ("ASN1_STRING_length", [types.ASN1_STRING_ptr], ctypes.c_int)
    _s_m ("ASN1_STRING_data", [types.ASN1_STRING_ptr], ctypes.c_char_p)

    _s_m ("ASN1_TIME_print", [types.BIO_ptr, types.ASN1_TIME_ptr], ctypes.c_int)

    _s_m ("i2a_ASN1_INTEGER", [types.BIO_ptr, types.ASN1_INTEGER_ptr], ctypes.c_int)

    _s_m ("ERR_print_errors_cb", [types.ERR_print_errors_cb_callback, ctypes.c_void_p], None)

    _s_m ("CRYPTO_free", [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int], None)

    return libssl_handle, binder_time_mixin_methods
