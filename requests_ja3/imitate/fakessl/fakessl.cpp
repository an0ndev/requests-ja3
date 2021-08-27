#include <pybind11/pybind11.h>

long increment (long n) {
    return n + 1;
}

PYBIND11_MODULE (fakessl, module) {
    module.def ("increment", &increment, "Increments a number", pybind11::arg ("n"));
}

/*
<%
cfg ["parallel"] = True
setup_pybind11 (cfg)
%>
*/