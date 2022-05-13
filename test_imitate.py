from requests_ja3.imitate.imitate import generate_imitation_libssl
import requests_ja3.decoder as decoder
from requests_ja3.imitate.test import ja3_from_any_ssl

target_ja3 = decoder.JA3.from_string ("771,4866-4867-4865-49196-49200-159-52393-52392-52394-49195-49199-158-49188-49192-107-49187-49191-103-49162-49172-57-49161-49171-51-157-156-61-60-53-47-255,0-11-10-35-22-23-13-43-45-51-21,29-23-30-25-24,0-1-2") # e1d8b
print (target_ja3)

fakessl = generate_imitation_libssl (
    target_ja3,
    use_in_tree_libssl = True
)

ja3_from_test, user_agent_from_test = ja3_from_any_ssl (fakessl)

assert ja3_from_test.print_comparison_with (target_ja3)

print ("PASSES IMITATION TEST")