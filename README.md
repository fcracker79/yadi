YADI
=================================================
Yet Another Dependency Injection framework

YADI is a dependency injection framework.
It supports both classes and function in a declarative fashion.

Installation
------------

```sh
pip install yadi-framework
```

Basic examples
--------------

This is a simple injection example:

[//]: # (tmp/readme_md_1.py)

```python
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

```

Here it is an example of how to inject functions:

```python
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

```

Contexts
--------
All the components are kept in a context.

By default, the `inject` decorator keeps the beans instances in `from yadi.context_impl.DEFAULT_CONTEXT`.

You might want to instantiate new contexts and pass it as a `context` keyword argument of `inject` decorator.