from yadi import bean_factories
from yadi.context import SINGLETON
from yadi.context_impl import DEFAULT_CONTEXT


def inject(scope=SINGLETON, context=DEFAULT_CONTEXT, name=None):
    def _outer(object_type):
        bean = bean_factories.recursive_create(object_type, scope, context)
        context.register_bean(name, bean, object_type, scope)

        return object_type
    return _outer


def post_create(fun):
    fun.__yadi_post_create = True
    return fun
