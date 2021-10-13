#pragma once

#include <pybind11/pybind11.h>
namespace py = pybind11;

#include <openssl/ssl.h>
#include <openssl/err.h>

class SSLContext;

class SSLSocket {
    py::object sock;
    SSLContext & context;
    int fd;
    SSL* ssl;
public:
    SSLSocket (py::object sock_, SSLContext & context_);
    void connect (py::tuple address);
    ~SSLSocket ();
};
