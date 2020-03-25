from capri.core.registry import (
    Registry,
    RegistrationError,
    RegistrationNotFoundError)


class Provider:

    def __init__(self):
        self._values = Registry()
        self._instances = Registry()
        self._factories = Registry()
        self._tokens = Registry()

    def get_value(self, token, *, many=False):
        return self._get(self._values, token, many=many)

    def get_instance(self, token, *, many=False):
        return self._get(self._instances, token, many=many)

    def get_factory(self, token, *, many=False):
        return self._get(self._factories, token, many=many)

    def register_value(self, value, token, *, force=False):
        key = self._register_token(token)
        return self._values.register(value, key, force=force)

    def register_instance(self, instance, token, *, force=False):
        key = self._register_token(token)
        return self._register_instance_or_factory(
            self._instances, instance, key, force=force)

    def register_factory(self, factory, token, *, force=False):
        key = self._register_token(token)
        if force is True:
            self._instances.unregister(key)

        return self._register_instance_or_factory(
            self._factories, factory, key, force=force)

    def _get(self, registry, token, *, many=False):
        if many is True:
            return self._get_many(registry, token)

        return registry.get(self._generate_key(token))

    def _get_many(self, registry, token):
        parent_key = self._generate_key(token, many=True)
        return [(
            registry.get(self._generate_key(_token)),
            _token
        ) for _token in self._tokens.get(parent_key)]

    def _register_instance_or_factory(self, registry, instance_or_factory,
                                      key, *, force=False):
        if force is True:
            return registry.register(instance_or_factory, key, force=force)

        try:
            self._instances.get(key)
            self._factories.get(key)
        except RegistrationNotFoundError:
            return registry.register(instance_or_factory, key)

        raise RegistrationError('Failed to register instance or factory')

    def _register_token(self, token):
        if not isinstance(token, (list, tuple)):
            parent_token = token
        else:
            parent_token = token[:-1]

        parent_key = self._generate_key(parent_token, many=True)

        try:
            tokens = self._tokens.get(parent_key)
        except RegistrationNotFoundError:
            tokens = set()
            self._tokens.register(tokens, parent_key)

        tokens.add(token)

        return self._generate_key(token)

    def _generate_key(self, token, *, many=False):
        if not isinstance(token, (list, tuple)):
            token = [token]

        default = '__default__'
        key = '.'.join([
            self._format_key_part(part)
            for part in token if part != default])
        if many is False:
            key = '{}.{}'.format(key, default)

        return key

    def _format_key_part(self, part):
        return str(part).replace('.', ':').replace('\'', '')
