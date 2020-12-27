import inspect
from typing import Any
from capri.utils import NesteDict, Singleton

from .context import Context
from .exceptions import ContextExists, RegistrationExists
from .factory import Factory
from .provider import Provider
from .registry import Registry
from .typing import Item, Token

class App(metaclass=Singleton):

    def __init__(self, settings: dict, bootstrap='bootstrap'):
        self.settings = NesteDict(**(settings or {}))
        self._bootstrap = bootstrap
        self._providers = Registry()

    def register(
        self,
        item: Item,
        token: Token,
        *,
        factory=False,
        ctx_iface=None,
        force=False
    ):
        if factory:
            item = Factory(item)
        provider = self._get_context_provider(ctx_iface)
        provider.register(item, token, force=force)

    def create_context(
        self,
        factory=Context,
        iface=None,
        *args,
        **kwargs
    ) -> Context:
        iface = [*([iface or factory])]
        token = iface[0]

        if Context not in iface:
            iface.append(Context)

        providers = list(set([self._get_context_provider(i) for i in iface]))
        context = factory(self.settings, providers, *args, **kwargs)
        try:
            providers[0].register(context, token)
        except RegistrationExists:
            raise ContextExists()

        return context

    def include(self, path: str, *args, **kwargs):
        if path.startswith('.'):
            origin = inspect.stack()[1]
            path = '{}{}'.format(inspect.getmodule(origin[0]).__name__, path)
        module = __import__(path, globals(), locals(), [self._bootstrap], 0)
        module.bootstrap(self, *args, **kwargs)

    def _get_context_provider(self, ctx_iface: Any) -> Provider:
        ctx_iface = ctx_iface or Context
        key = self._generate_context_key(ctx_iface)
        return self._providers.getset(key, Provider())


    def _generate_context_key(self, ctx_iface: Any) -> str:
        return str(ctx_iface).replace('.', ':').replace('\'', '')
