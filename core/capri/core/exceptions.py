from .typing import Token


class ContextError(Exception):
    pass


class ContextExists(ContextError):

    def __init__(self):
        super().__init__(
            'A context with that interface already exists. '
            'You should use it or create a context with a different '
            'interface.'
        )


class InjectionError(Exception):
    pass


class DependencyNotFound(InjectionError):

    def __init__(self, token: Token):
        super().__init__(
            'Failed to inject dependency: {}. '.format(str(token))
        )


class BadSignature(InjectionError):

    def __init__(self, arg: str):
        super().__init__(
            'Argument "{}" is not annotated. '
            'Can\'t inject dependency.'.format(arg)
        )


class RegistrationError(Exception):
    pass


class RegistrationExists(RegistrationError):

    def __init__(self, key: str):
        super().__init__(
            'An item is already registered under that key: {}. '
            'Use force=true to override'.format(key)
        )


class RegistrationNotFound(RegistrationError):

    def __init__(self, key: str):
        super().__init__('No item found at key: {}'.format(key)
    )
