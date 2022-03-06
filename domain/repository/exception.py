from datetime import datetime
from typing import List, Dict, Union

from PyQt5.QtSql import QSqlQuery
from domain.interface.exception import DateTimeExceptionRepository


class DateTimeExceptionInMemoryRepository(DateTimeExceptionRepository):
    def print_exp_info_from_query(self) -> Dict:
        record = self.query.record()
        data = {
            "id": self.query.value(record.indexOf("id")),
            "user_id": self.query.value(record.indexOf("user_id")),
            "user_name": self.query.value(record.indexOf("user_name")),
            "start": self.query.value(record.indexOf("start_datetime")),
            "end": self.query.value(record.indexOf("end_datetime"))
        }
        return data

    @staticmethod
    def exp_datetime_query_record(_query: QSqlQuery):
        record = _query.record()
        value_dict = {
            "id": record.indexOf("id"),
            "user_id": record.indexOf("user_id"),
            "user_name": record.indexOf("user_name"),
            "start": record.indexOf("start_datetime"),
            "end": record.indexOf("end_datetime")
        }

        return record, value_dict

    def create_exp_datetime_table(self):
        self.query.exec_(
            """
            CREATE TABLE if NOT EXISTS exp_datetime (
                id INTEGER primary key autoincrement,
                user_id INTEGER,
                start_datetime DATETIME DEFAULT NULL,
                end_datetime DATETIME DEFAULT NULL,
                foreign key (user_id) REFERENCES user(id) ON DELETE CASCADE
            )
            """
        )

    def insert_exp_datetime(self, user_id: int, start_dt: datetime, end_dt: datetime) -> Union[int, None]:
        self.query.prepare(
            f"""
            INSERT INTO exp_datetime(user_id, start_datetime, end_datetime)
            VALUES (:user_id, :start_datetime, :end_datetime);
            """
        )
        self.query.bindValue(":user_id", user_id)
        self.query.bindValue(":start_datetime", start_dt)
        self.query.bindValue(":end_datetime", end_dt)
        self.query.exec_()

        return self.query.value(0) if self.query.first() else None

    def update_exp_datetime(self, exp_id: int, start_dt: datetime, end_dt: datetime) -> Union[int, None]:
        self.query.prepare(
            f"""
            UPDATE exp_datetime 
            SET (start_datetime, end_datetime) = (:start_datetime, :end_datetime) 
            WHERE id='{exp_id}';
            """
        )
        self.query.bindValue(":start_datetime", start_dt)
        self.query.bindValue(":end_datetime", end_dt)
        self.query.exec_()

        return self.query.value(0) if self.query.first() else None

    def get_all_exp_datetime(self) -> Union[List[Dict], None]:
        self.query.exec_(
            """
            SELECT e.id as id, u.id as user_id, u.name as user_name, e.start_datetime, e.end_datetime
            FROM exp_datetime e inner join user u on u.id = e.user_id;
            """
        )
        result = []
        while self.query.next():
            result.append(self.print_exp_info_from_query())
        return result

    def get_exp_datetime(self, exp_id: int) -> Union[Dict, NameError]:
        self.query.exec_(
            f"""
            SELECT e.id as id, u.id as user_id, u.name as user_name, e.start_datetime, e.end_datetime
            FROM exp_datetime e inner join user u on u.id = e.user_id WHERE e.id='{exp_id}';
            """
        )
        return self.print_exp_info_from_query()

    def delete_all_exp_datetime(self):
        self.query.exec_("""DELETE FROM exp_datetime;""")

    def delete_exp_datetime_by_id(self, exp_id: int) -> Union[int, None]:
        self.query.exec_(f"""DELETE FROM exp_datetime WHERE id='{exp_id}';""")
        return self.query.value(0) if self.query.first() else None

    def delete_exp_datetime_by_user_id(self, user_id: int) -> Union[int, None]:
        self.query.exec_(
            f"""
            DELETE FROM exp_datetime WHERE user_id='{user_id}' AND EXISTS (SELECT * FROM user WHERE id='{user_id}');
            """
        )
        return self.query.value(0) if self.query.first() else None
