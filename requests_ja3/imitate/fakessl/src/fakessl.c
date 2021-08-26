#define PY_SSIZE_T_CLEAN
#include <Python.h>

typedef struct {
    unsigned long call_count;
} FakeSSLData;

static long increment (long input) {
    return input + 1;
}
static PyObject* pyincrement (PyObject* fakessl_module, PyObject* args, PyObject* kwargs) {
    FakeSSLData* fakessl_data = PyModule_GetState (fakessl_module);
    if (fakessl_data == NULL) return NULL;
    (fakessl_data->call_count)++;
    printf ("%ld\n", fakessl_data->call_count);

    PyLongObject* long_object;
    static char* keywords [] = {"n", NULL};
    if (!PyArg_ParseTupleAndKeywords (args, kwargs, "O!:increment", (char **) &keywords, &PyLong_Type, &long_object)) return NULL;

    long long_raw = PyLong_AsLong ((PyObject*) long_object);
    if (PyErr_Occurred ()) return NULL;

    unsigned long output = increment (long_raw);

    return PyLong_FromLong (output);
}


PyMethodDef fakessl_method_defs [] = {
    {
        .ml_name = "increment",
        .ml_meth = (PyCFunction) pyincrement,
        .ml_flags = METH_VARARGS | METH_KEYWORDS,
        .ml_doc = NULL
    },
    {NULL}
};

PyModuleDef fakessl_module_def = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "fakessl",
    .m_doc = NULL,
    .m_size = sizeof (FakeSSLData),
    .m_methods = fakessl_method_defs,
    .m_slots = NULL,
    .m_traverse = NULL,
    .m_clear = NULL,
    .m_free = NULL
};

PyMODINIT_FUNC PyInit_fakessl () {
    return PyModule_Create (&fakessl_module_def);
}