import requests

from requests_ja3.patcher import Patcher

target_ja3_str = "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27,,"
Patcher.patch (requests, target_ja3_str)
Patcher.check (requests, target_ja3_str)
