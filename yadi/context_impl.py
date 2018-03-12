import typing

from yadi import bean_factories, listeners, listeners_impl
from yadi.context import Context, Scope, SINGLETON, PROTOTYPE


class DelegationContext(Context):
    __slots__ = (
        '_object_factories',
        '_scopes',
        '_bean_scopes',
        '_aliases',
        '_post_create_listeners'
    )
    _TYPES_2_LIST = {
        listeners.LifecycleObjectListener: '_post_create_listeners'
    }

    def __init__(self):
        self._object_factories = dict()  # type: typing.Dict[str, typing.Callable[[Context], object]]
        self._scopes = dict()  # type: typing.Dict[str, Scope]
        self._bean_scopes = dict()  # type: typing.Dict[str, str]
        self._aliases = dict()  # type: typing.Dict[str, str]
        self._post_create_listeners = []  # type: typing.List[listeners.LifecycleObjectListener]

    def add_scope(self, scope: Scope):
        self._scopes[scope.name] = scope

    def register_bean(self, key: str, obj_factory: typing.Callable[[Context], object], object_type, scope: str):
        all_aliases = bean_factories.get_all_keys_from_type(object_type)
        if not key:
            all_aliases = list(all_aliases)
            key = all_aliases[0]
            all_aliases = all_aliases[1:]

        self._bean_scopes[key] = scope
        self._object_factories[key] = obj_factory
        for cur_key in all_aliases:
            self._aliases[cur_key] = key
        self._aliases[key] = key

    def _key_from_union(self, key: typing.Union[str, type, callable]) -> str:
        if isinstance(key, str):
            key = self._aliases[key]
        else:
            key = self._aliases[bean_factories.bean_name_from_type(key)]
        return key

    def get_bean(self, key: typing.Union[str, type, callable]):
        key = self._key_from_union(key)
        scope_name = self._bean_scopes[key]
        if not scope_name:
            return None
        result = self._scopes[scope_name].get(key)
        if not result:
            result = self._object_factories[key](self)
            self._scopes[scope_name].set(key, result)
        return result

    def bean_scope(self, key: typing.Union[str, type, callable]) -> typing.Optional[Scope]:
        key = self._key_from_union(key)
        scope_name = self._bean_scopes[key]
        if not scope_name:
            return None
        return self.scope(scope_name)

    def scope(self, scope_name: str) -> typing.Optional[Scope]:
        return self._scopes.get(scope_name)

    def add_listener(self, listener: listeners.YadiListener):
        for k, v in self._TYPES_2_LIST.items():
            if isinstance(listener, k):
                getattr(self, v).append(listener)

    def on_create(self, bean):
        for listener in self._post_create_listeners:
            listener.on_create(bean)


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

    @property
    def level(self):
        return 0


class _PrototypeScope(Scope):
    @property
    def name(self):
        return PROTOTYPE

    def get(self, key: str):
        return None

    def set(self, key: str, obj: object):
        pass

    @property
    def level(self):
        return super(_PrototypeScope, self).level


class BaseScopesContext(DelegationContext):
    def __init__(self):
        super(BaseScopesContext, self).__init__()
        self.add_scope(_SingletonScope())
        self.add_scope(_PrototypeScope())


DEFAULT_CONTEXT = BaseScopesContext()
DEFAULT_CONTEXT.add_listener(listeners_impl.FunctionAttributeLifeCycleListener('__yadi_post_create'))
