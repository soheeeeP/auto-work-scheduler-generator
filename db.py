from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel


class DataBase(object):
    def __init__(self):
        self._db = None
        self._query = QSqlQuery()

    def __del__(self):
        self._terminate_db_connection()

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, db_name):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_name)
        if not self.db.open():
            raise EnvironmentError('database connection failed')

    def _terminate_db_connection(self):
        self.db.close()
        self.db.removeDatabase('test.db')

    def _create_user_table_in_db(self):
        self.query.exec_(
            """
            create table user (
                id INTEGER primary key autoincrement ,
                rank VARCHAR(30) NOT NULL ,
                name VARCHAR(30) NOT NULL ,
                status VARCHAR(30) default 'Default' ,
                
                weekday_day BOOLEAN default TRUE ,
                weekday_dinner BOOLEAN default TRUE ,
                weekday_night BOOLEAN default TRUE ,
                holiday_day BOOLEAN default TRUE ,
                holiday_dinner BOOLEAN default TRUE ,
                holiday_night BOOLEAN default TRUE ,
                
                weekday_day_count INTEGER default 0 ,
                weekday_dinner_count  INTEGER default 0 ,
                weekday_night_count  INTEGER default 0 ,
                holiday_day_count INTEGER default 0 ,
                hoiday_dinner_count INTEGER default 0 ,
                holiday_night_count  INTEGER default 0
            )
            """
        )

    def _insert_dummy_user_data_in_db(self, rank, name, status):
        self.query.exec_(
            f"""insert into user (rank, name, status) values ('{rank}', '{name}', '{status}')"""
        )

    def print_sql_query(self):
        self.query.exec_("select * from user")
        while self.query.next():
            print(f'{self.query.value(0)}: {self.query.value(1)} | {self.query.value(2)} | {self.query.value(3)}')

