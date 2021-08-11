from requests_ja3.monitor.monitor import SingleJA3Yoinker
from requests_ja3.decoder import Decoder

import requests

yoinker = SingleJA3Yoinker (interface = "wlp59s0", server_name = "ja3er.com")

api_response = requests.get ("https://ja3er.com/json")
yoinked_response = yoinker.yoink ()

def pprint_ja3 (ja3: dict):
    for field_name, field_value in ja3.items ():
        print (f"{field_name}: {field_value}")
sep = '-' * 5

print (f"{sep} API JA3 {sep}")
api_ja3 = Decoder.decode (api_response.json () ["ja3"])
pprint_ja3 (api_ja3)
print ("")
print (f"{sep} YOINKED JA3 {sep}")
yoinked_ja3 = Decoder.decode (yoinked_response.string_ja3)
pprint_ja3 (yoinked_ja3)
assert api_ja3 == yoinked_ja3
