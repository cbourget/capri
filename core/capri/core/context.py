from capri.core.injector import Injector


class AppContext:

    def __init__(self, settings, providers):
        self.settings = settings
        self._injector = Injector(providers, self)

    def get_value(self, token, *, many=False):
        return self._injector.get_value(token, many=many)

    def get_instance(self, token, *, many=False):
        return self._injector.get_instance(token, many=many)


class RootContext(AppContext):
    pass
