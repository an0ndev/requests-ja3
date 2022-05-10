from requests_ja3.imitate.imitate import generate_imitation_libssl
from requests_ja3.imitate.test_server import JA3Fetcher

fakessl = generate_imitation_libssl (
    None,
    use_in_tree_libssl = True
)

ja3, user_agent = JA3Fetcher (fakessl).fetch ()

print (f"JA3: {ja3}")
print (f"Reported user agent: {user_agent}")