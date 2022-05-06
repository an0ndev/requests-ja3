import requests_ja3.decoder as decoder
import hashlib

class Hasher:
    fields = ["ssl_version", "accepted_ciphers", "list_of_extensions", "elliptic_curve", "elliptic_curve_point_format"]
    field_delimiter = ','
    value_delimiter = '-'
    @staticmethod
    def hash (ja3: decoder.JA3) -> str:
        field_values = []
        for field_name in Hasher.fields:
            field_value_src = ja3 [field_name]
            if isinstance (field_value_src, list):
                field_values.append (Hasher.value_delimiter.join (map (str, field_value_src)))
            else:
                field_values.append (str (field_value_src))
        ja3_str = Hasher.field_delimiter.join (field_values)
        print (ja3_str)
        return hashlib.md5 (ja3_str.encode ()).hexdigest ()