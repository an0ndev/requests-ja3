#include "SSLContext.hpp"
#include "SSLSocket.hpp"

SSLContext::SSLContext () {
    context = SSL_CTX_new (TLS_client_method ());
    if (context == NULL) throw std::runtime_error ("failed to create SSL context");
};

SSLSocket SSLContext::wrap_socket (py::object sock) {
    return SSLSocket (sock, *this);
};

SSLContext::~SSLContext () {
    SSL_CTX_free (context);
};