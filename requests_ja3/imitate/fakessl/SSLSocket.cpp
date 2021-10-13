#include "SSLSocket.hpp"
#include "SSLContext.hpp"
#include "test_no_ssl.hpp"

SSLSocket::SSLSocket (py::object sock_, SSLContext & context_) : sock (sock_), context (context_) {
    if (!py::isinstance (sock, py::module_::import ("socket").attr ("socket"))) {
        throw std::invalid_argument ("A socket or socket-like object is required");
    }

    fd = sock.attr ("fileno") ().cast <int> ();

    ssl = SSL_new (context.context);
    if (ssl == NULL) throw std::runtime_error ("failed to create SSL object");

    printf ("socket file descriptor: %d\n", fd);
    if (SSL_set_fd (ssl, fd) < 1) {
        SSL_free (ssl);
        throw std::runtime_error ("failed to set SSL file descriptor");
    }
};

void SSLSocket::connect (py::tuple address) {
    printf ("C++ calling connect\n");
    sock.attr ("connect") (address);
    printf ("C++ called connect\n");
    printf ("calling test_post_connect\n");
    test_post_connect (fd, context.context, ssl);
    printf ("called test_post_connect\n");
    if (ssl == nullptr) throw std::runtime_error ("SSL is nullptr?");
    printf ("ssl: %lu\n", (unsigned long) ssl);
    if (SSL_connect (ssl) < 1) {
        printf ("SSL_connect failed\n");
        throw std::runtime_error ("SSL_connect failed");
    }
    printf ("done with connect\n");
};

SSLSocket::~SSLSocket () {
    SSL_free (ssl);
};