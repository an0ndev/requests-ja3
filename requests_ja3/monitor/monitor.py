import dataclasses
import hashlib
import threading
from typing import Optional, List

from .utils import ensure_root
ensure_root ()

from scapy.layers.l2 import Ether
from scapy.layers.tls.all import *
from scapy.sendrecv import AsyncSniffer

@dataclasses.dataclass
class JA3Result:
    server_names: Optional [List [str]]
    string_ja3: str
    md5_ja3: str

class SingleJA3Yoinker:
    def __init__ (self, interface: str, server_name: Optional [str] = None):
        self.server_name = server_name

        self.ja3_result: Optional [JA3Result] = None
        self.ja3_ready_event = threading.Event ()
        self.sniffer = AsyncSniffer (prn = self._packet_handler, store = False, iface = interface)
        self.sniffer.start ()
    def yoink (self) -> JA3Result:
        self.ja3_ready_event.wait ()
        return self.ja3_result
    def _packet_handler (self, packet: Ether):
        if self.ja3_ready_event.is_set (): return

        summary = packet.summary ()
        if "TLS Handshake - Client Hello" not in summary: return
        tls_layer: TLS = packet [TLS]
        self.ja3_result = self._ja3_from_tls_client_hello (tls_layer.msg [0])
        if self.ja3_result is None: return
        self.sniffer.stop (join = False)
        self.ja3_ready_event.set ()
    def _ja3_from_tls_client_hello (self, tls_client_hello: TLSClientHello) -> Optional [JA3Result]:
        field_delimiter = ','
        value_delimiter = '-'
        out_fields = []

        try:
            tls_client_hello.version
        except KeyError:
            print (f"aye wtf, you sure this is a client hello? {type (tls_client_hello)}")
            raise

        # def print_field (field_name): print (f"{field_name} {tls_client_hello.fields [field_name]}")
        # for field in ("version", "ciphers", "ext"): print_field (field)
        grease_values = [(base << 8) | base for base in [0xA | (upper_bit << 4) for upper_bit in range (16)]]

        # SSL Version
        out_fields.append (str (tls_client_hello.version))

        # Cipher
        out_ciphers = []
        for cipher in tls_client_hello.ciphers:
            if cipher in grease_values: continue
            out_ciphers.append (str (cipher))
        out_fields.append (value_delimiter.join (out_ciphers))

        # SSL Extension
        out_extensions = []
        ec_extension = None
        ec_formats_extension = None

        server_names = None

        for extension in tls_client_hello.ext:
            if extension.name == "TLS Extension - Server Name":
                server_names = list (server_name.servername.decode () for server_name in extension.fields ['servernames'])
                if self.server_name not in server_names: return
            extension_type = extension.type
            if extension_type in grease_values: continue
            # if extension_type == 0x15: continue # "Padding"
            if extension.name == "TLS Extension - Scapy Unknown":
                print (f"WARNING: unknown extension {extension.type}, not adding to signature")
                continue
            out_extensions.append (str (extension.type))
            if extension.type == 10: # "Supported Groups"
                ec_extension = extension
            elif extension.type == 11: # "EC Point Formats"
                ec_formats_extension = extension
        out_fields.append (value_delimiter.join (out_extensions))

        if server_names is None and self.server_name is not None: return

        # Elliptic Curve
        if ec_extension is not None:
            out_groups = []
            for group in ec_extension.fields ["groups"]:
                if group in grease_values: continue
                out_groups.append (str (group))
            out_fields.append (value_delimiter.join (out_groups))
        else: out_fields.append ("")

        # Elliptic Curve Point Format
        if ec_formats_extension is not None:
            out_fields.append (value_delimiter.join (str (point_format) for point_format in ec_formats_extension.fields ["ecpl"]))
        else: out_fields.append ("")

        string_ja3 = field_delimiter.join (out_fields)
        md5_ja3 = hashlib.md5 (string_ja3.encode ()).hexdigest ()
        return JA3Result (server_names, string_ja3, md5_ja3)
