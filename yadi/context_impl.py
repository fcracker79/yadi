import typing

from yadi import bean_factories
from yadi.context import Context, Scope, SINGLETON, PROTOTYPE


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

    def get_bean(self, key: typing.Union[str, type]):
        if not isinstance(key, str):
            key = bean_factories.bean_name_from_type(key)

        scope_name = self._bean_scopes[key]
        if not scope_name:
            return None
        result = self._scopes[scope_name].get(key)
        if not result:
            result = self._object_factories[key](self)
            for cur_key in bean_factories.get_all_keys_from_type(type(result)):
                self._scopes[scope_name].set(cur_key, result)
            self._scopes[scope_name].set(key, result)
        return result


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
