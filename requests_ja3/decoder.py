from typing import Optional, Union, List

JA3 = dict

class Decoder:
    # written according to https://github.com/salesforce/ja3/blob/master/README.md
    class InvalidJA3Exception (Exception): pass

    field_descriptions = [ # each item is tuple (name (str), can_have_multiple_values (bool), is_optional (bool))
        ("ssl_version", False, False),
        ("accepted_ciphers", True, False),
        ("list_of_extensions", True, True),
        ("elliptic_curve", True, True),
        ("elliptic_curve_point_format", True, True)
    ]
    field_delimiter = ','
    value_delimiter = '-'
    @staticmethod
    def decode (ja3_str: str) -> JA3:
        out = {}
        field_sources = ja3_str.split (Decoder.field_delimiter)

        if len (Decoder.field_descriptions) != len (field_sources):
            raise Decoder.InvalidJA3Exception (f"invalid number of fields (spec needs {len (Decoder.field_descriptions)} but given JA3 has {len (field_sources)})")

        for field_name, field_can_have_multiple_values, field_is_optional in Decoder.field_descriptions:
            field_source = field_sources.pop (0)

            field_values = field_source.split (Decoder.value_delimiter)
            if len (field_values) == 1 and field_values [0] == '': field_values = []
            field_values = list (map (int, field_values))

            field_out: Optional [Union [int, List [int]]]
            if len (field_values) == 0:
                if field_is_optional: field_out = None
                else: raise Decoder.InvalidJA3Exception (f"non-optional field {field_name} is empty")
            elif len (field_values) > 1:
                if field_can_have_multiple_values:
                    field_values.sort ()
                    field_out = field_values
                else: raise Decoder.InvalidJA3Exception (f"non-multiple-value field {field_name} has multiple values {field_values}")
            else: field_out = field_values [0]

            out [field_name] = field_out

        return out

def compare (lhs: JA3, rhs: JA3, lenient: bool) -> bool:
    try:
        assert lhs == rhs
        return True
    except AssertionError:
        if not lenient: return False
        lhs_lenient = lhs.copy ()
        del lhs_lenient ["elliptic_curve"]
        del lhs_lenient ["elliptic_curve_point_format"]
        rhs_lenient = rhs.copy ()
        del rhs_lenient ["elliptic_curve"]
        del rhs_lenient ["elliptic_curve_point_format"]
        assert lhs_lenient == rhs_lenient
        return True

def print_comparison (lhs: JA3, rhs: JA3) -> bool:
    for _field_name in lhs.keys ():
        if lhs [_field_name] == rhs [_field_name]:
            print (f"{_field_name} matches")
        else:
            print (f"{_field_name} doesn't match ({lhs [_field_name]} vs {rhs [_field_name]})")
    if compare (lhs, rhs, lenient = False):
        print ("MATCHES")
        return True
    elif compare (lhs, rhs, lenient = True):
        print ("MATCHES (lenient)")
        return True
    else:
        print ("DOESN'T MATCH")
        return False