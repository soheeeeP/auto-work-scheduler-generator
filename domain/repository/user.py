from typing import List, Tuple, Union, Dict

from domain.interface.user import UserRepository, UserData


class UserInMemoryRepository(UserRepository):
    def print_user_info_from_query(self):
        user_id, rank, name, status, work_count = \
            self.query.value(0), \
            self.query.value(1), \
            self.query.value(2), \
            self.query.value(3), \
            self.query.value(4)

        return UserData((user_id, rank, name, status, work_count))

    def create_default_user_table(self):
        self.query.exec_(
            """
            CREATE TABLE if NOT EXISTS user (
                id INTEGER primary key autoincrement,
                rank VARCHAR (30) NOT NULL,
                name VARCHAR (30) NOT NULL,
                status VARCHAR (30) NOT NULL DEFAULT 'Default',
                work_count INTEGER DEFAULT 0 CHECK ( work_count >= 0 )
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

    def get_user_by_name(self, name: str) -> Union[UserData, NameError]:
        self.query.exec_(f"""SELECT * FROM user WHERE name='{name}';""")
        if not self.query.first():
            raise NameError(f'user whose name is {name} does not exist')

        return self.print_user_info_from_query()

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
            INSERT INTO user(rank, name, status) VALUES (:rank, :name, :status);
            """
        )
        self.query.bindValue(":rank", data[0])
        self.query.bindValue(":name", data[1])
        self.query.bindValue(":status", data[2])
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
            WHERE name=:name AND rank=:rank AND status=:status AND work_count=:work_count;
            """
        )
        self.query.bindValue(":name", user_data['name'])
        self.query.bindValue(":rank", user_data['rank'])
        self.query.bindValue(":status", user_data['status'])
        self.query.bindValue(":work_count", user_data['work_count'])
        self.query.exec_()

        if not self.query.first():
            raise ValueError(f'user does not exist')

        return self.query.value(0) or None

    def update_user(self, user_id: int, user_data: Dict):
        self.query.prepare(
            f"""
            UPDATE user SET (rank, name, status) = (:rank, :name, :status) WHERE id='{user_id}';
            """
        )
        self.query.bindValue(":rank", user_data['rank'])
        self.query.bindValue(":name", user_data['name'])
        self.query.bindValue(":status", user_data['status'])
        self.query.exec_()

    def update_user_work_count(self, user_id: int, mode: str):
        if mode == 'up':
            self.query.exec_(f"""UPDATE user SET work_count = work_count + 1 WHERE id='{user_id}';""")
        elif mode == 'down':
            self.query.exec_(f"""UPDATE user SET work_count = work_count - 1 WHERE id='{user_id}';""")
        else:
            raise ValueError(f'cannot update user_work_count: invalid mode {mode}')
