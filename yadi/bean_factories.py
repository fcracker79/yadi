import inspect
import itertools
import typing
from collections import OrderedDict
from types import FunctionType

from yadi.context import Context
from yadi.listeners import LifecycleObjectListener


def bean_name_from_type(object_type):
    return '{}/{}'.format(object_type.__module__, object_type.__name__)


def get_all_keys_from_type(object_type) -> typing.Iterable[str]:
    yield from (bean_name_from_type(x) for x in _get_all_subtypes(object_type))


class _ScopedProxy:
    def __init__(self, context: Context, bean_name: str):
        self._context = context
        self._bean_name = bean_name

    def __getattr__(self, item):
        if item in ('_context', '_bean_name'):
            return super(_ScopedProxy, self).__getattr__(item)
        return getattr(self._context.get_bean(self._bean_name), item)


def _get_all_subtypes(object_type) -> typing.Iterable[type]:
    if not hasattr(object_type, '__bases__'):
        return
    yield object_type
    for supertype in object_type.__bases__:
        yield from _get_all_subtypes(supertype)


def recursive_create(object_type: type, scope: str, listener: LifecycleObjectListener):
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

            current_scope = context.scope(scope)

            for param, arg_type in object_type.__init__.__annotations__.items():
                bean_name = arg_type.__yadi__
                bean_scope = context.bean_scope(bean_name)
                if current_scope.level < bean_scope.level:
                    bean_instance = _ScopedProxy(context, bean_name)
                else:
                    bean_instance = context.get_bean(bean_name)
                args[param] = bean_instance
            result = object_type(**args)
            listener.on_create(result)
            return result
    return _inner
