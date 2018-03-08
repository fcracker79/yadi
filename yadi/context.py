import abc
import typing


class Scope(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def get(self, key: str) -> typing.Optional[object]:
        pass

    @abc.abstractmethod
    def set(self, key: str, obj: object):
        pass


class Context(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add_scope(self, scope: Scope):
        pass

    @abc.abstractmethod
    def register_bean(self, key: str, obj: object, scope_name: str):
        pass

    @abc.abstractmethod
    def get_bean(self, key: str) -> typing.Optional[object]:
        pass


class ScopeDelegationContext(Context):
    def __init__(self):
        self._object_factories = dict()  # type: typing.Dict[str, typing.Callable[[Context], object]]
        self._scopes = dict()  # type: typing.Dict[str, Scope]
        self._bean_scopes = dict()  # type: typing.Dict[str, str]

    def add_scope(self, scope: Scope):
        self._scopes[scope.name] = scope

    def register_bean(self, key: str, obj_factory: typing.Callable[[Context], object], scope_name: str):
        self._bean_scopes[key] = scope_name
        self._object_factories[key] = obj_factory

    def get_bean(self, key: str):
        scope_name = self._bean_scopes[key]
        if not scope_name:
            return None
        result = self._scopes[scope_name].get(key)
        if not result:
            self._scopes[scope_name] = result = self._object_factories[key](self)
        return result

SINGLETON = 'singleton'
PROTOTYPE = 'prototype'


class _SingletonScope(Scope):
    def __init__(self):
        self._beans = dict()

    @property
    def name(self) -> str:
        return SINGLETON

    def get(self, key: str) -> typing.Optional[object]:
        return self._beans.get(key)

    def set(self, key: str, obj: object):
        self._beans[key] = obj


class _PrototypeScope(Scope):
    @property
    def name(self):
        return PROTOTYPE

    def get(self, key: str):
        return None

    def set(self, key: str, obj: object):
        pass


class BaseScopesContext(ScopeDelegationContext):
    def __init__(self):
        super(BaseScopesContext, self).__init__()
        self.add_scope(_SingletonScope())
        self.add_scope(_PrototypeScope())


DEFAULT_CONTEXT = BaseScopesContext()
