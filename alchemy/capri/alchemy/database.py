class Database:
    """ SQLAlchemy database """

    def __init__(self, engine, metadata):
        self.engine = engine
        self.metadata = metadata
        self.connection = None

    def connect(self):
        if self.connection is None or self.connection.closed:
            self.connection = self.engine.connect()
        return self.connection

    def close(self):
        if self.connection is None:
            return

        if self.connection.in_transaction():
            raise DatabaseError(
                'Cannot close connection when transactions are still ongoing.')

        self.connection.close()
        self.connection = None

    def execute(self, executable):
        connection = self.connect()
        result = connection.execute(executable)

        if not connection.in_transaction():
            self.close()

        return result


class DatabaseError(Exception):
    pass
