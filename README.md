# requests-ja3

Modifying Python's `requests` module to spoof a ja3 fingerprint

(Since the repo seems to be getting some external attention, I want to clarify that this is experimental and not currently in a working state. Thank you!)

### TO-DO LIST
- [x] `decoder`: parse string version of ja3
- [x] `patcher`: find and replace usages of ssl module in an imported `requests` module
- [x] `monitor`: dump ja3 off network using scapy
  - some inconsistency here? some fields don't seem to match ja3 reported by ja3er
  - not sure how to further debug this, client hello packet data from wireshark matches scapy
- [x] `server`: dump ja3 server-side with customized openssl
  - the cause for the ^ inconsistency with ja3er is because the last two fields (extension info) aren't used by tls 1.3
  - this server dumps the field values despite the extensions going unused
- [ ] `imitate`: fake ssl module with customizable ja3
    - [x] ~~dummy C extension with setup.py and portable compiler setup~~
    - [x] ~~dummy pybind11 + cppimport extension~~ **(moved to ctypes)**
    - [ ] ~~ability to verify fakessl against real ssl module~~ can't inspect pybind11 method signatures yet
    - [x] dummy SSLSocket class
    - [x] customized openssl compile options
    - [x] linkage against C extension
    - [x] usage of compiled openssl in SSLSocket class
    - [x] `ssl.wrap_socket` at minimum
    - [ ] other `ssl` functions used by requests/urllib3
- [ ] tests using ja3s from common browsers
  - [x] brave browser (works!)
  - [ ] firefox (segfaults)
- [ ] `patcher`: patch fakessl into a requests module
  - [ ] patch the module
  - [ ] automatically test the patched module against a local server

**progress (5/13/22):**
- all fields are customized
- I implemented the compressed certificate extension in my fork of OpenSSL, so that works
- Most other extensions are enabled automatically
- server (for dumping ja3) works, with solutions for ja3er's flaws
- can imitate brave browser's fingerprint successfully!!!
- need to sort segfault when imitating firefox, and finish code for patching a requests module

### REFERENCES
JA3 specification: [https://github.com/salesforce/ja3/blob/master/README.md](https://github.com/salesforce/ja3/blob/master/README.md)