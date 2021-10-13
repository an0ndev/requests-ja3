#pragma once

#include "SSLSocket.hpp"

#include <pybind11/pybind11.h>
namespace py = pybind11;

#include <openssl/ssl.h>
#include <openssl/err.h>

class SSLContext {
    SSL_CTX* context;

    friend SSLSocket;
public:
    SSLContext ();
    SSLSocket wrap_socket (py::object sock);
    ~SSLContext ();
};
