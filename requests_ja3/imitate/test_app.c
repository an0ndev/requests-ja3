#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>

#include <openssl/ssl.h>
#include <openssl/err.h>

#include <stdio.h>
#include <unistd.h>

int main () {
    printf ("start of main\n");
    char domain_name [] = "google.com";

    struct addrinfo hints = {
        .ai_flags = 0,
        .ai_family = AF_INET,
        .ai_socktype = SOCK_STREAM,
        .ai_protocol = 0,
        .ai_flags = 0
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
    if (inet_ntop (AF_INET, &(address.sin_addr), (void*) &inet_ntop_result, INET_ADDRSTRLEN) == NULL) {
        perror ("failed to convert address to text form");
        return EXIT_FAILURE;
    }
    printf ("address for domain name %s: %s\n", domain_name, inet_ntop_result);

    address.sin_port = htons (443);
    int clientSocket = socket (AF_INET, SOCK_STREAM, 0);
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
    if (writeReturnValue < ((sizeof http_request) - 1)) {
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
