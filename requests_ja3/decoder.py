from typing import Optional, Union, List
import hashlib
import copy
import dataclasses

Value = int
default_field_delimiter = ','
default_value_delimiter = '-'

@dataclasses.dataclass
class JA3:
    ssl_version: Value
    accepted_ciphers: list [Value]
    list_of_extensions: list [Value]
    elliptic_curve: Optional [list [Value]]
    elliptic_curve_point_format: Optional [list [Value]]
    @staticmethod
    def from_string (source_string: str, field_delimiter = default_field_delimiter, value_delimiter = default_value_delimiter) -> "JA3":
        def parse_list (_list: str) -> list [Value]: return list (map (int, _list.split (value_delimiter)))
        raw_fields = source_string.split (field_delimiter)
        raw_ssl_version, raw_accepted_ciphers, raw_list_of_extensions, raw_elliptic_curve, raw_elliptic_curve_point_format = tuple (raw_fields)

        list_of_extensions = parse_list (raw_list_of_extensions)

        return JA3 (
            ssl_version = int (raw_ssl_version),
            accepted_ciphers = parse_list (raw_accepted_ciphers),
            list_of_extensions = list_of_extensions,
            elliptic_curve = parse_list (raw_elliptic_curve) if 10 in list_of_extensions else None,
            elliptic_curve_point_format = parse_list (raw_elliptic_curve_point_format) if 11 in list_of_extensions else None
        )
    def to_string (self, field_delimiter = default_field_delimiter, value_delimiter = default_value_delimiter) -> str:
        def stringify_list (_list: list [Value]) -> str: return value_delimiter.join (map (str, _list))
        return field_delimiter.join ((
            str (self.ssl_version),
            stringify_list (self.accepted_ciphers),
            stringify_list (self.list_of_extensions),
            stringify_list (self.elliptic_curve) if self.elliptic_curve is not None else "",
            stringify_list (self.elliptic_curve_point_format) if self.elliptic_curve_point_format is not None else ""
        ))
    def to_hash (self) -> str:
        return hashlib.md5 (self.to_string ().encode ()).hexdigest ()
    def compare_to (self: "JA3", reference: "JA3", lenient: bool) -> bool:
        try:
            assert self == reference
            return True
        except AssertionError:
            if not lenient: return False
            self_lenient = copy.copy (self)
            self_lenient.elliptic_curve = None
            self_lenient.elliptic_curve_point_format = None
            reference_lenient = copy.copy (reference)
            reference_lenient.elliptic_curve = None
            reference_lenient.elliptic_curve_point_format = None
            assert self_lenient == reference_lenient
            return True
    def print_comparison_with (self: "JA3", reference: "JA3") -> bool:
        for _field_name in (
            "ssl_version", "accepted_ciphers", "list_of_extensions", "elliptic_curve", "elliptic_curve_point_format"
        ):
            if getattr (self, _field_name) == getattr (reference, _field_name):
                print (f"{_field_name} matches")
            else:
                print (f"{_field_name} doesn't match ({getattr (self, _field_name)} vs {getattr (reference, _field_name)})")
                if _field_name in ("list_of_extensions", "elliptic_curve, elliptic_curve_point_format"):
                    self_list = getattr (self, _field_name)
                    ref_list = getattr (reference, _field_name)
                    missing = set (ref_list) - set (self_list)
                    if len (missing) > 0: print (f"--> missing: {missing}")
                    extra = set (self_list) - set (ref_list)
                    if len (extra) > 0: print (f"--> extra: {extra}")
        if self.compare_to (reference, lenient = False):
            print ("MATCHES")
            return True
        elif self.compare_to (reference, lenient = True):
            print ("MATCHES (lenient)")
            return True
        else:
            print ("DOESN'T MATCH")
            return False
    def __repr__ (self) -> str:
        return f"<JA3 str={self.to_string ()} hash={self.to_hash ()}>"
