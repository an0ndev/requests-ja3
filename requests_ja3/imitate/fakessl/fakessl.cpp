#include "test_no_ssl.hpp"
#include "SSLSocket.hpp"
#include "SSLContext.hpp"

namespace py = pybind11;

PYBIND11_MODULE (fakessl, module) {
    module.def ("test_no_ssl", &test_no_ssl);
    module.def ("test_ssl", &test_ssl);
    py::class_ <SSLSocket> (module, "SSLSocket")
        .def ("connect", &SSLSocket::connect);
    py::class_ <SSLContext> (module, "SSLContext")
        .def (py::init <> ())
        .def ("wrap_socket", &SSLContext::wrap_socket);
}

/*
<%
cfg ["parallel"] = True
cfg ["sources"] = ["test_no_ssl.cpp", "SSLSocket.cpp", "SSLContext.cpp"]
setup_pybind11 (cfg)
%>
*/