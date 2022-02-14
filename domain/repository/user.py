from typing import List, Tuple, Union, Dict

from PyQt5.QtSql import QSqlQuery
from domain.interface.user import UserRepository, UserData


class UserInMemoryRepository(UserRepository):
    def print_user_info_from_query(self):
        data = {
            "id": self.query.value(0),
            "rank": self.query.value(1),
            "name": self.query.value(2),
            "status": self.query.value(3),
            "weekday_work_count": self.query.value(4),
            "holiday_work_count": self.query.value(5)
        }
        return UserData(data)

    @staticmethod
    def exp_relation_record_from_query(_query: QSqlQuery):
        record = _query.record()
        data = {
            "exp_relation_id": record.indexOf("exp_relation_id"),
            "user_1_id": record.indexOf("user_1_id"),
            "user_1_name": record.indexOf("user_1_name"),
            "user_2_id": record.indexOf("user_2_id"),
            "user_2_name": record.indexOf("user_2_name")
        }

        return record, data

    def create_default_user_table(self):
        self.query.exec_(
            """
            CREATE TABLE if NOT EXISTS user (
                id INTEGER primary key autoincrement,
                rank VARCHAR (30) NOT NULL,
                name VARCHAR (30) NOT NULL,
                status VARCHAR (30) NOT NULL DEFAULT 'Default',
                weekday_work_count INTEGER DEFAULT 0 CHECK ( weekday_work_count >= 0 ),
                holiday_work_count INTEGER DEFAULT 0 CHECK ( holiday_work_count >= 0 ),
                work_mode VARCHAR (30) DEFAULT 'on' CHECK ( work_mode IN ('on', 'off'))
            )
            """
        )

    def get_all_users(self) -> Union[List[UserData], None]:
        self.query.exec_("SELECT * FROM user")
        if not self.query.first():
            return None

        result = []
        while self.query.next():
            result.append(self.print_user_info_from_query())
        return result

    def get_user_by_id(self, user_id: int) -> bool:
        self.query.exec_(f"""SELECT * FROM user WHERE id='{user_id}';""")
        if not self.query.first():
            raise NameError(f'user whose id is {id} does not exist')

        self.print_user_info_from_query()
        return True

    def get_user_by_name(self, name: str) -> Union[List[UserData], None]:
        self.query.prepare(f"""SELECT * FROM user WHERE name LIKE (:search_name);""")
        self.query.bindValue(":search_name", f'%{name}%')
        self.query.exec_()

        result = []
        while self.query.next():
            result.append(self.print_user_info_from_query())
        return result

    def get_users_by_rank(self, rank: str) -> Union[List[UserData], NameError]:
        self.query.exec_(f"""SELECT * FROM user WHERE rank='{rank}';""")
        if not self.query.first():
            raise NameError(f'user whose rank is {rank} does not exist')

        result = []
        while self.query.next():
            result.append(self.print_user_info_from_query())
        return result

    def get_users_by_status(self, status: str) -> Union[List[UserData], NameError]:
        self.query.exec_(f"""SELECT * FROM user WHERE status='{status}';""")
        if not self.query.first():
            raise NameError(f'user whose status is {status} does not exist')

        result = []
        while self.query.next():
            result.append(self.print_user_info_from_query())
        return result

    def insert_new_user(self, data: UserData) -> int:
        self.query.prepare(
            """
            INSERT INTO user(rank, name, status, weekday_work_count, holiday_work_count) 
            VALUES (:rank, :name, :status, :weekday_work_count, :holiday_work_count);
            """
        )
        self.query.bindValue(":rank", data["rank"])
        self.query.bindValue(":name", data["name"])
        self.query.bindValue(":status", data["status"])
        self.query.bindValue(":weekday_work_count", data["weekday_work_count"])
        self.query.bindValue(":holiday_work_count", data["holiday_work_count"])
        self.query.exec_()

        return self.query.lastInsertId()

    def insert_dummy_users(self, data: List[UserData]):
        user_id_list = []
        for user_data in data:
            user_id = self.insert_new_user(data=user_data)
            user_id_list.append(user_id)

        return user_id_list

    def delete_user(self, user_id: int):
        self.query.exec_(
            f"""
            DELETE FROM user WHERE id='{user_id}' AND EXISTS (SELECT * FROM user WHERE id='{user_id}');
            """
        )

    def delete_all_users(self):
        self.query.exec_("""DELETE FROM USER;""")

    def get_user_id(self, user_data: Dict) -> Union[int, ValueError]:
        self.query.prepare(
            f"""
            SELECT id FROM user 
            WHERE name=:name AND rank=:rank AND status=:status 
            AND weekday_work_count=:weekday_work_count
            AND holiday_work_count=:holiday_work_count;
            """
        )
        self.query.bindValue(":name", user_data['name'])
        self.query.bindValue(":rank", user_data['rank'])
        self.query.bindValue(":status", user_data['status'])
        self.query.bindValue(":weekday_work_count", user_data['weekday_work_count'])
        self.query.bindValue(":holiday_work_count", user_data['holiday_work_count'])
        self.query.exec_()

        if not self.query.first():
            raise ValueError(f'user does not exist')

        return self.query.value(0) or None

    def update_user(self, user_id: int, user_data: Dict):
        self.query.prepare(
            f"""
            UPDATE user
            SET (rank, name, status, weekday_work_count, holiday_work_count, work_mode)
            = (:rank, :name, :status, :weekday_work_count, :holiday_work_count, :work_mode)
            WHERE id='{user_id}';
            """
        )
        self.query.bindValue(":rank", user_data['rank'])
        self.query.bindValue(":name", user_data['name'])
        self.query.bindValue(":status", user_data['status'])
        self.query.bindValue(":weekday_work_count", int(user_data['weekday_work_count']))
        self.query.bindValue(":holiday_work_count", int(user_data['holiday_work_count']))
        self.query.bindValue(":work_mode", user_data['work_mode'])

        self.query.exec_()

    def update_user_work_count(self, user_id: int, mode: str, up: bool):
        col = f'{mode}_work_count'
        if up:
            self.query.exec_(f"""UPDATE user SET {col} = '{col}' + 1 WHERE id='{user_id}';""")
        else:
            self.query.exec_(f"""UPDATE user SET {col} = '{col}' - 1 WHERE id='{user_id}';""")

    def get_max_work_count(self):
        self.query.exec_(
            """
            SELECT MAX(weekday_work_count) as max_week_count, MAX(holiday_work_count) as max_holiday_count FROM user;
            """
        )
        if not self.query.first():
            raise NameError(f'error while selecting max(week_count) value from user table')

        work_count = {
            "weekday": self.query.value(0),
            "holiday": self.query.value(1)
        }
        return work_count

    def get_min_work_count(self):
        self.query.exec_(
            """
            SELECT MIN(weekday_work_count) as max_week_count, MIN(holiday_work_count) as max_holiday_count FROM user;
            """
        )
        if not self.query.first():
            raise NameError(f'error while selecting max(week_count) value from user table')

        work_count = {
            "weekday": self.query.value(0),
            "holiday": self.query.value(1)
        }
        return work_count

    def get_work_mode_users(self):
        self.query.exec_(
            """
            SELECT * FROM user WHERE work_mode = 'on';
            """
        )

        if not self.query.first():
            raise NameError(f'error while selecting users')

        result = []
        while self.query.next():
            result.append(self.print_user_info_from_query())
        return result

    def create_exp_relation_table(self):
        self.query.exec_(
            """
            CREATE TABLE if NOT EXISTS exp_relation (
                exp_relation_id INTEGER primary key autoincrement,
                user_1_id INTEGER,
                user_1_name VARCHAR (30) NOT NULL,
                user_2_id INTEGER,
                user_2_name VARCHAR (30) NOT NULL,
                foreign key (user_1_id, user_2_id) REFERENCES user(id, id) ON DELETE CASCADE
            )
            """
        )

    def get_all_exp_relation(self) -> Union[List[Dict], None]:
        self.query.exec_("""SELECT * FROM exp_relation;""")

        record, exp_query_dict = self.exp_relation_record_from_query(_query=self.query)
        result = []
        while self.query.next():
            item = {
                "exp_relation_id": self.query.value(exp_query_dict["exp_relation_id"]),
                "user_1_id": self.query.value(exp_query_dict["user_1_id"]),
                "user_1_name": self.query.value(exp_query_dict["user_1_name"]),
                "user_2_id": self.query.value(exp_query_dict["user_2_id"]),
                "user_2_name": self.query.value(exp_query_dict["user_2_name"])
            }
            result.append(item)

        return result

    def insert_exp_relation(self, user_1_id: int, user_1_name: str, user_2_id: int, user_2_name: str):
        self.query.prepare(
            """
            INSERT INTO exp_relation (user_1_id, user_1_name, user_2_id, user_2_name)
            VALUES (:user_1_id, :user_1_name, :user_2_id, :user_2_name);
            """
        )

        self.query.bindValue(":user_1_id", user_1_id)
        self.query.bindValue(":user_2_id", user_2_id)
        self.query.bindValue(":user_1_name", user_1_name)
        self.query.bindValue(":user_2_name", user_2_name)
        self.query.exec_()

    def delete_exp_relation(self, user_1_id: int, user_2_id: int):
        self.query.exec_(f"""DELETE FROM exp_relation WHERE user_1_id='{user_1_id}' AND user_2_id='{user_2_id}'""")
