from typing import List, Tuple, Union

from domain.interface.user import UserRepository, UserData


class UserInMemoryRepository(UserRepository):
    # TODO: user object 생성, workmode object 생성
    def print_user_info_from_query(self):
        user_id, rank, name, status = \
            self.query.value(0), \
            self.query.value(1), \
            self.query.value(2), \
            self.query.value(3)

        return UserData((user_id, rank, name, status))

    def create_default_user_table(self):
        self.query.exec_(
            """
            CREATE TABLE if NOT EXISTS user (
                id INTEGER primary key autoincrement,
                rank VARCHAR (30) NOT NULL,
                name VARCHAR (30) NOT NULL,
                status VARCHAR (30) NOT NULL DEFAULT 'Default'
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

    def get_user_by_name(self, name: str) -> Union[UserData, NameError]:
        self.query.exec_(f"""SELECT * FROM user WHERE name='{name}';""")
        if not self.query.first():
            raise NameError(f'user whose name is {name} does not exist')

        return self.print_user_info_from_query()

    def set_user_name(self, user_id: int, name: str):
        self.query.exec_(f"""UPDATE user SET name='{name}' WHERE id='{user_id}';""")

    def get_users_by_rank(self, rank: str) -> Union[List[UserData], NameError]:
        self.query.exec_(f"""SELECT * FROM user WHERE rank='{rank}';""")
        if not self.query.first():
            raise NameError(f'user whose rank is {rank} does not exist')

        result = []
        while self.query.next():
            result.append(self.print_user_info_from_query())
        return result

    def set_user_rank(self, user_id: int, rank: str):
        self.query.exec_(f"""UPDATE user SET rank='{rank}' WHERE id='{user_id}';""")

    def get_users_by_status(self, status: str) -> Union[List[UserData], NameError]:
        self.query.exec_(f"""SELECT * FROM user WHERE status='{status}';""")
        if not self.query.first():
            raise NameError(f'user whose status is {status} does not exist')

        result = []
        while self.query.next():
            result.append(self.print_user_info_from_query())
        return result

    def set_user_status(self, user_id: int, status: str):
        self.query.exec_(f"""UPDATE user SET status='{status}' WHERE id='{user_id}';""")

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
