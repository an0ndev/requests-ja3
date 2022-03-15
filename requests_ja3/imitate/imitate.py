import importlib, importlib.util, importlib.machinery
import os
import shutil
import tempfile
import types
import zipfile
import subprocess

import requests

# import cppimport, cppimport.importer, cppimport.templating, cppimport.build_module

from requests_ja3.decoder import Decoder
from requests_ja3.imitate.verify import verify_fakessl
from requests_ja3.imitate.test import test_any_ssl

import pathlib

def generate_imitation_libssl (ja3_str: str, use_in_tree_libssl: bool = False, verify_against_real_ssl: bool = False) -> types.ModuleType:
    # ja3 = Decoder.decode (ja3_str)
    # print (ja3)

    libssl_path, openssl_temp_dir = _compile_libssl (use_in_tree_libssl = use_in_tree_libssl)

    import requests_ja3.imitate.fakessl_py as fakessl
    fakessl.initialize (libssl_path, openssl_temp_dir)

    # local_1 = "bruh lol"
    # ssl_socket = fakessl.SSLContext.wrap_socket (local_1)
    # print (ssl_socket)

    if verify_against_real_ssl: verify_fakessl (fakessl)

    test_any_ssl (fakessl)

    return fakessl

def _compile_libssl (use_in_tree_libssl: bool) -> (pathlib.Path, tempfile.TemporaryDirectory):
    working_dir = tempfile.TemporaryDirectory ()

    try:
        working_dir_path = pathlib.Path (working_dir.name)
        if use_in_tree_libssl:
            openssl_src_latest_base_name = "openssl"
            openssl_src_path = pathlib.Path (__file__).parent / openssl_src_latest_base_name
        else:
            openssl_src_branch_name = "OpenSSL_1_1_1-stable"
            openssl_src_latest_base_name = f"openssl-{openssl_src_branch_name}"
            openssl_src_zip_name = f"{openssl_src_latest_base_name}.zip"
            openssl_src_zip_path = working_dir_path / openssl_src_zip_name
            openssl_src_path = working_dir_path / openssl_src_latest_base_name

            openssl_src_url = f"https://github.com/an0ndev/openssl/archive/refs/heads/{openssl_src_branch_name}.zip"
            openssl_src_resp = requests.get (openssl_src_url)
            openssl_src_resp.raise_for_status ()
            with open (openssl_src_zip_path, "wb+") as openssl_src_zip_file:
                openssl_src_zip_file.write (openssl_src_resp.content)

            openssl_src_tar = zipfile.ZipFile (openssl_src_zip_path)
            openssl_src_tar.extractall (working_dir_path)

        def quiet_exec_in_src (*args):
            popen = subprocess.Popen (args, cwd = openssl_src_path, stderr = subprocess.PIPE, stdout = subprocess.PIPE)
            return_code = popen.wait ()
            if return_code != 0:
                stdout_data, stderr_data = popen.communicate ()
                raise Exception (stderr_data.decode ())

        quiet_exec_in_src ("/usr/bin/chmod", "+x", "config")
        quiet_exec_in_src ("/usr/bin/chmod", "+x", "Configure")
        quiet_exec_in_src ("/usr/bin/bash", "config", "no-ssl2", "no-ssl3")
        quiet_exec_in_src ("/usr/bin/make", f"-j{os.cpu_count ()}")

        libssl_archive_path = openssl_src_path / "libssl.a"
        libcrypto_archive_path = openssl_src_path / "libcrypto.a"
        libcrypto_and_ssl_path = openssl_src_path / "libcrypto_and_ssl.so"

        # ugly hack to prioritize usage of symbols from compiled libcrypto:
        # combine symbols from compiled libcrypto and libssl into one single shared library
        quiet_exec_in_src ("/usr/bin/gcc", "-shared", "-o", str (libcrypto_and_ssl_path), "-Wl,--whole-archive", str (libcrypto_archive_path), str (libssl_archive_path), "-Wl,--no-whole-archive")

        return libcrypto_and_ssl_path, working_dir
    except:
        working_dir.cleanup ()
        raise
