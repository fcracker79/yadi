from yadi import bean_factories
from yadi.context import SINGLETON
from yadi.context_impl import DEFAULT_CONTEXT


def inject(scope_name=SINGLETON, context=DEFAULT_CONTEXT, name=None):
    def _outer(object_type):
        if name:
            names = (name, )
        else:
            names = bean_factories.get_all_keys_from_type(object_type)

        bean = bean_factories.recursive_create(object_type)
        for cur_name in names:
            context.register_bean(cur_name, bean, scope_name)
        return object_type
    return _outer
