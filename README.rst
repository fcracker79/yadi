YADI
====

Yet Another Dependency Injection framework

YADI is a dependency injection framework. It supports both classes and
function in a declarative fashion.

Installation
------------

.. code:: sh

    pip install yadi-framework

Basic examples
--------------

This is a simple injection example:

.. code:: python

    from yadi.context_impl import DEFAULT_CONTEXT
    from yadi.decorators import inject
    from yadi.types import Yadi


    @inject()
    class Component1:
        pass


    @inject()
    class Component2:
        def __init__(self, c1: Yadi[Component1]):
            self.c1 = c1


    @inject()
    class Component3:
        def __init__(self, c1: Yadi[Component1]):
            self.c1 = c1


    c2 = DEFAULT_CONTEXT.get_bean(Component2)  # type: Component2
    c3 = DEFAULT_CONTEXT.get_bean(Component3)  # type: Component3
    print(Component1 is type(c2.c1))  # True
    print(c2.c1 is c3.c1)  # True

Here it is an example of how to inject functions:

.. code:: python

    from yadi.context_impl import DEFAULT_CONTEXT
    from yadi.decorators import inject
    from yadi.types import Yadi


    @inject()
    class Component:
        pass


    @inject(name='another_function')
    def h(x, y, z=None):
        assert isinstance(x, Component)
        print('Function h:', type(x))


    @inject(name='my_function')
    def f(a: Yadi[Component], b, c: Yadi['another_function'] = None, d: str = None):
        c(a, b, z=d)


    DEFAULT_CONTEXT.get_bean('my_function')(23, d=5)  # Function h: <class '__main__.Component'>

Scopes
------

By default, all the beans are saved as Singleton. Each singleton is
stored in its context, that is, there is a single instance *for each
context instance*.

Alternatively, it is possible to save beans as Prototypes, that is, a
different instance is generated whenever the bean is referred to.

.. code:: python

    from yadi import context
    from yadi import types
    from yadi.context_impl import DEFAULT_CONTEXT
    from yadi.decorators import inject


    @inject(scope=context.PROTOTYPE, name='a component 1')
    class Component1:
        pass


    @inject(name='a component 2')
    class Component2:
        def __init__(
                self,
                f1: types.Yadi[Component1],
                f2: types.Yadi['a component 1']):
            self.f1, self.f2 = f1, f2


    @inject(name='a component 3')
    class Component3:
        def __init__(
                self,
                f1: types.Yadi[Component1],
                f2: types.Yadi['a component 1']):
            self.f1, self.f2 = f1, f2


    c2 = DEFAULT_CONTEXT.get_bean('a component 2')  # type: Component2
    c3 = DEFAULT_CONTEXT.get_bean('a component 3')  # type: Component3

    print(isinstance(c2.f1, Component1))  # True
    print(isinstance(c2.f2, Component1))  # True

    print(isinstance(c3.f1, Component1))  # True
    print(isinstance(c3.f2, Component1))  # True

    print(c2.f1 == c2.f2)  # False
    print(c3.f1 == c3.f2)  # False
    print(c2.f1 == c3.f1)  # False
    print(c2.f1 == c3.f2)  # False
    print(c2.f2 == c3.f1)  # False
    print(c2.f2 == c3.f2)  # False

It is also possible to define custom scopes and add them to a context.

Here it is an example of thread-local scope:

.. code:: python

    import threading

    from yadi.context import Scope
    from yadi.context_impl import DEFAULT_CONTEXT
    from yadi.decorators import inject


    class ThreadLocalScope(Scope):
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


    DEFAULT_CONTEXT.add_scope(ThreadLocalScope())


    @inject(scope='threadlocal', name='a component 1')
    class Component1:
        pass


    c1 = DEFAULT_CONTEXT.get_bean('a component 1')
    c1_2 = DEFAULT_CONTEXT.get_bean('a component 1')

    thread_c1 = []
    c1_t = None


    def _f():
        global c1_t
        c1_t = DEFAULT_CONTEXT.get_bean('a component 1')
        print(c1_t == DEFAULT_CONTEXT.get_bean('a component 1'))  # True
        thread_c1.append(c1_t)


    t = threading.Thread(target=_f)
    t.start()
    t.join()

    print(c1 == c1_2)  # True
    print(c1 == c1_t)  # False

**Scoped proxies** Let's suppose to inject a thread-local scoped bean in
a singleton. As a result, different thread sharing the same singleton
should not share the same thread local bean, which is not possible.

In order to solve this issue, YADI creates a proxy around the injected
bean that delegates any access to the current bean in the context.

More in general, scopes have a ``level`` attribute: if the injected bean
has a higher scope level than the container bean, the injected bean is
wrapped into a scoped proxy.

Here it is an example of scoped proxies (don't worry, you do not have to
do anything to make it work).

.. code:: python

    import random
    import threading

    from yadi.bean_factories import _ScopedProxy
    from yadi.context import Scope
    from yadi.context_impl import DEFAULT_CONTEXT
    from yadi.decorators import inject
    from yadi.types import Yadi


    class ThreadLocalScope(Scope):
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


    DEFAULT_CONTEXT.add_scope(ThreadLocalScope())


    @inject(scope='threadlocal')
    class Component1:
        def __init__(self):
            self.object_id = random.randint(0, 1000000)


    @inject(name='a component')
    class Component2:
        def __init__(self, f1: Yadi[Component1]):
            self.f1 = f1


    component = DEFAULT_CONTEXT.get_bean('a component')
    component_thread_id = []
    print('Main thread, scoped proxy type', type(component.f1) == _ScopedProxy)  # Main thread, scoped proxy type True


    def _f():
        component_thread = DEFAULT_CONTEXT.get_bean('a component')
        print('Subthread, scoped proxy type', type(component_thread.f1) == _ScopedProxy)
        component_thread_id.append(component_thread.f1.object_id)
        print(
            'Subthread, bean id',
            component_thread.f1.object_id == DEFAULT_CONTEXT.get_bean('a component').f1.object_id)


    t = threading.Thread(target=_f)
    t.start()
    t.join()  # Subthread, scoped proxy type True
              # Subthread, bean id True

    print('Main thread, bean id', component.f1.object_id == component_thread_id[0])  # Main thread, bean id False

Contexts
--------

All the components are kept in a context.

By default, the ``inject`` decorator keeps the beans instances in
``yadi.context_impl.DEFAULT_CONTEXT``.

You might want to instantiate a new context and pass it as a ``context``
keyword argument of ``inject`` decorator.
