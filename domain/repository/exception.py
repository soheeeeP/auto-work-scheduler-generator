from datetime import datetime
from typing import List, Dict, Union

from PyQt5.QtSql import QSqlQuery
from domain.interface.exception import DateTimeExceptionRepository, RelationExceptionRepository


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

    @staticmethod
    def renew_user_exp_datetime_timeline(q: QSqlQuery, start_dt: str, end_dt: str) -> List:
        today = datetime.today().strftime("%Y/%m/%d %H:%M")

        timeline = [{"start": start_dt, "end": end_dt}]
        while q.next():
            timeline.append({"start": q.value(0), "end": q.value(1)})
        timeline.sort(key=lambda x: (x["start"], x["end"]))

        new_timeline = [{"start": today, "end": today}]

        prev_start_dt, prev_end_dt = today, today
        for t in timeline:
            s_dt, e_dt = t["start"], t["end"]

            if prev_end_dt < s_dt:
                new_timeline.append({"start": s_dt, "end": e_dt})
                prev_start_dt, prev_end_dt = s_dt, e_dt
            elif s_dt <= prev_end_dt <= e_dt:
                new_timeline[-1]["end"] = e_dt
                prev_start_dt, prev_end_dt = new_timeline[-1]["start"], e_dt
            else:
                continue

        return new_timeline

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

    def insert_exp_datetime(self, user_id: int, start_dt: str, end_dt: str) -> Union[int, None]:
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

    def update_exp_datetime(self, exp_id: int, start_dt: str, end_dt: str) -> Union[int, None]:
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

    def update_exp_datetime_timeline_by_user_id(self, user_id: int, start_dt: str, end_dt: str) -> bool:
        self.query.exec_(f"""SELECT start_datetime as start, end_datetime as end FROM exp_datetime WHERE user_id='{user_id}';""")
        if self.query.first() is False:
            self.insert_exp_datetime(user_id=user_id, start_dt=start_dt, end_dt=end_dt)
            return True

        self.query.previous()
        new_timeline = self.renew_user_exp_datetime_timeline(q=self.query, start_dt=start_dt, end_dt=end_dt)

        self.delete_exp_datetime_by_user_id(user_id=user_id)
        self.query.exec_(
            f"""INSERT INTO exp_datetime (user_id, start_datetime, end_datetime) VALUES %s;"""
            % str([(user_id, x["start"], x["end"]) for x in new_timeline]).strip('[]')
        )
        return True

    def update_exp_datetime_timeline_all_user(self) -> bool:
        today = datetime.today().strftime("%Y/%m/%d %H:%M")

        self.query.exec_(f"""SELECT user_id FROM exp_datetime GROUP BY user_id;""")
        user_id_list = []
        while self.query.next():
            user_id_list.append(self.query.value(0))

        for user_id in user_id_list:
            self.update_exp_datetime_timeline_by_user_id(
                user_id=user_id,
                start_dt=today,
                end_dt=today
            )

        return True

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


class RelationExceptionInMemoryRepository(RelationExceptionRepository):
    @staticmethod
    def exp_relation_query_record(_query: QSqlQuery):
        record = _query.record()
        col_dict = {
            "id": record.indexOf("id"),
            "user1_id": record.indexOf("user1_id"),
            "user1_name": record.indexOf("user1_name"),
            "user2_id": record.indexOf("user2_id"),
            "user2_name": record.indexOf("user2_name")
        }

        return record, col_dict

    def print_from_query(self, col_idx: Dict) -> Dict:
        print(self.query.value(0))
        return {
            "id": self.query.value(col_idx["id"]),
            "user1_id": self.query.value(col_idx["user1_id"]),
            "user1_name": self.query.value(col_idx["user1_name"]),
            "user2_id": self.query.value(col_idx["user2_id"]),
            "user2_name": self.query.value(col_idx["user2_name"])
        }

    def create_exp_relation_table(self):
        self.query.exec_(
            """
            CREATE TABLE if NOT EXISTS exp_relation (
                id INTEGER primary key autoincrement,
                user1_id INTEGER,
                user2_id INTEGER,
                foreign key (user1_id) REFERENCES user(id) ON DELETE CASCADE,
                foreign key (user2_id) REFERENCES user(id) ON DELETE CASCADE
            )
            """
        )
        pass

    def insert_exp_relation_by_id(self, user1_id: int, user2_id) -> bool:
        exists = self.get_exp_relation_by_user_id_set(user1_id=user1_id, user2_id=user2_id)
        if exists:
            return False

        self.query.prepare(f"""INSERT INTO exp_relation (user1_id, user2_id) VALUES (:user1_id, :user2_id);""")
        self.query.bindValue(":user1_id", user1_id)
        self.query.bindValue(":user2_id", user2_id)

        result = self.query.exec_()

        return result

    def insert_exp_relation_by_name(self, user1_name: str, user2_name: str) -> bool:
        exists = self.get_exp_relation_by_user_name_set(user1_name=user1_name, user2_name=user2_name)
        if exists:
            return False

        result = self.query.exec_(
            f"""
            INSERT INTO exp_relation(user1_id, user2_id)
            SELECT u1.id, u2.id
            FROM user u1, user u2 WHERE u1.name='{user1_name}' AND u2.name='{user2_name}';
            """
        )
        return result

    def get_exp_relation_by_user_id_set(self, user1_id: int, user2_id: int) -> Union[Dict, None]:
        self.query.exec_(
            f"""
            SELECT e.id as id, e.user1_id as user1_id, u1.name as user1_name, e.user2_id as user2_id, u2.name as user2_name
            FROM exp_relation e
            INNER JOIN user u1 on u1.id = e.user1_id INNER JOIN user u2 on u2.id = e.user2_id
            WHERE u1.id='{user1_id}' AND u2.id='{user2_id}';
            """
        )
        if self.query.first() is False:
            return None

        record, value = self.exp_relation_query_record(_query=self.query)
        return self.print_from_query(col_idx=value)

    def get_exp_relation_by_user_name_set(self, user1_name: str, user2_name: str) -> Union[Dict, None]:
        self.query.exec_(
            f"""
            SELECT e.id as id, e.user1_id as user1_id, u1.name as user1_name, e.user2_id as user2_id, u2.name as user2_name
            FROM exp_relation e
            INNER JOIN user u1 on u1.id = e.user1_id INNER JOIN user u2 on u2.id = e.user2_id
            WHERE u1.name='{user1_name}' AND u2.name='{user2_name}';
            """
        )
        if self.query.first() is False:
            return None

        record, value = self.exp_relation_query_record(_query=self.query)
        return self.print_from_query(col_idx=value)

    def get_all_exp_relation(self) -> Union[List[Dict], None]:
        self.query.exec_(
            f"""
            SELECT e.id as id, e.user1_id as user1_id, u1.name as user1_name, e.user2_id as user2_id, u2.name as user2_name
            FROM exp_relation e
            INNER JOIN user u1 on u1.id = e.user1_id INNER JOIN user u2 on u2.id = e.user2_id;
            """
        )
        if self.query.first() is False:
            return None

        self.query.previous()

        record, value = self.exp_relation_query_record(_query=self.query)
        result = []
        while self.query.next():
            result.append(self.print_from_query(col_idx=value))
        return result

    def delete_exp_relation_by_user_id_set(self, user1_id: int, user2_id: int) -> bool:
        self.query.exec_(f"""DELETE FROM exp_relation WHERE user1_id='{user1_id}' AND user2_id='{user2_id}';""")

        del_rows_cnt = self.query.numRowsAffected()
        return False if del_rows_cnt == 0 else True

    def delete_exp_relation_by_user_name_set(self, user1_name: int, user2_name: set) -> bool:
        self.query.exec_(
            f"""
            DELETE FROM exp_relation
            WHERE user1_id IN (
                    SELECT user1_id
                    FROM exp_relation e INNER JOIN user u1 on u1.id = e.user1_id WHERE u1.name='{user1_name}'
                ) AND
                user2_id IN (
                    SELECT user2_id
                    FROM exp_relation e INNER JOIN user u2 on u2.id = e.user2_id WHERE u2.name='{user2_name}'
                );
            """
        )
        del_rows_cnt = self.query.numRowsAffected()
        return False if del_rows_cnt == 0 else True

    def delete_all_exp_relation(self) -> bool:
        self.query.exec_("""DELETE FROM exp_relation;""")

        del_rows_cnt = self.query.numRowsAffected()
        return False if del_rows_cnt == 0 else True
