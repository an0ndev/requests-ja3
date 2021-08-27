# requests-ja3

Modifying Python's `requests` module to spoof a ja3 fingerprint

(Since the repo seems to be getting some external attention, I want to clarify that this is experimental and not currently in a working state. Thank you!)

### TO-DO LIST
- [x] `decoder`: parse string version of ja3
- [x] `patcher`: find and replace usages of ssl module in an imported `requests` module
- [x] `monitor`: dump ja3 off network using scapy
  - some inconsistency here? some fields don't seem to match ja3 reported by ja3er
  - not sure how to further debug this, client hello packet data from wireshark matches scapy
- [ ] `imitate`: fake ssl module with customizable ja3
    - [x] ~~dummy C extension with setup.py and portable compiler setup~~
    - [x] dummy pybind11 + cppimport extension
    - [ ] dummy SSLSocket class
    - [ ] customized openssl compile options + linkage against C extension
    - [ ] usage of compiled openssl in SSLSocket class
    - [ ] `ssl.wrap_socket` at minimum
    - [ ] other `ssl` functions used by requests/urllib3
- [ ] tests using ja3s from common browsers

### REFERENCES
JA3 specification: [https://github.com/salesforce/ja3/blob/master/README.md](https://github.com/salesforce/ja3/blob/master/README.md)