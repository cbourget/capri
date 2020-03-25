from capri.core.provider import Provider
from capri.core.registry import RegistrationNotFoundError


class Injector:

    def __init__(self, providers, context):
        self._providers = providers
        self._context = context
        self._cache = Provider()

    def get_value(self, token, *, many=False):
        if many is True:
            return self._get_many_values(token)

        for provider in self._providers:
            try:
                return provider.get_value(token)
            except RegistrationNotFoundError:
                pass

        raise InjectionError('No value found with token: {}'.format(token))

    def _get_many_values(self, token):
        values = []
        tokens = []
        for provider in self._providers:
            try:
                result = provider.get_value(token, many=True)
            except RegistrationNotFoundError:
                continue

            for value, _token in result:
                if _token not in tokens:
                    values.append((value, _token))

        if values:
            return values

        raise InjectionError(
            'No values found with token: {}'.format(token))

    def get_instance(self, token, *, many=False):
        if many is True:
            return self._get_many_instances(token)

        try:
            return self._get_instance_from_cache(token)
        except RegistrationNotFoundError:
            pass

        for provider in self._providers:
            try:
                return self._get_instance_from_provider(token, provider)
            except RegistrationNotFoundError:
                pass

        raise InjectionError(
            'No instance found with token: {}'.format(token))

    def _get_many_instances(self, token):
        instances = []
        tokens = []
        for provider in self._providers:
            try:
                items = self._get_instance_from_provider(
                    token, provider, many=True)
            except RegistrationNotFoundError:
                continue

            for instance, _token in items:
                if _token not in tokens:
                    instances.append((instance, _token))
                    tokens.append(_token)

        if instances:
            return instances

        raise InjectionError(
            'No instances found with token: {}'.format(token))

    def _get_instance_from_provider(self, token, provider, *, many=False):
        try:
            return provider.get_instance(token, many=many)
        except RegistrationNotFoundError:
            pass

        if many is True:
            return self._resolve_factories(provider, token)
        return self._resolve_factory(provider, token)

    def _get_instance_from_cache(self, token):
        return self._cache.get_instance(token)

    def _cache_instance(self, instance, token):
        self._cache.register_instance(instance, token)

    def _resolve_factory(self, provider, token):
        factory = provider.get_factory(token)
        instance = factory(self._context)
        self._cache_instance(instance, token)
        return instance

    def _resolve_factories(self, provider, token):
        instances = []
        factories = provider.get_factory(token, many=True)
        for factory, token in factories:
            try:
                instance = self._get_instance_from_cache(token)
            except RegistrationNotFoundError:
                instance = self._get_instance_from_provider(token, provider)

            instances.append((instance, token))

        return instances


class InjectionError(Exception):
    pass
