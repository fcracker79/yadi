import typing

from yadi.context import Context


def bean_name_from_type(object_type):
    return '{}/{}'.format(object_type.__module__, object_type.__name__)


def get_all_keys_from_type(object_type) -> typing.Iterable[str]:
    yield from (bean_name_from_type(x) for x in _get_all_subtypes(object_type))


def _get_all_subtypes(object_type) -> typing.Iterable[type]:
    yield object_type
    for supertype in object_type.__bases__:
        yield from _get_all_subtypes(supertype)


def recursive_create(object_type: type):
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
