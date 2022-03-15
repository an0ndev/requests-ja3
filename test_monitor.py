from requests_ja3.monitor.monitor import SingleJA3Yoinker
from requests_ja3.decoder import Decoder

import requests

yoinker = SingleJA3Yoinker (interface = "br0", server_name = "ja3er.com")

api_response = requests.get ("https://ja3er.com/json")
yoinked_response = yoinker.yoink ()

def pprint_ja3 (ja3: dict):
    for field_name, field_value in ja3.items ():
        print (f"{field_name}: {field_value}")
sep = '-' * 5

print (f"{sep} API JA3 {sep}")
print (api_response.json ())
api_ja3 = Decoder.decode (api_response.json () ["ja3"])
pprint_ja3 (api_ja3)
print ("")
print (f"{sep} YOINKED JA3 {sep}")
yoinked_ja3 = Decoder.decode (yoinked_response.string_ja3)
pprint_ja3 (yoinked_ja3)
print ("")
for _field_name in api_ja3.keys ():
    print (f"{_field_name} {'matches' if api_ja3 [_field_name] == yoinked_ja3 [_field_name] else 'doesnt match'}")
try:
    assert api_ja3 == yoinked_ja3
    print ("MATCHES")
except AssertionError:
    api_ja3_lenient = api_ja3.copy ()
    del api_ja3_lenient ["elliptic_curve"]
    del api_ja3_lenient ["elliptic_curve_point_format"]
    yoinked_ja3_lenient = yoinked_ja3.copy ()
    del yoinked_ja3_lenient ["elliptic_curve"]
    del yoinked_ja3_lenient ["elliptic_curve_point_format"]
    assert api_ja3_lenient == yoinked_ja3_lenient
    print ("MATCHES (lenient mode: excluding elliptic curve)")
