from capri.utils.nestedict import NesteDict


class Registry:

    def __init__(self):
        self._items = NesteDict()

    def get(self, key):
        try:
            return self._items[key]
        except KeyError:
            raise RegistrationNotFoundError(key)

    def register(self, item, key, *, force=False):
        if force is True or key not in self._items:
            self._items[key] = item
            return key
        raise RegistrationExistsError(key)

    def unregister(self, key):
        try:
            del self._items[key]
        except KeyError:
            pass


class RegistrationError(Exception):
    pass


class RegistrationExistsError(RegistrationError):
    
    def __init__(self, key):
        super().__init__(
            'An item is already registered under that key: {}. '
            'Use force=true to override'.format(key))


class RegistrationNotFoundError(RegistrationError):
    
    def __init__(self, key):
        super().__init__('No item found at key: {}'.format(key))
