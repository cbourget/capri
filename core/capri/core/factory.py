from inspect import isclass, signature
from typing import Any, Callable
from capri.utils.annotation import param_is_positionnal

from .context import Context
from .exceptions import BadSignature
from .typing import Item


class Factory:
    def __init__(self, factory: Callable):
        self._factory = factory

    def __call__(self, context: Context) -> Item:
        factory = self._factory
        args = []
        kwargs = {}

        parameters = signature(factory).parameters.values()
        func = factory if not isclass(factory) else factory.__init__
        for param in parameters:
            try:
                arg = self._get_param_value(func, param, context)
            except BadSignature as exc:
                if len(parameters) == 1:
                    arg = context
                else:
                    raise exc

            if param_is_positionnal(param):
                args.append(arg)
            else:
                kwargs[param.name] = arg

        return factory(*args, **kwargs)

    def _get_param_value(self, function: Callable, param, context: Context) -> Any:
        name = param.name
        annon = function.__annotations__.get(name)
        if not annon:
            raise BadSignature(name)
        return context.get(annon)

