import subprocess
from typing import Dict, List

SSLCipherNumber = int
SSLCipherName = str

class SSLUtils:
    @staticmethod
    def get_cipher_names () -> Dict [SSLCipherNumber, SSLCipherName]:
        out = {}

        cipher_list_str = subprocess.run ("openssl ciphers -V ALL", shell = True, stdout = subprocess.PIPE).stdout.decode ().replace ("\r", "")
        if cipher_list_str.endswith ("\n"):
            cipher_list_str = cipher_list_str [:-(len ("\n"))]
        cipher_lines = map (lambda _str: _str.strip (), cipher_list_str.split ('\n'))
        for cipher_line in cipher_lines:
            cipher_line = cipher_line.replace (" - ", " ")
            while "  " in cipher_line:
                cipher_line = cipher_line.replace ("  ", " ")
            number_as_str, name, protocol_version, key_exchange, authentication, encryption, mac_algorithms = tuple (cipher_line.split (' '))
            number_first_byte_with_hex_prefix, number_second_byte_with_hex_prefix = number_as_str.split (',')
            assert all (map (lambda byte: byte.startswith ("0x"), (number_first_byte_with_hex_prefix, number_second_byte_with_hex_prefix)))
            number_first_byte_str, number_second_byte_str = tuple (map (lambda byte: byte [len ("0x"):], (number_first_byte_with_hex_prefix, number_second_byte_with_hex_prefix)))
            number_first_byte, number_second_byte = tuple (map (lambda byte: int (byte, 16), (number_first_byte_str, number_second_byte_str)))
            number_bytes = bytes ([number_first_byte, number_second_byte])
            number = int.from_bytes (number_bytes, byteorder = "big", signed = False)
            out [number] = name

        out_sorted = {number: out [number] for number in sorted (list (out.keys ()))}
        for number, name in out_sorted.items (): print (f"{number}: {name}")
        return out_sorted
    @staticmethod
    def cipher_numbers_to_string (cipher_numbers: List [SSLCipherNumber]) -> str:
        cipher_names = SSLUtils.get_cipher_names ().copy ()
        selected = ':'.join (cipher_names [cipher_number] for cipher_number in cipher_numbers)
        for cipher_number in cipher_numbers: del cipher_names [cipher_number]
        rejected = ':'.join (f"!{cipher_names [cipher_number]}" for cipher_number in cipher_names.keys ())
        print (f"selected {selected}")
        print (f"rejected {rejected}")
        return f"{selected}:{rejected}"
