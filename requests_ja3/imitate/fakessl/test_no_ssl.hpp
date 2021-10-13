#pragma once

#include <openssl/ssl.h>

#include <pybind11/pybind11.h>
namespace py = pybind11;

void test_no_ssl (py::object sock);

int test_ssl (py::object sock);

int test_post_connect (int fd, SSL_CTX* context, SSL* connection);