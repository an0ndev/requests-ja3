from requests_ja3 import decoder
from requests_ja3.patcher import Patcher
import requests

target_ja3 = decoder.JA3.from_string ("771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513-21,29-23-24,0") # cd08e31494f9531f560d64c695473da9
print (target_ja3)
Patcher.patch(requests, target_ja3)
Patcher.check(requests, target_ja3)