class NesteDict(dict):

    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self

    def __getitem__(self, key):
        nested = super()

        keys = key.split('.')
        for _key in keys[:-1]:
            try:
                nested = nested.__getitem__(_key)
            except KeyError:
                raise KeyError('{} not found.'.format(key))

            assert isinstance(nested, dict)

        try:
            value = nested.__getitem__(keys[-1])
        except KeyError:
            raise KeyError('{} not found.'.format(key))

        return value

    def __setitem__(self, key, value):
        nested = super()

        keys = key.split('.')
        for _key in keys[:-1]:
            try:
                nested = nested.__getitem__(_key)
            except KeyError:
                _nested = NesteDict()
                nested.__setitem__(_key, _nested)
                nested = _nested

            assert isinstance(nested, dict)

        nested.__setitem__(keys[-1], value)

    def __delitem__(self, key):
        keys = key.rsplit('.', 1)
        if len(keys) == 1:
            super().__delitem__(keys[0])
        else:
            nested = self.__getitem__(keys[0])
            nested.__delitem__(keys[1])

    def __contains__(self, key):
        try:
            self.__getitem__(key)
        except KeyError:
            return False

        return True

    def get(self, key, default=None):
        try:
            value = self.__getitem__(key)
        except KeyError:
            value = default

        return value

    def nested_keys(self):
        keys = []
        for key, value in self.items():
            if isinstance(value, dict):
                nested_keys = NesteDict(**value).nested_keys()
                keys = keys + [f'{key}.{k}' for k in nested_keys]
            keys.append(key)

        return keys

    def set(self, key, value):
        self.__setitem__(key, value)
