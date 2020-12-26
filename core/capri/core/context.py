from .injector import Injector


class AppContext:

    def __init__(self, settings, providers):
        self.settings = settings
        self._injector = Injector(providers, self)

    def get_value(self, token):
        return self._injector.get_value(token)

    def get_values(self, token):
        return self._injector.get_values(token)

    def get_instance(self, token):
        return self._injector.get_instance(token)

    def get_instances(self, token):
        return self._injector.get_instances(token)


class RootContext(AppContext):
    pass
