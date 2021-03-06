import abc
import unittest
from yadi import decorators
from yadi import context_impl, types


class TestObjectInjection(unittest.TestCase):
    def test_base_scopes_context_with_names(self):
        sut = context_impl.BaseScopesContext()

        class Component1I(metaclass=abc.ABCMeta):
            pass

        class Component2I(metaclass=abc.ABCMeta):
            pass

        @decorators.inject(context=sut, name='a component')
        class Component2(Component2I):
            def __init__(self, c1: types.Yadi[Component1I]):
                self.c1 = c1

        @decorators.inject(context=sut)
        class Component1(Component1I):
            pass

        c2 = sut.get_bean('a component')  # type: Component2
        self.assertEqual(Component1, type(c2.c1))

    def test_base_scopes_context_with_types(self):
        sut = context_impl.BaseScopesContext()

        class Component1I(metaclass=abc.ABCMeta):
            pass

        class Component2I(metaclass=abc.ABCMeta):
            pass

        @decorators.inject(context=sut)
        class Component2(Component2I):
            def __init__(self, c1: types.Yadi[Component1I]):
                self.c1 = c1

        @decorators.inject(context=sut)
        class Component1(Component1I):
            pass

        c2_class = sut.get_bean(Component2)  # type: Component2
        self.assertEqual(Component1, type(c2_class.c1))
        c2_interface = sut.get_bean(Component2I)  # type: Component2
        self.assertIs(c2_class, c2_interface)
