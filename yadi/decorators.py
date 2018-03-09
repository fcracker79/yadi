import typing

from yadi import bean_factories
from yadi.context import SINGLETON
from yadi.context_impl import DEFAULT_CONTEXT
from yadi.types import bean_name_from_type


def get_all_keys_from_type(object_type) -> typing.Iterable[str]:
    yield from (bean_name_from_type(x) for x in _get_all_subtypes(object_type))


def _get_all_subtypes(object_type) -> typing.Iterable[type]:
    yield object_type
    for supertype in object_type.__bases__:
        yield from _get_all_subtypes(supertype)


def inject(scope_name=SINGLETON, context=DEFAULT_CONTEXT, name=None):
    def _outer(object_type):
        if name:
            names = (name, )
        else:
            names = get_all_keys_from_type(object_type)

        bean = bean_factories.recursive_create(object_type)
        for cur_name in names:
            context.register_bean(cur_name, bean, scope_name)
        return object_type
    return _outer
