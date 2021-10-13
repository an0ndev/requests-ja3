import inspect
import ssl

import types
import typing
from typing import Optional

def verify_fakessl (fakessl_module: types.ModuleType) -> None:
    return _visit_node (node = fakessl_module, reference_root = ssl, node_name = "fakessl", is_root = True)

def _visit_node (node: object, reference_root: type (ssl), node_name: str, is_root: bool = False):
    # raise NotImplementedError ("broken until pybind11 adds support for inspect.signature from methods")

    def simple_visit_children ():
        for item_name in dir (node):
            if _name_is_builtin (item_name): continue
            print (item_name)
            _visit_node (getattr (node, item_name), reference_root, node_name = f"{node_name}.{item_name}", is_root = False)

    def find_reference_match () -> object:
        name_levels_with_module = node_name.split (".")
        assert name_levels_with_module [0] == "fakessl"
        sub_name_levels = name_levels_with_module [1:]
        topmost_item: object = reference_root
        for sub_name in sub_name_levels:
            topmost_item = getattr (topmost_item, sub_name)
        return topmost_item

    def type_name_is (_object: object, *reference_names: str) -> bool: return any (str (type (_object)) == f"<class '{reference_name}'>" for reference_name in reference_names)

    reference_match = find_reference_match ()
    print (f"REFERENCE MATCH TYPE {type (reference_match)}")
    if node == reference_match: return

    function_or_method_type_names = ["builtin_function_or_method", "function", "method"]

    if isinstance (node, types.ModuleType):
        if not is_root: return
        print (f"{node} is module")
        assert type_name_is (reference_match, "module")
        simple_visit_children ()
    elif type_name_is (node, "pybind11_builtins.pybind11_type"):
        print (f"{node} is pybind11 type")
        simple_visit_children ()
    elif type_name_is (node, "type"):
        print (f"{node} is python builtin type")
        simple_visit_children ()
    elif type_name_is (node, *function_or_method_type_names):
        print (f"{node} is builtin function or method")
        assert type_name_is (reference_match, *function_or_method_type_names)
        reference_method: typing.Callable = reference_match
        print (f"found ref method {reference_method}! comparing signature")
        reference_signature = inspect.signature (reference_method)
        print (f"our doc {node.__doc__}")
        print (f"our method dict {node.__dict__}")
        signature = inspect.signature (node)
        assert reference_signature == signature, f"ref sig {reference_signature} != {signature}"
    else:
        raise Exception (f"dont know what {node} (name {node_name}, type {type (node)}) is")

def _name_is_builtin (name: str) -> bool: return name.startswith ("__") and name.endswith ("__")