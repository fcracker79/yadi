import typing

from yadi import bean_factories


class YadiMeta(typing.TypingMeta, type):
    def __new__(cls, name, bases, namespace):
        return super().__new__(cls, name, bases, namespace, _root=True)

    def __getitem__(self, arg):
        if isinstance(arg, tuple):
            orig_type, name = arg
            orig_type = orig_type
        elif isinstance(arg, str):
            orig_type, name = object, arg
        else:
            orig_type, name = arg, bean_factories.bean_name_from_type(arg)

        class _yadi(orig_type):
            __yadi__ = name
        return _yadi


class Yadi(typing.Final, metaclass=YadiMeta):
    __slots__ = ()
