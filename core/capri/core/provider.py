from typing import List, Tuple

from .registry import Registry
from .typing import Item, Token


class Provider:

    def __init__(self):
        self._items = Registry()
        self._tokens = Registry()

    def get(self, token: Token) -> Item:
        return self._items.get(self._generate_key(token))

    def get_all(self, token: Token) -> List[Tuple[Item, Token]]:
        parent_key = self._generate_key(token, multi=True)
        return [(
            self._items.get(self._generate_key(_token)),
            _token
        ) for _token in self._tokens.get(parent_key)]

    def register(self, item: Item, token: Token, *, force=False) -> str:
        key = self._register_token(token)
        return self._items.register(item, key, force=force)

    def _register_token(self, token: Token) -> str:
        if not isinstance(token, (list, tuple)):
            parent_token = token
        else:
            parent_token = token[:-1]

        parent_key = self._generate_key(parent_token, multi=True)
        tokens = self._tokens.getset(parent_key, set())
        tokens.add(token)

        return self._generate_key(token)

    def _generate_key(self, token: Token, *, multi=False) -> str:
        if not isinstance(token, (list, tuple)):
            token = [token]

        default = '__default__'
        key = '.'.join([
            self._stringify_token(segment)
            for segment in token if segment != default])
        if multi is False:
            key = '{}.{}'.format(key, default)

        return key

    def _stringify_token(self, token: Token) -> str:
        return str(token).replace('.', ':').replace('\'', '')
