import inspect

from capri.utils import NesteDict, Singleton

from .context import RootContext
from .provider import Provider
from .registry import Registry, RegistrationNotFound

class App(metaclass=Singleton):

    def __init__(self, settings, bootstrap='bootstrap'):
        self.settings = NesteDict(**(settings or {}))
        self._bootstrap = bootstrap
        self._providers = Registry()

    def register_value(self, value, token, *, ctx_iface=None,
                       force=False):
        provider = self._get_context_provider(ctx_iface)
        provider.register_value(value, token, force=force)

    def register_instance(self, instance, token, *, ctx_iface=None,
                          force=False):
        provider = self._get_context_provider(ctx_iface)
        provider.register_instance(instance, token, force=force)

    def register_factory(self, factory, token=None, *, ctx_iface=None,
                         force=False):
        token = factory if token is None else token
        provider = self._get_context_provider(ctx_iface)
        provider.register_factory(factory, token, force=force)

    def create_context(self, factory=RootContext, iface=None, *args, **kwargs):
        token = iface or factory
        if not iface:
            iface = [factory]
        elif not isinstance(iface, list):
            iface = [iface]

        if RootContext not in iface:
            iface.append(RootContext)

        providers = [self._get_context_provider(i) for i in iface]
        context = factory(self.settings, providers, *args, **kwargs)
        providers[0].register_instance(context, token)

        return context

    def include(self, path, *args, **kwargs):
        if path.startswith('.'):
            origin = inspect.stack()[1]
            path = '{}{}'.format(inspect.getmodule(origin[0]).__name__, path)
        module = __import__(path, globals(), locals(), [self._bootstrap], 0)
        module.bootstrap(self, *args, **kwargs)

    def _get_context_provider(self, ctx_iface):
        ctx_iface = ctx_iface or RootContext
        key = self._generate_context_key(ctx_iface)

        try:
            provider = self._providers.get(key)
        except RegistrationNotFound:
            provider = Provider()
            self._providers.register(provider, key)

        return provider

    def _generate_context_key(self, ctx_iface):
        return str(ctx_iface).replace('.', ':').replace('\'', '')
