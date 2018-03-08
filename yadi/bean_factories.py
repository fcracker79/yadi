from yadi.context import Context


def recursive_create(object_type: type):
    def _inner(context: Context) -> object:
        args = {}
        for param, arg_type in object_type.__init__.__annotations__.items():
            bean_name = arg_type.__yadi__
            bean_instance = context.get_bean(bean_name)
            args[param] = bean_instance
        return object_type(**args)
    return _inner
