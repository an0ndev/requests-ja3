#include "test_no_ssl.hpp"

#include <openssl/err.h>

#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>

sockaddr_in get_google_com_addr () {
    char domain_name [] = "google.com";

    addrinfo hints = {
        .ai_flags = 0,
        .ai_family = AF_INET,
        .ai_socktype = SOCK_STREAM,
        .ai_protocol = 0
    };
    addrinfo* addressInfo;
    int ret = getaddrinfo (domain_name, NULL, &hints, &addressInfo);
    if (ret < 0) {
        throw std::runtime_error ("failed to lookup domain name");
    }

    sockaddr_in address = *((sockaddr_in*) addressInfo->ai_addr);
    freeaddrinfo (addressInfo);

    return address;
};

void write_http_request (int connection) {
#define CRLF "\r\n"
    static char http_request [] = "GET / HTTP/1.1" CRLF "Host: google.com" CRLF "Connection: close" CRLF CRLF;

    int writeReturnValue = write (connection, http_request, (sizeof http_request) - 1);
    if (writeReturnValue < (int) ((sizeof http_request) - 1)) {
        if (writeReturnValue < 1) {
            throw std::runtime_error ("couldn't write to connection");
        } else {
            throw std::runtime_error ("couldn't write entire payload to connection");
        }
    }
};

void read_http_response (int connection) {
const unsigned int bufferSize = 256;
    char buffer [bufferSize];

    while (true) {
        int readReturnValue = read (connection, buffer, bufferSize);
        if (readReturnValue > 0) {
            fwrite (buffer, readReturnValue, 1, stdout);
        } else {
            if (readReturnValue == 0) {
                break;
            } else {
                throw std::runtime_error ("couldn't read from connection");
            }
        }
    }
};

void test_no_ssl (py::object sock) {
    printf ("aye\n");

    if (!py::isinstance (sock, py::module_::import ("socket").attr ("socket"))) {
        throw std::invalid_argument ("A socket or socket-like object is required");
    }

    int rawSock = sock.attr ("fileno") ().cast <int> ();
    printf ("raw socket file descriptor: %d\n", rawSock);

    sockaddr_in google_com_addr = get_google_com_addr ();
    google_com_addr.sin_port = htons (80);

    if (connect (rawSock, (sockaddr*) &google_com_addr, sizeof (google_com_addr)) < 0) {
        throw std::runtime_error ("couldn't connect");
    }

    write_http_request (rawSock);

    read_http_response (rawSock);

    shutdown (rawSock, SHUT_RDWR);
    close (rawSock);
};

int test_ssl (py::object sock) {
    int clientSocket = sock.attr ("fileno") ().cast <int> ();

    char domain_name [] = "google.com";

    struct addrinfo hints = {
        .ai_flags = 0,
        .ai_family = AF_INET,
        .ai_socktype = SOCK_STREAM,
        .ai_protocol = 0,
    };
    struct addrinfo* addressInfo;
    printf ("looking up domain name\n");
    int ret = getaddrinfo (domain_name, NULL, &hints, &addressInfo);
    if (ret < 0) {
        perror ("failed to lookup domain name");
        return EXIT_FAILURE;
    }

    struct sockaddr_in address = *((struct sockaddr_in*) addressInfo->ai_addr);
    freeaddrinfo (addressInfo);

    char inet_ntop_result [INET_ADDRSTRLEN];
    if (inet_ntop (AF_INET, &(address.sin_addr), (char*) &inet_ntop_result, INET_ADDRSTRLEN) == NULL) {
        perror ("failed to convert address to text form");
        return EXIT_FAILURE;
    }
    printf ("address for domain name %s: %s\n", domain_name, inet_ntop_result);

    address.sin_port = htons (443);
    if (connect (clientSocket, (struct sockaddr*) &address, sizeof (address)) < 0) {
        perror ("couldn't connect");
        return EXIT_FAILURE;
    }

    SSL_CTX* context = SSL_CTX_new (TLS_client_method ());
#define ssl_perror(inner) printf (inner ": %s\n", ERR_error_string (ERR_get_error (), NULL))
    if (context == NULL) {
        ssl_perror ("couldn't create context");
        return EXIT_FAILURE;
    }

    SSL* connection = SSL_new (context);
    if (connection == NULL) {
        ssl_perror ("couldn't create connection");
        SSL_CTX_free (context);
        return EXIT_FAILURE;
    }

    if (SSL_set_fd (connection, clientSocket) < 1) {
        ssl_perror ("couldn't set file descriptor");
        SSL_free (connection);
        SSL_CTX_free (context);
        return EXIT_FAILURE;
    }

    if (SSL_connect (connection) < 1) {
        ssl_perror ("couldn't prepare connection");
        SSL_free (connection);
        SSL_CTX_free (context);
        return EXIT_FAILURE;
    }

#define CRLF "\r\n"
    char http_request [] = "GET / HTTP/1.1" CRLF "Host: google.com" CRLF "Connection: close" CRLF CRLF;

    int writeReturnValue = SSL_write (connection, http_request, (sizeof http_request) - 1);
    if (writeReturnValue < (int) ((sizeof http_request) - 1)) {
        if (writeReturnValue < 1) {
            ssl_perror ("couldn't write to connection");
        } else {
            ssl_perror ("couldn't write entire payload to connection");
        }
        SSL_free (connection);
        SSL_CTX_free (context);
        return EXIT_FAILURE;
    }

    const unsigned int bufferSize = 256;
    char buffer [bufferSize];

    while (1) {
        int readReturnValue = SSL_read (connection, buffer, bufferSize);
        if (readReturnValue > 0) {
            fwrite (buffer, readReturnValue, 1, stdout);
        } else {
            if (readReturnValue == 0) {
                break;
            } else {
                ssl_perror ("couldn't read from connection");
                SSL_free (connection);
                SSL_CTX_free (context);
                return EXIT_FAILURE;
            }
        }
    }

    if (SSL_shutdown (connection) < 0) {
        ssl_perror ("couldn't shut down connection");
        SSL_free (connection);
        SSL_CTX_free (context);
        return EXIT_FAILURE;
    }

    SSL_free (connection);
    SSL_CTX_free (context);

    shutdown (clientSocket, SHUT_RDWR);
    close (clientSocket);

    return EXIT_SUCCESS;
}

int test_post_connect (int fd, SSL_CTX* context, SSL* connection) {
    if (SSL_connect (connection) < 1) {
        ssl_perror ("couldn't prepare connection");
        SSL_free (connection);
        SSL_CTX_free (context);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}