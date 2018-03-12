import unittest

import yadi
from yadi.context_impl import DEFAULT_CONTEXT
from yadi.decorators import inject, post_create
from yadi.types import Yadi


class TestPostCreate(unittest.TestCase):
    def test(self):
        @inject()
        class Component1:
            pass

        @inject()
        class Component2:
            def __init__(self, c1: Yadi[Component1]):
                self.c1 = c1
                self.invoked_post_create = 0

            @post_create
            def finished_creating(self):
                assert self.c1
                self.invoked_post_create += 1

        component_2 = DEFAULT_CONTEXT.get_bean(Component2)  # type: Component2
        self.assertEqual(1, component_2.invoked_post_create)
        DEFAULT_CONTEXT.get_bean(Component2)
        self.assertEqual(1, component_2.invoked_post_create)
