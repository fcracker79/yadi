import abc


class YadiListener(metaclass=abc.ABCMeta):
    pass


class LifecycleObjectListener(YadiListener, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def on_create(self, bean):
        pass
