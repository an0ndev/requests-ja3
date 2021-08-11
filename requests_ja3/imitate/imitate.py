import os
import tempfile

from requests_ja3.decoder import Decoder

import pathlib

def generate_imitation_libssl (ja3_str: str) -> pathlib.Path:
    ja3 = Decoder.decode (ja3_str)
    print (ja3)

    with tempfile.TemporaryDirectory () as working_dir_str:
        working_dir = pathlib.Path (working_dir_str)
        test_app_base_file_name = "test_app"
        test_app_file_name = f"{test_app_base_file_name}.c"
        print ("compiling")
        assert os.system (f"gcc {pathlib.Path (os.path.dirname (__file__))/test_app_file_name} -lssl -lcrypto -o {working_dir/test_app_base_file_name}") == 0
        print ("compiled, running")
        assert os.system (working_dir/test_app_base_file_name) == 0
