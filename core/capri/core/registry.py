from capri.utils import NesteDict
from .exceptions import RegistrationExists, RegistrationNotFound
from .typing import Item


class Registry:

    def __init__(self):
        self._items = NesteDict()

    def get(self, key: str) -> Item:
        try:
            return self._items[key]
        except KeyError:
            raise RegistrationNotFound(key)

    def getset(self, key: str, default: Item) -> Item:
        try:
            return self.get(key)
        except RegistrationNotFound:
            pass

        self.register(default, key)
        return default

    def register(self, item: Item, key: str, *, force=False) -> str:
        if force is True or key not in self._items:
            self._items[key] = item
            return key
        raise RegistrationExists(key)

    def unregister(self, key: str):
        try:
            del self._items[key]
        except KeyError:
            pass
