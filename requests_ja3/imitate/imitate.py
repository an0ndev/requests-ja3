import importlib, importlib.util, importlib.machinery
import os
import shutil
import tempfile
import types
import zipfile
import subprocess
import typing

import requests

# import cppimport, cppimport.importer, cppimport.templating, cppimport.build_module

import requests_ja3.decoder as decoder
from requests_ja3.imitate.verify import verify_fakessl

import pathlib

def generate_imitation_libssl (target_ja3: typing.Optional [decoder.JA3], use_in_tree_libssl: bool = False, verify_against_real_ssl: bool = False) -> types.ModuleType:
    libssl_path, openssl_temp_dir = _compile_libssl (target_ja3, use_in_tree_libssl = use_in_tree_libssl)

    import requests_ja3.imitate.fakessl_py as fakessl
    fakessl.initialize (libssl_path, openssl_temp_dir, target_ja3)

    # local_1 = "bruh lol"
    # ssl_socket = fakessl.SSLContext.wrap_socket (local_1)
    # print (ssl_socket)

    if verify_against_real_ssl: verify_fakessl (fakessl)

    return fakessl

def _compile_libssl (target_ja3: typing.Optional [decoder.JA3], use_in_tree_libssl: bool) -> (pathlib.Path, tempfile.TemporaryDirectory):
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
            stdout_data, stderr_data = popen.communicate ()
            stderr_str = stderr_data.decode ()
            if "warning" in stderr_str:
                print (f"--- COMPILER WARNINGS ---\n{stderr_str}--- END COMPILER WARNINGS ---")
            if popen.returncode != 0:
                raise Exception (stderr_str)

        quiet_exec_in_src ("/usr/bin/make", "clean")

        quiet_exec_in_src ("/usr/bin/chmod", "+x", "config")
        quiet_exec_in_src ("/usr/bin/chmod", "+x", "Configure")
        config_options = ["no-ssl2", "no-ssl3", "zlib"]
        if target_ja3 is not None:
            if 0xFF in target_ja3.accepted_ciphers:
                config_options.append ("-DFAKESSL_RFC5746_AS_CIPHER")
            if 65281 in target_ja3.list_of_extensions:
                config_options.append ("-DFAKESSL_RFC5746_AS_EXTENSION")
            if target_ja3.elliptic_curve is None:
                config_options.append ("-DFAKESSL_DISABLE_ECC")
        quiet_exec_in_src ("/usr/bin/bash", "config", *config_options)
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
