from requests_ja3.imitate.imitate import generate_imitation_libssl
import requests_ja3.decoder as decoder
from requests_ja3.imitate.test import ja3_from_any_ssl

target_ja3 = decoder.Decoder.decode ("771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27,,") # b32309a26951912be7dba376398abc3b
print (target_ja3)

fakessl = generate_imitation_libssl (
    target_ja3,
    use_in_tree_libssl = True
)

ja3_from_test = ja3_from_any_ssl (fakessl)

assert decoder.print_comparison (target_ja3, ja3_from_test)
