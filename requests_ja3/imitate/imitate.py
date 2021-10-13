import importlib, importlib.util, importlib.machinery
import os
import shutil
import tempfile
import types

import cppimport, cppimport.importer, cppimport.templating, cppimport.build_module

from requests_ja3.decoder import Decoder
from requests_ja3.imitate.test import test_any_ssl

import requests_ja3.imitate.fakessl_py as fakessl_py

import pathlib

# noinspection PyUnresolvedReferences
def generate_imitation_libssl (ja3_str: str) -> types.ModuleType:
    # ja3 = Decoder.decode (ja3_str)
    # print (ja3)

    # fakessl = _compile_fakessl_extension ()
    fakessl = fakessl_py

    # local_1 = "bruh lol"
    # ssl_socket = fakessl.SSLContext.wrap_socket (local_1)
    # print (ssl_socket)

    test_any_ssl (fakessl)

    return fakessl

def _compile_fakessl_extension () -> types.ModuleType:
    with tempfile.TemporaryDirectory () as working_dir_str:
        working_dir = pathlib.Path (working_dir_str)
        imitate_py_dir = pathlib.Path (os.path.dirname (__file__))

        shutil.copytree (imitate_py_dir / "fakessl", working_dir / "fakessl")

        module_data = cppimport.importer.setup_module_data ("fakessl", str (working_dir / "fakessl" / "fakessl.cpp"))
        cppimport.templating.run_templating (module_data)

        cfg = module_data ["cfg"]
        cfg ["libraries"] = ["ssl", "crypto"]
        extra_compile_args: list = cfg ["extra_compile_args"]
        # extra_compile_args.append ("-lssl -lcrypto")
        # extra_compile_args.append ("-DTEST")
        extra_compile_args.append ("-O0")

        cppimport.build_module.build_module (module_data)

        spec = importlib.util.spec_from_file_location ("fakessl", module_data ["ext_path"])
        fakessl = importlib.util.module_from_spec (spec)

    return fakessl
