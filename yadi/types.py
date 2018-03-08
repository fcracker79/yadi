import typing


def bean_name_from_type(object_type):
    return '{}/{}'.format(object_type.__module__, object_type.__name__)


class YadiMeta(typing.TypingMeta, type):
    def __new__(cls, name, bases, namespace):
        return super().__new__(cls, name, bases, namespace, _root=True)

    def __getitem__(self, arg):
        if isinstance(arg, tuple):
            orig_type, name = arg
            orig_type = orig_type
        else:
            orig_type, name = arg, bean_name_from_type(arg)

        class _yadi(orig_type):
            __yadi__ = name
        return _yadi


class Yadi(typing.Final, metaclass=YadiMeta):
    __slots__ = ()
