from typing import List, Union, Dict

from PyQt5.QtSql import QSqlQuery
from domain.interface.workmode import WorkModeRepository, WorkData


class WorkModeInMemoryRepository(WorkModeRepository):
    def query_record(self, _query: QSqlQuery):
        record = _query.record()

        return {
            "rank": _query.value(record.indexOf("rank")),
            "name": _query.value(record.indexOf("name")),
            "status": _query.value(record.indexOf("status")),
            "work_count": _query.value(record.indexOf("work_count")),
            f"weekday_{int}": _query.value(record.indexOf(f"weekday_{int}")),
            f"holiday_{int}": _query.value(record.indexOf(f"holiday_{int}")),
        }

    def create_work_mode_table(self, term_count: int):
        self.query.exec_(
            """
            CREATE TABLE if NOT EXISTS workmode (
                workmode_id INTEGER primary key autoincrement,
                user_id INTEGER,
                foreign key (user_id) REFERENCES user(id)
            )
            """
        )
        for i in range(term_count):
            self.query.exec_(f"""ALTER TABLE workmode ADD weekday_{i + 1} BIT DEFAULT 1;""")
            self.query.exec_(f"""ALTER TABLE workmode ADD holiday_{i + 1} BIT DEFAULT 1;""")

    def drop_work_mode_table(self):
        self.query.exec_("""DROP TABLE workmode;""")

    def insert_user_work_mode(self, user_id: int, option: WorkData):
        keys = ('user_id',) + tuple(key for key in option.keys())
        values = (user_id,) + tuple(value for value in option.values())

        self.query.prepare(f"""INSERT INTO workmode {keys} VALUES {values};""")
        self.query.exec_()

    def update_user_work_mode(self, option: WorkData):
        user_id = option['user_id']
        self.query.exec_(f"""SELECT * FROM workmode WHERE user_id='{user_id}';""")
        if not self.query.first():
            raise NameError(f'user whose id is {user_id} does not exist')

        for key, value in option['data'].items():
            self.query.exec_(f"""UPDATE workmode SET {key} = '{value}' WHERE user_id = '{user_id}';""")

    def update_users_list_work_mode(self, options: List[WorkData]):
        for o in options:
            self.update_user_work_mode(option=o)

    def get_all_users_work_mode_columns(self, term_count: int) -> Union[List[Dict], NameError]:
        self.query.exec_("""SELECT * FROM user u INNER JOIN workmode w on u.id = w.user_id;""")

        query_dict = self.query_record(_query=self.query)

        result = []
        while self.query.next():
            item = {
                "rank": query_dict["rank"],
                "name": query_dict["name"],
                "status": query_dict["status"],
                "work_count": query_dict["work_count"],
            }
            for i in range(1, term_count + 1):
                item[f"weekday_{i}"] = query_dict[f"weekday_{i}"]
                item[f"holiday_{i}"] = query_dict[f"holiday_{i}"]
            result.append(item)

        return result

    def get_user_work_mode_column(self, user_id: int, term_count: int) -> Union[Dict, NameError]:
        self.query.exec_(f"""SELECT * FROM user u INNER JOIN workmode w on u.id = w.user_id and u.id = '{user_id}';""")
        self.query.next()

        query_dict = self.query_record(_query=self.query)

        item = {
            "rank": query_dict["rank"],
            "name": query_dict["name"],
            "status": query_dict["status"],
            "work_count": query_dict["work_count"],
        }
        for i in range(1, term_count + 1):
            item[f"weekday_{i}"] = query_dict[f"weekday_{i}"]
            item[f"holiday_{i}"] = query_dict[f"holiday_{i}"]
        return item
