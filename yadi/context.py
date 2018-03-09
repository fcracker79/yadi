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


SINGLETON = 'singleton'
PROTOTYPE = 'prototype'
