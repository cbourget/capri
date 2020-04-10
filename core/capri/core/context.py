from capri.core.injector import Injector


class AppContext:

    def __init__(self, settings, providers):
        self.settings = settings
        self._injector = Injector(providers, self)

    def get_value(self, token, *, multi=False):
        return self._injector.get_value(token, multi=multi)

    def get_instance(self, token, *, multi=False):
        return self._injector.get_instance(token, multi=multi)


class RootContext(AppContext):
    pass
