from sqlalchemy import Connection, MetaData
from sqlalchemy.engine import Engine, ResultProxy
from sqlalchemy.sql.expression import Executable

from .exceptions import DatabaseError

class Database:
    """ SQLAlchemy database """

    def __init__(self, engine: Engine, metadata: MetaData):
        self.engine = engine
        self.metadata = metadata
        self.connection = None

    def connect(self) -> Connection:
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

    def execute(self, executable: Executable) -> ResultProxy:
        connection = self.connect()
        result = connection.execute(executable)

        if not connection.in_transaction():
            self.close()

        return result
