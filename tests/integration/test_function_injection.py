import unittest

from yadi import context_impl, types
from yadi import decorators


class TestObjectInjection(unittest.TestCase):
    def test_functions_positional_arguments(self):
        sut = context_impl.BaseScopesContext()

        @decorators.inject(context=sut)
        class Component:
            pass

        @decorators.inject(context=sut, name='my_function')
        def f(a: int, b, c: types.Yadi[Component]):
            pass

        fun = sut.get_bean('my_function')
        fun(1, 2)

    def test_functions_keyword_argument(self):
        sut = context_impl.BaseScopesContext()

        @decorators.inject(context=sut)
        class Component:
            pass

        @decorators.inject(context=sut, name='my_function')
        def f(a: int, b, c: types.Yadi[Component]=None, d: str=None):
            self.assertTrue(isinstance(c, Component))

        fun = sut.get_bean('my_function')
        fun(1, 2, d='hello')

    def test_functions_of_functions(self):
        sut = context_impl.BaseScopesContext()

        @decorators.inject(context=sut, name='another_function')
        def h(x, y, z=None):
            pass

        @decorators.inject(context=sut, name='my_function')
        def f(a: int, b, c: types.Yadi['another_function'] = None, d: str = None):
            c(a, b, z=d)

        sut.get_bean('my_function')(12, 23, d=5)

    def text_functions_and_objects(self):
        sut = context_impl.BaseScopesContext()

        @decorators.inject(context=sut)
        class Component:
            pass

        @decorators.inject(context=sut, name='another_function')
        def h(x, y, z=None):
            self.assertTrue(isinstance(x, Component))

        @decorators.inject(context=sut, name='my_function')
        def f(a: types.Yadi[Component], b, c: types.Yadi['another_function'] = None, d: str = None):
            c(a, b, z=d)

        sut.get_bean('my_function')(23, d=5)
