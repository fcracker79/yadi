import random
import threading
import unittest

from yadi import context_impl, decorators, types, context
from yadi.bean_factories import _ScopedProxy


class TestScopedProxy(unittest.TestCase):
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

        @decorators.inject(scope='threadlocal')
        class Component1:
            def __init__(self):
                self.object_id = random.randint(0, 1000000)

        @decorators.inject(name='a component')
        class Component2:
            def __init__(self, f1: types.Yadi[Component1]):
                self.f1 = f1

        component = context_impl.DEFAULT_CONTEXT.get_bean('a component')
        component_thread_id = []
        self.assertIs(type(component.f1), _ScopedProxy)

        def _f():
            component_thread = context_impl.DEFAULT_CONTEXT.get_bean('a component')
            self.assertIs(type(component_thread.f1), _ScopedProxy)
            component_thread_id.append(component_thread.f1.object_id)
            self.assertEqual(
                component_thread.f1.object_id,
                context_impl.DEFAULT_CONTEXT.get_bean('a component').f1.object_id)

        t = threading.Thread(target=_f)
        t.start()
        t.join()

        self.assertNotEqual(component.f1.object_id, component_thread_id[0])
