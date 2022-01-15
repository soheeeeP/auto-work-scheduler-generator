from typing import List

from domain.interface.workmode import WorkModeRepository, WorkData


class WorkModeInMemoryRepository(WorkModeRepository):
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
            self.query.exec_(f"""ALTER TABLE workmode ADD weekday_{i+1} BIT DEFAULT 1;""")
            self.query.exec_(f"""ALTER TABLE workmode ADD holiday_{i+1} BIT DEFAULT 1;""")

    def drop_work_mode_table(self):
        self.query.exec_("""DROP TABLE workmode;""")

    def insert_user_work_mode(self, user_id: int, option: WorkData):
        keys = ('user_id', ) + tuple(key for key in option.keys())
        values = (user_id, ) + tuple(value for value in option.values())

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
