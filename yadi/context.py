import abc
import sys
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

    @property
    @abc.abstractmethod
    def level(self) -> int:
        return sys.maxsize


class Context(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add_scope(self, scope: Scope):
        pass

    @abc.abstractmethod
    def register_bean(self, key: str, obj: object, object_type, scope: str):
        pass

    @abc.abstractmethod
    def get_bean(self, key: str) -> typing.Optional[object]:
        pass

    @abc.abstractmethod
    def bean_scope(self, key: typing.Union[str, type, callable]) -> typing.Optional[Scope]:
        pass

    @abc.abstractmethod
    def scope(self, scope_name: str) -> typing.Optional[Scope]:
        pass


SINGLETON = 'singleton'
PROTOTYPE = 'prototype'
