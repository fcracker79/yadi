import inspect
import itertools
import typing
from collections import OrderedDict
from types import FunctionType

from yadi.context import Context


def bean_name_from_type(object_type):
    return '{}/{}'.format(object_type.__module__, object_type.__name__)


def get_all_keys_from_type(object_type) -> typing.Iterable[str]:
    yield from (bean_name_from_type(x) for x in _get_all_subtypes(object_type))


def _get_all_subtypes(object_type) -> typing.Iterable[type]:
    if not hasattr(object_type, '__bases__'):
        return
    yield object_type
    for supertype in object_type.__bases__:
        yield from _get_all_subtypes(supertype)


def recursive_create(object_type: type):
    _EXTERNAL = object()
    if isinstance(object_type, FunctionType):
        arguments = OrderedDict()
        for param_name, param in inspect.signature(object_type).parameters.items():
            assert param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
            arguments[param_name] = \
                param.annotation.__yadi__ if hasattr(param.annotation, '__yadi__') \
                else _EXTERNAL

        def _create_args(context: Context, args: OrderedDict, *a, **kw) -> dict:
            result = {}
            a_idx = 0
            for param_name, param_marker in args.items():
                if param_marker is _EXTERNAL:
                    if param_name in kw:
                        value = kw[param_name]
                    else:
                        value = a[a_idx]
                        a_idx += 1
                else:
                    value = context.get_bean(param_marker)
                result[param_name] = value
            return result

        def _inner(context: Context) -> callable:
            def _inner_inner(*a, **kw):
                return object_type(
                    **_create_args(context, arguments, *a, **kw)
                )
            return _inner_inner
    else:
        def _inner(context: Context) -> object:
            args = {}
            if not hasattr(object_type.__init__, '__annotations__'):
                return object_type()

            for param, arg_type in object_type.__init__.__annotations__.items():
                bean_name = arg_type.__yadi__
                bean_instance = context.get_bean(bean_name)
                args[param] = bean_instance
            return object_type(**args)
    return _inner
