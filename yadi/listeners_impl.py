import typing

from yadi import listeners
from yadi.bean_factories import _ScopedProxy


class FunctionAttributeLifeCycleListener(listeners.LifecycleObjectListener):
    def __init__(self, yadi_attribute: str):
        self._yadi_attribute = yadi_attribute
        self._cached_on_create_methods = dict()  # type: typing.Dict[type, typing.Set[str]]

    @classmethod
    def _type_from_instance(cls, bean) -> type:
        if isinstance(bean, _ScopedProxy):
            return type(bean._bean_name)
        return type(bean)

    def _compute_on_create_methods(self, bean) -> typing.Set[str]:
        result = set()
        for method_name in dir(bean):
            method = getattr(bean, method_name)
            if callable(method) and hasattr(method, self._yadi_attribute):
                result.add(method_name)
        return result

    def on_create(self, bean):
        bean_type = self._type_from_instance(bean)
        on_create_methods = self._cached_on_create_methods.get(bean_type)
        if on_create_methods is None:
            self._cached_on_create_methods[bean_type] = on_create_methods = \
                self._compute_on_create_methods(bean)

        for method_name in on_create_methods:
            getattr(bean, method_name)()
