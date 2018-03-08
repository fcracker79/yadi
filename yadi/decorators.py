from yadi import bean_factories
from yadi.context import SINGLETON, DEFAULT_CONTEXT
from yadi.types import bean_name_from_type


def inject(scope_name=SINGLETON, context=DEFAULT_CONTEXT, name=None):
    def _outer(object_type):
        context.register_bean(
            name or bean_name_from_type(object_type),
            bean_factories.recursive_create(object_type),
            scope_name
        )
        return object_type
    return _outer
