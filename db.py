from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel

from domain.interface.config import ConfigRepository
from domain.interface.user import UserRepository


class DataBase(object):
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.db = db_name
        self.query = QSqlQuery()

        self._config_repository = None
        self._user_repository = None
        self._schedule_repository = None

    def __del__(self):
        if self._db.isOpen():
            self._terminate_db_connection()

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, db_name):
        self._db = QSqlDatabase.addDatabase("QSQLITE")
        self._db.setDatabaseName(db_name)
        if not self._db.open():
            raise EnvironmentError('database connection failed')

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @property
    def config_repository(self):
        return self._config_repository

    @config_repository.setter
    def config_repository(self, value):
        self._config_repository = value

    @property
    def user_repository(self):
        return self._user_repository

    @user_repository.setter
    def user_repository(self, value):
        self._user_repository = value

    @property
    def schedule_repository(self):
        return self._schedule_repository

    @schedule_repository.setter
    def schedule_repository(self, value):
        self._schedule_repository = value

    def _terminate_db_connection(self):
        self._db.close()
        self._db.removeDatabase(self.db_name)

    def connect_in_memory_repositories(self, config_repository: ConfigRepository, user_repository: UserRepository):
        self.config_repository = config_repository
        self._config_repository.query = self._query

        self.user_repository = user_repository
        self._user_repository.query = self._query

    def create_db_tables(self):
        self._config_repository.create_config_table()
        term_count, worker_per_term, assistant_mode = self._config_repository.get_config()

        self._user_repository.create_default_user_table()
        self._user_repository.add_term_related_columns_in_user(term=term_count)
