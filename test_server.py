from requests_ja3.imitate.imitate import generate_imitation_libssl
from requests_ja3.imitate.test_server import ja3_server_from_any_ssl
from requests_ja3.hasher import Hasher

fakessl = generate_imitation_libssl (
    None,
    use_in_tree_libssl = True
)

ja3, ja3_str, ja3_hash, user_agent = ja3_server_from_any_ssl (fakessl)

print (f"JA3: {ja3}")
print (f"JA3 string: {ja3_str}")
print (f"JA3 hash: {ja3_hash}")
print (f"Reported user agent: {user_agent}")