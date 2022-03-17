from requests_ja3.monitor.monitor import SingleJA3Yoinker
import requests_ja3.decoder as decoder

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
api_ja3 = decoder.Decoder.decode (api_response.json () ["ja3"])
pprint_ja3 (api_ja3)
print ("")
print (f"{sep} YOINKED JA3 {sep}")
yoinked_ja3 = decoder.Decoder.decode (yoinked_response.string_ja3)
pprint_ja3 (yoinked_ja3)
print ("")

decoder.print_comparison (api_ja3, yoinked_ja3)