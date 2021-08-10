import functools
import sys
from typing import Callable, Optional

def _wrap (wrapped: Callable, name: str, pre_hook: Optional [Callable] = None, post_hook: Optional [Callable] = None):
    @functools.wraps (wrapped)
    def wrapper (*args, **kwargs):
        print (f"{name} called with args {args} and kwargs {kwargs}")
        args_after_hook, kwargs_after_hook = pre_hook (*args, **kwargs) if pre_hook is not None else (args, kwargs)
        wrapped_return_value = wrapped (*args_after_hook, **kwargs_after_hook)
        return post_hook (wrapped_return_value) if post_hook is not None else wrapped_return_value
    return wrapper
def _module_from_class (_class): return sys.modules [_class.__module__]
