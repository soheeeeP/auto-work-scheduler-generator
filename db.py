from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel

from domain.interface.config import ConfigRepository
from domain.interface.user import UserRepository
from domain.interface.workmode import WorkModeRepository
from domain.interface.schedule import ScheduleRepository
from domain.interface.exception import DateTimeExceptionRepository, RelationExceptionRepository

from domain.repository.config import ConfigInMemoryRepository
from domain.repository.schedule import ScheduleInMemoryRepository
from domain.repository.user import UserInMemoryRepository
from domain.repository.workmode import WorkModeInMemoryRepository
from domain.repository.exception import DateTimeExceptionInMemoryRepository, RelationExceptionInMemoryRepository


class DataBase(object):
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.db = db_name
        self.query = QSqlQuery()

        self.__config_repository = None
        self.__user_repository = None
        self.__work_mode_repository = None
        self.__schedule_repository = None
        self.__exp_datetime_repository = None
        self.__exp_relation_repository = None

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
        return self.__config_repository

    @config_repository.setter
    def config_repository(self, value):
        self.__config_repository = value

    @property
    def user_repository(self):
        return self.__user_repository

    @user_repository.setter
    def user_repository(self, value):
        self.__user_repository = value

    @property
    def work_mode_repository(self):
        return self.__work_mode_repository

    @work_mode_repository.setter
    def work_mode_repository(self, value):
        self.__work_mode_repository = value

    @property
    def schedule_repository(self):
        return self.__schedule_repository

    @schedule_repository.setter
    def schedule_repository(self, value):
        self.__schedule_repository = value

    @property
    def exp_datetime_repository(self):
        return self.__exp_datetime_repository

    @exp_datetime_repository.setter
    def exp_datetime_repository(self, value):
        self.__exp_datetime_repository = value

    @property
    def exp_relation_repository(self):
        return self.__exp_relation_repository

    @exp_relation_repository.setter
    def exp_relation_repository(self, value):
        self.__exp_relation_repository = value

    def _terminate_db_connection(self):
        self.db.close()
        self.db.removeDatabase(self.db_name)

    def connect_in_memory_repositories(
            self,
            config_repository: ConfigRepository,
            user_repository: UserRepository,
            work_mode_repository: WorkModeRepository,
            schedule_repository: ScheduleRepository,
            exp_datetime_repository: DateTimeExceptionRepository,
            exp_relation_repository: RelationExceptionRepository
    ):
        self.config_repository = config_repository
        self.config_repository.query = self.query

        self.user_repository = user_repository
        self.user_repository.query = self.query

        self.work_mode_repository = work_mode_repository
        self.work_mode_repository.query = self.query

        self.schedule_repository = schedule_repository
        self.schedule_repository.query = self.query

        self.exp_datetime_repository = exp_datetime_repository
        self.exp_datetime_repository.query = self.query

        self.exp_relation_repository = exp_relation_repository
        self.exp_relation_repository.query = self.query

    def create_db_tables(self):
        self.config_repository.create_config_table()
        term_count, worker_per_term, assistant_mode = self.config_repository.get_config()

        self.user_repository.create_default_user_table()
        self.exp_datetime_repository.create_exp_datetime_table()
        self.exp_relation_repository.create_exp_relation_table()

        self.work_mode_repository.create_work_mode_table(term_count=term_count)
        self.schedule_repository.create_schedule_table()

        self.query.exec("""PRAGMA foreign_keys = ON;""")


# todo: db name을 .env로 분리
database = DataBase(db_name='test.db')
database.connect_in_memory_repositories(
        config_repository=ConfigInMemoryRepository(),
        user_repository=UserInMemoryRepository(),
        work_mode_repository=WorkModeInMemoryRepository(),
        schedule_repository=ScheduleInMemoryRepository(),
        exp_datetime_repository=DateTimeExceptionInMemoryRepository(),
        exp_relation_repository=RelationExceptionInMemoryRepository()
    )
database.create_db_tables()
