from inspect import isclass, signature

from capri.utils.annotation import param_is_positionnal

from .provider import Provider
from .registry import RegistrationNotFound


class Injector:

    def __init__(self, providers, context):
        self._providers = providers
        self._context = context
        self._cache = Provider()

    def get_value(self, token):
        for provider in self._providers:
            try:
                return provider.get_value(token)
            except RegistrationNotFound:
                pass

        raise RegistrationNotFound(token)

    def get_values(self, token):
        values = []
        tokens = []
        for provider in self._providers:
            try:
                result = provider.get_values(token)
            except RegistrationNotFound:
                continue

            for value, _token in result:
                if _token not in tokens:
                    values.append((value, _token))

        if values:
            return values

        raise RegistrationNotFound(token)

    def get_instance(self, token):
        try:
            return self._get_instance_from_cache(token)
        except RegistrationNotFound:
            pass

        for provider in self._providers:
            try:
                return self._get_instance_from_provider(token, provider)
            except RegistrationNotFound:
                pass

        raise RegistrationNotFound(token)

    def get_instances(self, token):
        instances = []
        tokens = []
        for provider in self._providers:
            try:
                items = self._get_instance_from_provider(
                    token, provider, multi=True)
            except RegistrationNotFound:
                continue

            for instance, _token in items:
                if _token not in tokens:
                    instances.append((instance, _token))
                    tokens.append(_token)

        if instances:
            return instances

        raise RegistrationNotFound(token)

    def _get_instance_from_provider(self, token, provider, *, multi=False):
        getter = provider.get_instance if not multi else provider.get_instances
        try:
            return getter(token)
        except RegistrationNotFound:
            pass

        if multi is True:
            return self._resolve_factories(provider, token)
        return self._resolve_factory(provider, token)

    def _get_instance_from_cache(self, token):
        return self._cache.get_instance(token)

    def _cache_instance(self, instance, token):
        self._cache.register_instance(instance, token)

    def _resolve_factory(self, provider, token):
        factory = provider.get_factory(token)
        args, kwargs = self._get_factory_args(factory)
        instance = factory(*args, **kwargs)
        self._cache_instance(instance, token)
        return instance

    def _resolve_factories(self, provider, token):
        instances = []
        factories = provider.get_factories(token)
        for factory, token in factories:
            try:
                instance = self._get_instance_from_cache(token)
            except RegistrationNotFound:
                instance = self._get_instance_from_provider(token, provider)

            instances.append((instance, token))

        return instances

    def _get_factory_args(self, factory):
        args = []
        kwargs = {}

        parameters = signature(factory).parameters.values()
        func = factory if not isclass(factory) else factory.__init__
        for param in parameters:
            try:
                arg = self._resolve_function_param(func, param)
            except BadSignature as exc:
                if len(parameters) == 1:
                    return [self._context], {}
                else:
                    raise exc

            if param_is_positionnal(param):
                args.append(arg)
            else:
                kwargs[param.name] = args

        return args, kwargs

    def _resolve_function_param(self, function, param):
        name = param.name
        annon = function.__annotations__.get(name)
        if not annon:
            raise BadSignature(name)

        for getter in (self._context.get_instance, self._context.get_value):
            try:
                arg = getter(annon)
            except RegistrationNotFound:
                pass
            else:
                break
        else:
            raise DependencyNotFound(name, annon)    

        return arg


class InjectionError(Exception):
    pass


class DependencyNotFound(InjectionError):

    def __init__(self, name, token):
        super().__init__(
            'Failed to inject: {}: {}. '.format(name, token))


class BadSignature(InjectionError):

    def __init__(self, arg):
        super().__init__(
            'Argument "{}" is not annotated. '
            'Can\'t inject dependency.'.format(arg))
