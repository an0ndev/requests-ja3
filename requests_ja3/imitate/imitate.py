import importlib, importlib.util, importlib.machinery
import os
import shutil
import tempfile
import types

import cppimport, cppimport.importer

from requests_ja3.decoder import Decoder

import pathlib

# noinspection PyUnresolvedReferences
def generate_imitation_libssl (ja3_str: str):
    # ja3 = Decoder.decode (ja3_str)
    # print (ja3)

    fakessl = _compile_fakessl_extension ()
    print (fakessl.increment (n = 5))

def _compile_fakessl_extension () -> types.ModuleType:
    with tempfile.TemporaryDirectory () as working_dir_str:
        working_dir = pathlib.Path (working_dir_str)
        imitate_py_dir = pathlib.Path (os.path.dirname (__file__))

        shutil.copytree (imitate_py_dir / "fakessl", working_dir / "fakessl")

        file_path = str (working_dir / "fakessl" / "fakessl.cpp")
        module_data = cppimport.importer.setup_module_data ("fakessl", file_path)
        cppimport.importer.template_and_build (file_path, module_data)

        spec = importlib.util.spec_from_file_location ("fakessl", module_data ["ext_path"])
        fakessl = importlib.util.module_from_spec (spec)

    return fakessl
