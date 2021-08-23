#define PY_SSIZE_T_CLEAN
#include <Python.h>

static unsigned long increment (unsigned long input) {
    return input + 1;
}
static PyObject* pyincrement (PyObject* self, PyObject* input) {
    unsigned long as_unsigned_long = PyLong_AsUnsignedLong (input);
    if (PyErr_Occurred ()) return NULL;
    unsigned long output = increment (as_unsigned_long);
    return PyLong_FromUnsignedLong (output);
}


PyMethodDef fakessl_methods [] = {
    {
        .ml_name = "increment",
        .ml_meth = (PyCFunction) pyincrement,
        .ml_flags = METH_O,
        .ml_doc = NULL
    },
    {NULL}
};

PyModuleDef fakessl_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "fakessl",
    .m_doc = NULL,
    .m_size = -1,
    .m_methods = fakessl_methods,
    .m_slots = NULL,
    .m_traverse = NULL,
    .m_clear = NULL,
    .m_free = NULL
};

PyMODINIT_FUNC PyInit_fakessl () {
    return PyModule_Create (&fakessl_module);
}