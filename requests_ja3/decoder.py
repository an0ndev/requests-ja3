from typing import Optional, Union, List
import hashlib
import copy

Value = int
class JA3:
    field_delimiter = ','
    value_delimiter = '-'
    def __init__ (
            self,
            ssl_version: Value,
            accepted_ciphers: list [Value],
            list_of_extensions: list [Value],
            elliptic_curve: Optional [list [Value]],
            elliptic_curve_point_format: Optional [list [Value]]
    ):
        self.ssl_version = ssl_version
        self.accepted_ciphers = accepted_ciphers
        self.list_of_extensions = list_of_extensions
        self.elliptic_curve = elliptic_curve
        self.elliptic_curve_point_format = elliptic_curve_point_format
    @staticmethod
    def from_string (source_string: str) -> "JA3":
        def parse_list (_list: str) -> list [Value]: return list (map (int, _list.split (JA3.value_delimiter)))
        raw_fields = source_string.split (JA3.field_delimiter)
        raw_ssl_version, raw_accepted_ciphers, raw_list_of_extensions, raw_elliptic_curve, raw_elliptic_curve_point_format = tuple (raw_fields)
        ssl_version = int (raw_ssl_version)
        accepted_ciphers = parse_list (raw_accepted_ciphers)
        list_of_extensions = parse_list (raw_list_of_extensions)
        elliptic_curve = parse_list (raw_elliptic_curve) if 10 in list_of_extensions else None
        elliptic_curve_point_format = parse_list (raw_elliptic_curve_point_format) if 11 in list_of_extensions else None
        return JA3 (
            ssl_version = ssl_version,
            accepted_ciphers = accepted_ciphers,
            list_of_extensions = list_of_extensions,
            elliptic_curve = elliptic_curve,
            elliptic_curve_point_format = elliptic_curve_point_format
        )
    def to_string (self) -> str:
        def stringify_list (_list: list [Value]) -> str: return JA3.value_delimiter.join (map (str, _list))
        return JA3.field_delimiter.join ((
            str (self.ssl_version),
            stringify_list (self.accepted_ciphers),
            stringify_list (self.list_of_extensions),
            stringify_list (self.elliptic_curve) if self.elliptic_curve is not None else "",
            stringify_list (self.elliptic_curve_point_format) if self.elliptic_curve_point_format is not None else ""
        ))
    def to_hash (self) -> str:
        return hashlib.md5 (self.to_string ().encode ()).hexdigest ()
    def compare_to (self: "JA3", rhs: "JA3", lenient: bool) -> bool:
        try:
            assert self == rhs
            return True
        except AssertionError:
            if not lenient: return False
            lhs_lenient = copy.copy (self)
            lhs_lenient.elliptic_curve = None
            lhs_lenient.elliptic_curve_point_format = None
            rhs_lenient = copy.copy (rhs)
            rhs_lenient.elliptic_curve = None
            rhs_lenient.elliptic_curve_point_format = None
            assert lhs_lenient == rhs_lenient
            return True
    def print_comparison_with (self: "JA3", rhs: "JA3") -> bool:
        for _field_name in (
            "ssl_version", "accepted_ciphers", "list_of_extensions", "elliptic_curve", "elliptic_curve_point_format"
        ):
            if getattr (self, _field_name) == getattr (rhs, _field_name):
                print (f"{_field_name} matches")
            else:
                print (f"{_field_name} doesn't match ({getattr (self, _field_name)} vs {getattr (rhs, _field_name)})")
        if self.compare_to (rhs, lenient = False):
            print ("MATCHES")
            return True
        elif self.compare_to (rhs, lenient = True):
            print ("MATCHES (lenient)")
            return True
        else:
            print ("DOESN'T MATCH")
            return False
    def __repr__ (self) -> str:
        return f"<JA3 str={self.to_string ()} hash={self.to_hash ()}>"
