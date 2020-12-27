from typing import List, Tuple, Union

from .exceptions import DependencyNotFound, RegistrationNotFound
from .context import Context
from .factory import Factory
from .provider import Provider
from .typing import Item, Token


class Injector:

    def __init__(self, providers: List[Provider], context: Context):
        self._providers = providers
        self._context = context
        self._cached = Provider()

    def get(self, token: Token) -> Item:
        for provider in self._providers:
            try:
                return self._get_from_provider(token, provider)
            except RegistrationNotFound:
                pass

        raise DependencyNotFound(token)

    def get_all(self, token: Token) -> List[Tuple[Item, Token]]:
        items = []
        tokens = []
        for provider in self._providers:
            try:
                _items = self._get_all_from_provider(token, provider)
            except RegistrationNotFound:
                continue

            for item, _token in _items:
                if _token not in tokens:
                    items.append((item, _token))
                    tokens.append(_token)

        if items:
            return items

        raise DependencyNotFound(token)

    def _cache(self, item: Item, token: Token):
        self._cached.register(item, token)

    def _get_from_cache(self, token: Token):
        return self._cached.get(token)

    def _get_from_provider(
        self,
        token: Token,
        provider:
        Provider
    ) -> Item:
        item = provider.get(token)
        return self._resolve(item, token)

    def _get_all_from_provider(
        self,
        token: Token,
        provider: Provider
    ) -> List[Tuple[Item, Token]]:
        items = provider.get_all(token)
        return [(self._resolve(i, t), t) for i, t in items]

    def _resolve(self, item: Union[Item, Factory], token: Token) -> Item:
        try:
            return self._get_from_cache(token)
        except RegistrationNotFound:
            pass

        if isinstance(item, Factory):
            resolved = item(self._context)
            self._cache(resolved, token)
        else:
            resolved = item

        return resolved
