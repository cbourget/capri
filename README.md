# Capri

Capri is a collection of packages built around `capri.core`, a lightweight framework that enables dependency injection.

## Capri.core

### A simple example

```python
# app.py

from capri.core.app import App
from .users.service import UserService

# Create an app with some settings
app = App({
    'database': {
        'host': 'my_host',
        'user': 'my_user',
        'password': 'my_password'
    }
})

# Include the database and users module
app.include('.database')
app.include('.users')

# Create a context
context = app.create_context()

# Retrieve the user service instance from it.
# If it doesn't exist, it'll get created and cached.
user_service = context.get(UserService)
user = user_service.by_id(1)
```

```python
# database.py

class Database:

   def __init__(self, host, user, password, port):
        self.host = host
        self.user = user
        self.password = password
        self.port = port

    def query(self):
        return ...
        
def database_factory(context):
    # Retrieve connection params from the app's settings.
    # The '.' notation allows nested settings to be accessed
    # without checking for the parent objet's existence
    settings = context.settings
    host = settings.get('database.host')
    user = settings.get('database.user')
    password = settings.get('database.password')
    port = settings.get('database.port', 5432)
    return Database(host, user, password, port)

def bootstrap(app):
    # Register the database factory under the Database interface.
    app.register(database_factory, Database, factory=True)
```

```python
# users/__init__.py

# The bootstrap method is invoked when a module is included (app.include)
def bootstrap(app):
  # Include the service module
  app.include('.service')
```

```python
# users/service.py

from ..database import Database

class UserService:

    # An annotated argument will automatically be injected
    def __init__(self, database: Database):
        self.database = database

    def by_id(self, user_id):
        return self.database.query()...

def bootstrap(app):
    # Register the user service factory under the
    # UserService interface. At this point, the user service
    # is not created yet and the database needs not to exist.
    app.register_factory(UserService)
```

In this simple example, we see how factories can be registered into an
app and instances retrieved on demand from an app's context.
Instances obtained this way are created the first time and then cached.

What this example didn't show is that we can also:
* Register instances (instead of factories)
* Register values
* Register under a composite interface (tuple) which also
enables multiple registrations under a the same interface
* Create custom contexts
* Register stuff for specific contexts only
* Override generic registrations in specific contexts
* Create contexts with multiple dependency injectors. Multiple
injectors are resolved in the order they were given (generally specifics -> generics)

## Capri.alchemy

SQLAlchemy engine wrapper. A project using SQLAlchemy should register a single instance of this.

## Capri.falcon

Provides a method to create a Falcon request factory. The context of those requests is a Capri context with dependency injection capabilities.

## Capri.utils

Provides some utilities used by other packages such as the NesteDict that enables accessing nested dict values as shown in the first example. 
