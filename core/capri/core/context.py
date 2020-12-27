from typing import List, Tuple
from capri.utils import NesteDict

from .provider import Provider
from .typing import Item, Token


class Context:

    def __init__(self, settings: NesteDict, providers: List[Provider]):
        from .injector import Injector
        self.settings = settings
        self._injector = Injector(providers, self)

    def get(self, token: Token) -> Item:
        return self._injector.get(token)

    def get_all(self, token: Token) -> List[Tuple[Item, Token]]:
        return self._injector.get_all(token)
