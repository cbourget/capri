class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls in cls._instances:
            return cls._instances[cls]

        def bust(self):
            self.__class__._instances.pop(self.__class__, None)

        setattr(cls, bust.__name__, bust)
        cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]
