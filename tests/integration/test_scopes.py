import abc
import itertools
import threading
import unittest
from yadi import decorators, context
from yadi import context_impl, types
from yadi.bean_factories import _ScopedProxy


class TestObjectInjection(unittest.TestCase):
    def test_base_scopes_prototype(self):
        sut = context_impl.BaseScopesContext()

        class Component1I(metaclass=abc.ABCMeta):
            pass

        class Component2I(metaclass=abc.ABCMeta):
            pass

        @decorators.inject(context=sut, scope=context.PROTOTYPE, name='a component 1')
        class Component1(Component1I):
            pass

        @decorators.inject(context=sut, name='a component 2')
        class Component2(Component2I):
            def __init__(
                    self, f1: types.Yadi[Component1I],
                    f2: types.Yadi[Component1],
                    f3: types.Yadi['a component 1']):
                self.f1, self.f2, self.f3 = f1, f2, f3

        @decorators.inject(context=sut, name='a component 3')
        class Component3(Component2I):
            def __init__(
                    self, f1: types.Yadi[Component1I],
                    f2: types.Yadi[Component1],
                    f3: types.Yadi['a component 1']):
                self.f1, self.f2, self.f3 = f1, f2, f3
        c2 = sut.get_bean('a component 2')  # type: Component2
        c3 = sut.get_bean('a component 3')  # type: Component3

        self.assertEqual(_ScopedProxy, type(c2.f1))
        self.assertEqual(_ScopedProxy, type(c2.f2))
        self.assertEqual(_ScopedProxy, type(c2.f3))
        self.assertEqual(_ScopedProxy, type(c3.f1))
        self.assertEqual(_ScopedProxy, type(c3.f2))
        self.assertEqual(_ScopedProxy, type(c3.f3))

        instances = [c2.f1, c2.f2, c2.f3, c3.f1, c3.f2, c3.f3]
        elements_to_skip = {
            i * (len(instances) + 1) for i in range(len(instances))
        }

        for i, couple in enumerate(itertools.product(instances, instances)):
            if i in elements_to_skip:
                continue
            ca, cb = couple
            self.assertIsNot(ca, cb)

    def test_base_scopes_singleton(self):
        sut = context_impl.BaseScopesContext()

        class Component1I(metaclass=abc.ABCMeta):
            pass

        class Component2I(metaclass=abc.ABCMeta):
            pass

        @decorators.inject(context=sut, scope=context.SINGLETON, name='a component 1')
        class Component1(Component1I):
            _COUNTER = 0

            def __init__(self):
                assert 0 == self.__class__._COUNTER
                self.__class__._COUNTER += 1

        @decorators.inject(context=sut, name='a component 2')
        class Component2(Component2I):
            def __init__(
                    self, f1: types.Yadi[Component1I],
                    f2: types.Yadi[Component1],
                    f3: types.Yadi['a component 1']):
                self.f1, self.f2, self.f3 = f1, f2, f3

        @decorators.inject(context=sut, name='a component 3')
        class Component3(Component2I):
            def __init__(
                    self, f1: types.Yadi[Component1I],
                    f2: types.Yadi[Component1],
                    f3: types.Yadi['a component 1']):
                self.f1, self.f2, self.f3 = f1, f2, f3
        c2 = sut.get_bean('a component 2')  # type: Component2
        c3 = sut.get_bean('a component 3')  # type: Component3

        self.assertEqual(Component1, type(c2.f1))
        self.assertEqual(Component1, type(c2.f2))
        self.assertEqual(Component1, type(c2.f3))
        self.assertEqual(Component1, type(c3.f1))
        self.assertEqual(Component1, type(c3.f2))
        self.assertEqual(Component1, type(c3.f3))

        instances = [c2.f1, c2.f2, c2.f3, c3.f1, c3.f2, c3.f3]

        for i, couple in enumerate(itertools.product(instances, instances)):
            ca, cb = couple
            self.assertIs(ca, cb)

    def test_custom_scope(self):
        class ThreadLocalScope(context.Scope):
            def __init__(self):
                self._tl = threading.local()

            def get(self, key: str):
                return getattr(self._tl, key, None)

            def set(self, key: str, obj: object):
                setattr(self._tl, key, obj)

            @property
            def name(self):
                return 'threadlocal'

            @property
            def level(self):
                return 100

        context_impl.DEFAULT_CONTEXT.add_scope(ThreadLocalScope())

        @decorators.inject(scope='threadlocal', name='a component 1')
        class Component1:
            pass

        c1 = context_impl.DEFAULT_CONTEXT.get_bean('a component 1')
        c1_2 = context_impl.DEFAULT_CONTEXT.get_bean('a component 1')

        c1_t = []

        def _f():
            c1_t.append(context_impl.DEFAULT_CONTEXT.get_bean('a component 1'))
            self.assertIs(c1_t[0], context_impl.DEFAULT_CONTEXT.get_bean('a component 1'))
        t = threading.Thread(target=_f)
        t.start()
        t.join()

        self.assertIs(c1, c1_2)
        self.assertIsNot(c1, c1_t[0])
