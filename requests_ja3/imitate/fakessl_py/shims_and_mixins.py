import typing

class ListWrapperMixin:
    def __init__ (self, mixin_methods: list [typing.Callable]):
        self.mixin_methods = mixin_methods
    def __getattr__ (self, item):
        for mixin_method in self.mixin_methods:
            if mixin_method.__name__ == item: return mixin_method
        raise AttributeError (item)

class ShimmedModule:
    def __init__ (self, src_module):
        self.src_module = src_module
        self.mixin_classes = []
    def __getattr__ (self, item):
        should_pass_src_module = False
        for mixin_class in self.mixin_classes:
            try:
                mixin_item = getattr (mixin_class, item)
            except AttributeError:
                continue
            should_pass_src_module = True
            src_method = mixin_item
            break
        else:
            src_method = getattr (self.src_module, item)

        assert isinstance (src_method, typing.Callable)
        def wrapper_method (*args, **kwargs):
            if should_pass_src_module: args = [self, *args]
            pretty_args = ", ".join (map (str, args [1:] if should_pass_src_module else args))
            pretty_kwargs = ", ".join (f"{kwarg_name} = {str (kwarg_value)}" for kwarg_name, kwarg_value in kwargs.items ())
            # print (f"{item} ({pretty_args}{f', {pretty_kwargs}' if pretty_kwargs != '' else ''}) -> ", end = "")

            ret = src_method (*args, **kwargs)

            # print (ret)
            return ret
        return wrapper_method
    def shim_apply_mixin (self, mixin_class):
        self.mixin_classes.append (mixin_class)
    def shim_apply_list_mixin (self, mixin_list):
        self.mixin_classes.append (ListWrapperMixin (mixin_list))

def shim_module (src_module):
    return ShimmedModule (src_module)
