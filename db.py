from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel


class DataBase(object):
    def __init__(self):
        self._db = None
        self._query = None

        self.term_count = 3             # 교대제 설정값 (기본값 3)
        self.worker_per_term = 1        # 시간 당 근무 인원수 (기본값 1)
        self.assistant_mode = False     # 사수/부사수 근무모드 on, off (기본값 off)

    def __del__(self):
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

        self.query = QSqlQuery()
        self._create_users_table_in_db()
        self._create_schedule_table_in_db()

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, query):
        self._query = query

    def _terminate_db_connection(self):
        if self._db.open():
            self._db.close()
            self._db.removeDatabase('test.db')

    # TODO: program 옵션에 따른 table column 추가하기
    def _create_users_table_in_db(self):
        self._query.exec_(
            """
            create table if not exists users (
                id INTEGER primary key autoincrement ,
                rank VARCHAR(30) NOT NULL ,
                name VARCHAR(30) NOT NULL ,
                status VARCHAR(30) default 'Default' ,
            )
            """
        )

    # TODO: schedule table 생성
    def _create_schedule_table_in_db(self):
        self._query.exec_(
            """
            create table if not exists schedule (
                id INTEGER primary key autoincrement ,
                date DATE NOT NULL ,
                time VARCHAR(30) NOT NULL ,
                worker_id INTEGER REFERENCES user(id)
            )
            """
        )

    def _insert_dummy_user_data_in_db(self, rank, name, status):
        # work = lambda x: False if x.upper == 'X' else True
        self._query.exec_(
            f"""insert into user (rank, name, status) values ('{rank}', '{name}', '{status}')"""
        )

    # TODO: query문 class method로 추가하기

    def select_all_user(self):
        self._query.exec_("select * from user")
        while self.query.next():
            print(f'{self.query.value(0)}: {self.query.value(1)} | {self.query.value(2)} | {self.query.value(3)}')

